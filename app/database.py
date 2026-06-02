import pymysql  # type: ignore[import-untyped]
import config


def get_connection():
    try:
        conn = pymysql.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE,
            cursorclass=pymysql.cursors.DictCursor,
        )
        print("Database connected successfully!")
        return conn
    except Exception as e:
        print("Database connection failed:")
        print(e)
        return None


def create_tables():
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()

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

    cursor.execute("SELECT * FROM users WHERE email = %s", ("admin@admin.com",))
    admin = cursor.fetchone()
    if not admin:
        from werkzeug.security import generate_password_hash

        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            ("Admin", "admin@admin.com", generate_password_hash("admin123"), "admin"),
        )
        conn.commit()
        cursor.execute("SELECT id FROM users WHERE email = %s", ("admin@admin.com",))
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
    cursor.close()
    conn.close()
