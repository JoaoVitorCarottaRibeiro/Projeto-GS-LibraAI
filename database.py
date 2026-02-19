import sqlite3

DB_NAME = "users.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            idade INTEGER NOT NULL,
            profissao TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            foto_perfil TEXT
        )
    """)

    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            module_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            UNIQUE(user_id, module_id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_points (
            user_id INTEGER PRIMARY KEY,
            points INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users WHERE email = ?
    """, (email,))

    user = cursor.fetchone()
    conn.close()
    return user

def get_user_progress(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT module_id, status
        FROM user_progress
        WHERE user_id = ?
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return {row["module_id"]: row["status"] for row in rows}


def set_module_completed(user_id, module_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO user_progress (user_id, module_id, status)
        VALUES (?, ?, 'completed')
        ON CONFLICT(user_id, module_id)
        DO UPDATE SET status = 'completed'
    """, (user_id, module_id))

    conn.commit()
    conn.close()


def get_module_status(user_id, module_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT status FROM user_progress
        WHERE user_id = ? AND module_id = ?
    """, (user_id, module_id))

    row = cursor.fetchone()
    conn.close()

    return row["status"] if row else None


def init_user_points(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO user_points (user_id, points)
        VALUES (?, 0)
    """, (user_id,))

    conn.commit()
    conn.close()


def add_points(user_id, points):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO user_points (user_id, points)
        VALUES (?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET points = points + excluded.points
    """, (user_id, points))

    conn.commit()
    conn.close()



def get_user_points(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT points FROM user_points
        WHERE user_id = ?
    """, (user_id,))

    row = cursor.fetchone()
    conn.close()

    return row["points"] if row else 0


def get_top_10_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.nome, up.points
        FROM user_points up
        JOIN users u ON u.id = up.user_id
        ORDER BY up.points DESC
        LIMIT 10
    """)

    result = cursor.fetchall()
    conn.close()
    return result

def update_module_progress(user_id, module_id, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO user_progress (user_id, module_id, status)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, module_id)
        DO UPDATE SET status = excluded.status
    """, (user_id, module_id, status))

    conn.commit()
    conn.close()

def add_points_to_user(user_id, points):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO user_points (user_id, points)
        VALUES (?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET points = points + excluded.points
    """, (user_id, points))

    conn.commit()
    conn.close()

def get_top_3_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.nome, up.points
        FROM user_points up
        JOIN users u ON u.id = up.user_id
        ORDER BY up.points DESC
        LIMIT 3
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows

