import logging
from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import get_connection
from app.auth import login_required
from app.controllers.ordercontroller import (
    get_all_orders,
    get_all_users,
    get_orders_for_user,
    create_order,
    update_order_status,
    update_order_details,
    update_user,
)

logger = logging.getLogger(__name__)


def home():
    if session.get("user_id"):
        return redirect(url_for("auth.dashboard"))
    return redirect(url_for("auth.login"))


def login():
    if session.get("user_id"):
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
            logger.warning("Login attempt with missing email or password")
            return render_template("login.html")

        conn = get_connection()
        if conn is None:
            flash("Database connection failed. Try again later.", "error")
            logger.error("Login failed: Database connection error")
            return render_template("login.html")

        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, password, role FROM users WHERE email = %s",
            (email,),
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_role"] = user["role"]
            flash("Login successful.", "success")
            logger.info("User logged in: %s (ID: %s)", email, user["id"])
            return redirect(url_for("auth.dashboard"))

        logger.warning("Failed login attempt for email: %s", email)
        flash("Invalid email or password.", "error")

    return render_template("login.html")


def register():
    if session.get("user_id"):
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.", "error")
            logger.warning("Registration attempt with missing fields")
            return render_template("register.html")

        if len(name) > 100:
            flash("Name must be less than 100 characters.", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            logger.warning("Registration attempt with weak password for: %s", email)
            return render_template("register.html")

        conn = get_connection()
        if conn is None:
            flash("Database connection failed. Try again later.", "error")
            logger.error("Registration failed: Database connection error")
            return render_template("register.html")

        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash("Email already registered.", "error")
            cursor.close()
            conn.close()
            logger.warning("Registration attempt with existing email: %s", email)
            return render_template("register.html")

        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed_password),
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Registration successful. Please log in.", "success")
        logger.info("New user registered: %s", email)
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@login_required
def dashboard():
    user_id = session.get("user_id")
    is_admin = session.get("user_role") == "admin"

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "update_status":
            order_id = request.form.get("order_id", type=int)
            status = request.form.get("status", "")
            ok, result = update_order_status(
                order_id, status, user_id, is_admin=is_admin
            )
            if ok:
                flash(f"Order #{order_id} marked as {result['status']}.", "success")
            else:
                flash(result, "error")
            return redirect(url_for("auth.dashboard"))

        if action == "update_order":
            order_id = request.form.get("order_id", type=int)
            ok, result = update_order_details(
                order_id,
                request.form.get("item"),
                request.form.get("quantity"),
                request.form.get("status"),
                user_id,
                is_admin=is_admin,
            )
            if ok:
                flash(f"Order #{order_id} updated.", "success")
            else:
                flash(result, "error")
            return redirect(url_for("auth.dashboard"))

        if action == "add_order":
            target_user_id = user_id
            if is_admin:
                target_user_id = request.form.get("user_id", type=int) or user_id
            ok, result = create_order(
                target_user_id,
                request.form.get("item"),
                request.form.get("quantity"),
            )
            if ok:
                flash("Order added.", "success")
            else:
                flash(result, "error")
            return redirect(url_for("auth.dashboard"))

        if action == "update_user" and is_admin:
            edit_user_id = request.form.get("user_id", type=int)
            ok, result = update_user(
                edit_user_id,
                request.form.get("name"),
                request.form.get("email"),
                request.form.get("role"),
            )
            if ok:
                if edit_user_id == user_id:
                    session["user_name"] = result["name"]
                    session["user_role"] = result["role"]
                flash(f"User #{edit_user_id} updated.", "success")
            else:
                flash(result, "error")
            return redirect(url_for("auth.dashboard"))

    orders = get_all_orders() if is_admin else get_orders_for_user(user_id)
    users = get_all_users() if is_admin else []

    return render_template(
        "dashboard.html",
        user_name=session.get("user_name"),
        user_role=session.get("user_role"),
        orders=orders,
        users=users,
        is_admin=is_admin,
    )


def logout():
    user_name = session.get("user_name", "Unknown")
    session.clear()
    flash("You have been logged out.", "success")
    logger.info("User logged out: %s", user_name)
    return redirect(url_for("auth.login"))
