import logging

import pymysql  # type: ignore[import-untyped]

import config

logger = logging.getLogger(__name__)


def get_connection():
    try:
        conn = pymysql.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE,
            cursorclass=pymysql.cursors.DictCursor,
        )
        logger.info("Database connected successfully!")
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None


def create_tables():
    conn = get_connection()
    if conn is None:
        logger.error("Cannot create tables: No database connection")
        return
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("Users table created/verified")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                item VARCHAR(100) NOT NULL,
                quantity INT NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        logger.info("Orders table created/verified")

        cursor.execute("SELECT * FROM users WHERE email = %s", ("admin@blackeye.com",))
        admin = cursor.fetchone()
        if not admin:
            from werkzeug.security import generate_password_hash

            cursor.execute(
                """
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    "Admin",
                    "admin@blackeye.com",
                    generate_password_hash("admin123"),
                    "admin",
                ),
            )
            conn.commit()
            logger.info("Admin user created")
            cursor.execute(
                "SELECT id FROM users WHERE email = %s",
                ("admin@blackeye.com",),
            )
            admin = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) AS cnt FROM orders")
        if cursor.fetchone()["cnt"] == 0:
            cursor.execute(
                "SELECT id FROM users WHERE role = 'user' ORDER BY id LIMIT 1"
            )
            sample_user = cursor.fetchone()
            if sample_user:
                cursor.execute(
                    "INSERT INTO orders (user_id, item, quantity, status) VALUES (%s, %s, %s, %s)",
                    (sample_user["id"], "Sample Widget", 2, "pending"),
                )
                conn.commit()
                logger.info("Sample order created")

        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
    finally:
        cursor.close()
        conn.close()
