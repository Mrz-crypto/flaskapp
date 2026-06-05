import logging
from functools import wraps
from flask import jsonify, request, abort, session, redirect, url_for
from app.database import get_connection

logger = logging.getLogger(__name__)

ALLOWED_STATUSES = ("pending", "shipped")
ALLOWED_ROLES = ("user", "admin")


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view


def _is_admin():
    return session.get("user_role") == "admin"


def get_all_users():
    conn = get_connection()
    if conn is None:
        return []
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, email, role, created_at FROM users ORDER BY name"
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_user_by_id(user_id):
    conn = get_connection()
    if conn is None:
        return None
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, email, role, created_at FROM users WHERE id = %s",
        (user_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def update_user(user_id, name, email, role):
    name = (name or "").strip()
    email = (email or "").strip().lower()
    role = (role or "").strip().lower()

    if not name or not email:
        logger.warning(f"Update user {user_id}: Missing name or email")
        return False, "Name and email are required."
    if role not in ALLOWED_ROLES:
        logger.warning(f"Update user {user_id}: Invalid role {role}")
        return False, "Role must be user or admin."
    if len(name) > 100:
        return False, "Name must be less than 100 characters."

    conn = get_connection()
    if conn is None:
        logger.error(f"Update user {user_id}: Database connection failed")
        return False, "Database connection failed."

    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        logger.warning(f"Update user: User {user_id} not found")
        return False, "User not found."

    cursor.execute("SELECT id FROM users WHERE email = %s AND id != %s", (email, user_id))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        logger.warning(f"Update user {user_id}: Email {email} already in use")
        return False, "Email is already used by another account."

    cursor.execute(
        "UPDATE users SET name = %s, email = %s, role = %s WHERE id = %s",
        (name, email, role, user_id),
    )
    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"User {user_id} updated: {name} ({role})")
    return True, get_user_by_id(user_id)


def get_orders_for_user(user_id):
    conn = get_connection()
    if conn is None:
        return []
    cursor = conn.cursor()
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
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_all_orders():
    conn = get_connection()
    if conn is None:
        return []
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT o.id, o.user_id, o.item, o.quantity, o.status, o.created_at,
               u.name AS user_name, u.email AS user_email
        FROM orders o
        JOIN users u ON u.id = o.user_id
        ORDER BY o.id DESC
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_order_by_id(order_id):
    conn = get_connection()
    if conn is None:
        return None
    cursor = conn.cursor()
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
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def create_order(user_id, item, quantity):
    item = (item or "").strip()
    if not item:
        logger.warning(f"Create order: Missing item name for user {user_id}")
        return False, "Item name is required."
    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        logger.warning(f"Create order: Invalid quantity {quantity} for user {user_id}")
        return False, "Quantity must be a number."
    if quantity < 1:
        return False, "Quantity must be at least 1."

    conn = get_connection()
    if conn is None:
        logger.error(f"Create order: Database connection failed for user {user_id}")
        return False, "Database connection failed."

    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        logger.warning(f"Create order: User {user_id} not found")
        return False, "User not found."

    cursor.execute(
        "INSERT INTO orders (user_id, item, quantity, status) VALUES (%s, %s, %s, %s)",
        (user_id, item, quantity, "pending"),
    )
    conn.commit()
    order_id = cursor.lastrowid
    cursor.close()
    conn.close()
    logger.info(f"Order {order_id} created for user {user_id}: {item} x {quantity}")
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
    cursor.execute("UPDATE orders SET status = %s WHERE id = %s", (status, order_id))
    conn.commit()
    cursor.close()
    conn.close()
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
    cursor.execute(
        "UPDATE orders SET item = %s, quantity = %s, status = %s WHERE id = %s",
        (item, quantity, status, order_id),
    )
    conn.commit()
    cursor.close()
    conn.close()
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
    item = payload.get("item")
    quantity = payload.get("quantity")
    user_id = session.get("user_id")
    if _is_admin() and payload.get("user_id"):
        user_id = payload.get("user_id")

    ok, result = create_order(user_id, item, quantity)
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
            order_id, payload["status"], actor_id, is_admin=is_admin
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


def delete_order(order_id):
    order = get_order_by_id(order_id)
    if order is None:
        logger.warning(f"Delete order: Order {order_id} not found")
        abort(404, description="Order not found")
    if not _is_admin() and order["user_id"] != session.get("user_id"):
        logger.warning(f"Delete order {order_id}: Unauthorized access by user {session.get('user_id')}")
        abort(403, description="Forbidden")

    conn = get_connection()
    if conn is None:
        logger.error(f"Delete order {order_id}: Database connection failed")
        abort(500, description="Database connection failed")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"Order {order_id} deleted")
    return jsonify({"deleted": order_id})

    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = %s WHERE id = %s", (status, order_id))
    conn.commit()
    cursor.close()
    conn.close()
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
    cursor.execute(
        "UPDATE orders SET item = %s, quantity = %s, status = %s WHERE id = %s",
        (item, quantity, status, order_id),
    )
    conn.commit()
    cursor.close()
    conn.close()
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
    item = payload.get("item")
    quantity = payload.get("quantity")
    user_id = session.get("user_id")
    if _is_admin() and payload.get("user_id"):
        user_id = payload.get("user_id")

    ok, result = create_order(user_id, item, quantity)
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
            order_id, payload["status"], actor_id, is_admin=is_admin
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
        logger.warning(f"Delete order: Order {order_id} not found")
        abort(404, description="Order not found")
    if not _is_admin() and order["user_id"] != session.get("user_id"):
        logger.warning(f"Delete order {order_id}: Unauthorized access by user {session.get('user_id')}")
        abort(403, description="Forbidden")

    conn = get_connection()
    if conn is None:
        logger.error(f"Delete order {order_id}: Database connection failed")
        abort(500, description="Database connection failed")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"Order {order_id} deleted")
    return jsonify({"deleted": order_id})
