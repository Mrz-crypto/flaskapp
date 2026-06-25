import logging

from flask import abort, jsonify, request, session

from app.auth import login_required
from app.database import get_connection

logger = logging.getLogger(__name__)

ALLOWED_STATUSES = ("pending", "shipped")
ALLOWED_ROLES = ("user", "admin")


def _is_admin():
    return session.get("user_role") == "admin"


def _close(cursor=None, conn=None):
    if cursor is not None:
        cursor.close()
    if conn is not None:
        conn.close()


def get_all_users():
    conn = get_connection()
    if conn is None:
        return []

    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, name, email, role, created_at FROM users ORDER BY name"
        )
        return cursor.fetchall()
    finally:
        _close(cursor, conn)


def get_user_by_id(user_id):
    conn = get_connection()
    if conn is None:
        return None

    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, name, email, role, created_at FROM users WHERE id = %s",
            (user_id,),
        )
        return cursor.fetchone()
    finally:
        _close(cursor, conn)


def update_user(user_id, name, email, role):
    name = (name or "").strip()
    email = (email or "").strip().lower()
    role = (role or "").strip().lower()

    if not name or not email:
        logger.warning("Update user %s: missing name or email", user_id)
        return False, "Name and email are required."
    if role not in ALLOWED_ROLES:
        logger.warning("Update user %s: invalid role %s", user_id, role)
        return False, "Role must be user or admin."
    if len(name) > 100:
        return False, "Name must be less than 100 characters."

    conn = get_connection()
    if conn is None:
        logger.error("Update user %s: database connection failed", user_id)
        return False, "Database connection failed."

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            logger.warning("Update user: user %s not found", user_id)
            return False, "User not found."

        cursor.execute(
            "SELECT id FROM users WHERE email = %s AND id != %s",
            (email, user_id),
        )
        if cursor.fetchone():
            logger.warning("Update user %s: email already in use", user_id)
            return False, "Email is already used by another account."

        cursor.execute(
            "UPDATE users SET name = %s, email = %s, role = %s WHERE id = %s",
            (name, email, role, user_id),
        )
        conn.commit()
    finally:
        _close(cursor, conn)

    logger.info("User %s updated: %s (%s)", user_id, name, role)
    return True, get_user_by_id(user_id)


def get_orders_for_user(user_id):
    conn = get_connection()
    if conn is None:
        return []

    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT o.id, o.user_id, o.item, o.quantity, o.status, o.created_at,
                   u.name AS user_name, u.email AS user_email
            FROM orders o
            JOIN users u ON u.id = o.user_id
            WHERE o.user_id = %s
            ORDER BY o.id DESC
            """,
            (user_id,),
        )
        return cursor.fetchall()
    finally:
        _close(cursor, conn)


def get_all_orders():
    conn = get_connection()
    if conn is None:
        return []

    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT o.id, o.user_id, o.item, o.quantity, o.status, o.created_at,
                   u.name AS user_name, u.email AS user_email
            FROM orders o
            JOIN users u ON u.id = o.user_id
            ORDER BY o.id DESC
            """
        )
        return cursor.fetchall()
    finally:
        _close(cursor, conn)


def get_order_by_id(order_id):
    conn = get_connection()
    if conn is None:
        return None

    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT o.id, o.user_id, o.item, o.quantity, o.status, o.created_at,
                   u.name AS user_name, u.email AS user_email
            FROM orders o
            JOIN users u ON u.id = o.user_id
            WHERE o.id = %s
            """,
            (order_id,),
        )
        return cursor.fetchone()
    finally:
        _close(cursor, conn)


def create_order(user_id, item, quantity):
    item = (item or "").strip()
    if not item:
        logger.warning("Create order: missing item name for user %s", user_id)
        return False, "Item name is required."

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        logger.warning("Create order: invalid quantity for user %s", user_id)
        return False, "Quantity must be a number."

    if quantity < 1:
        return False, "Quantity must be at least 1."

    conn = get_connection()
    if conn is None:
        logger.error("Create order: database connection failed for user %s", user_id)
        return False, "Database connection failed."

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            logger.warning("Create order: user %s not found", user_id)
            return False, "User not found."

        cursor.execute(
            """
            INSERT INTO orders (user_id, item, quantity, status)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, item, quantity, "pending"),
        )
        conn.commit()
        order_id = cursor.lastrowid
    finally:
        _close(cursor, conn)

    logger.info("Order %s created for user %s", order_id, user_id)
    return True, get_order_by_id(order_id)


def update_order_status(order_id, status, actor_id, is_admin=False):
    status = (status or "").strip().lower()
    if status not in ALLOWED_STATUSES:
        return False, "Status must be pending or shipped."

    order = get_order_by_id(order_id)
    if order is None:
        return False, "Order not found."
    if not is_admin and order["user_id"] != actor_id:
        return False, "You can only update your own orders."

    conn = get_connection()
    if conn is None:
        return False, "Database connection failed."

    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE orders SET status = %s WHERE id = %s", (status, order_id)
        )
        conn.commit()
    finally:
        _close(cursor, conn)

    return True, get_order_by_id(order_id)


def update_order_details(order_id, item, quantity, status, actor_id, is_admin=False):
    order = get_order_by_id(order_id)
    if order is None:
        return False, "Order not found."
    if not is_admin and order["user_id"] != actor_id:
        return False, "You can only update your own orders."

    item = (item or "").strip()
    if not item:
        return False, "Item name is required."

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return False, "Quantity must be a number."

    if quantity < 1:
        return False, "Quantity must be at least 1."

    status = (status or "").strip().lower()
    if status not in ALLOWED_STATUSES:
        return False, "Status must be pending or shipped."

    conn = get_connection()
    if conn is None:
        return False, "Database connection failed."

    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE orders SET item = %s, quantity = %s, status = %s WHERE id = %s",
            (item, quantity, status, order_id),
        )
        conn.commit()
    finally:
        _close(cursor, conn)

    return True, get_order_by_id(order_id)


def _orders_for_session():
    user_id = session.get("user_id")
    if _is_admin():
        return get_all_orders()
    return get_orders_for_user(user_id)


@login_required
def list_orders():
    return jsonify(_orders_for_session())


@login_required
def get_order(order_id):
    order = get_order_by_id(order_id)
    if order is None:
        abort(404, description="Order not found")
    if not _is_admin() and order["user_id"] != session.get("user_id"):
        abort(403, description="Forbidden")
    return jsonify(order)


@login_required
def create_order_api():
    payload = request.get_json(silent=True) or {}
    user_id = session.get("user_id")
    if _is_admin() and payload.get("user_id"):
        user_id = payload.get("user_id")

    ok, result = create_order(user_id, payload.get("item"), payload.get("quantity"))
    if not ok:
        abort(400, description=result)
    return jsonify(result), 201


@login_required
def update_order(order_id):
    order = get_order_by_id(order_id)
    if order is None:
        abort(404, description="Order not found")

    is_admin = _is_admin()
    actor_id = session.get("user_id")
    if not is_admin and order["user_id"] != actor_id:
        abort(403, description="Forbidden")

    payload = request.get_json(silent=True) or {}
    if payload.get("status") is not None and len(payload) == 1:
        ok, result = update_order_status(
            order_id,
            payload["status"],
            actor_id,
            is_admin=is_admin,
        )
    else:
        ok, result = update_order_details(
            order_id,
            payload.get("item", order["item"]),
            payload.get("quantity", order["quantity"]),
            payload.get("status", order["status"]),
            actor_id,
            is_admin=is_admin,
        )
    if not ok:
        abort(400, description=result)
    return jsonify(result)


@login_required
def delete_order(order_id):
    order = get_order_by_id(order_id)
    if order is None:
        logger.warning("Delete order: order %s not found", order_id)
        abort(404, description="Order not found")
    if not _is_admin() and order["user_id"] != session.get("user_id"):
        logger.warning(
            "Delete order %s: unauthorized access by user %s",
            order_id,
            session.get("user_id"),
        )
        abort(403, description="Forbidden")

    conn = get_connection()
    if conn is None:
        logger.error("Delete order %s: database connection failed", order_id)
        abort(500, description="Database connection failed")

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
        conn.commit()
    finally:
        _close(cursor, conn)

    logger.info("Order %s deleted", order_id)
    return jsonify({"deleted": order_id})
