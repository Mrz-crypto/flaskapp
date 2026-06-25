import logging

import pymysql  # type: ignore[import-untyped]
from werkzeug.security import generate_password_hash

import config

logger = logging.getLogger(__name__)


def get_connection():
    try:
        return pymysql.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE,
            cursorclass=pymysql.cursors.DictCursor,
        )
    except Exception:
        logger.exception("Database connection failed")
        return None


def create_tables():
    conn = get_connection()
    if conn is None:
        logger.error("Cannot create tables: no database connection")
        return

    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                item VARCHAR(100) NOT NULL,
                quantity INT NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        _ensure_admin_user(cursor)
        _ensure_sample_order(cursor)
        conn.commit()
        logger.info("Database initialization completed successfully")
    except Exception:
        conn.rollback()
        logger.exception("Error creating tables")
    finally:
        cursor.close()
        conn.close()


def _ensure_admin_user(cursor):
    cursor.execute("SELECT id FROM users WHERE email = %s", ("admin@blackeye.com",))
    if cursor.fetchone():
        return

    cursor.execute(
        """
        INSERT INTO users (name, email, password, role)
        VALUES (%s, %s, %s, %s)
        """,
        ("Admin", "admin@blackeye.com", generate_password_hash("admin123"), "admin"),
    )
    logger.info("Admin user created")


def _ensure_sample_order(cursor):
    cursor.execute("SELECT COUNT(*) AS cnt FROM orders")
    if cursor.fetchone()["cnt"] != 0:
        return

    cursor.execute("SELECT id FROM users WHERE role = 'user' ORDER BY id LIMIT 1")
    sample_user = cursor.fetchone()
    if not sample_user:
        return

    cursor.execute(
        """
        INSERT INTO orders (user_id, item, quantity, status)
        VALUES (%s, %s, %s, %s)
        """,
        (sample_user["id"], "Sample Widget", 2, "pending"),
    )
    logger.info("Sample order created")
