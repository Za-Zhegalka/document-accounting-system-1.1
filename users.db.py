import sqlite3

# Подключение к базе данных
connection = sqlite3.connect("users.db")
cursor = connection.cursor()

create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
"""
cursor.execute(create_table_query)
connection.commit()

cursor.execute("SELECT COUNT(*) FROM users")
count = cursor.fetchone()[0]
if count == 0:
    initial_users = [
        ("Главный менеджер", "admin_password", "Администратор"),
        ("Специалист отделения", "operator_password", "Оператор"),
        ("Секретарь", "user_password", "Пользователь"),
        ("Заказчик", "guest_password", "Внешний пользователь")
    ]
    insert_query = """
        INSERT INTO users (username, password, role) VALUES (?, ?, ?)
    """
    cursor.executemany(insert_query, initial_users)
    connection.commit()

create_actions_table_query = """
    CREATE TABLE IF NOT EXISTS actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT,
        user TEXT,
        time TEXT
    )
"""
cursor.execute(create_actions_table_query)
connection.commit()

create_files_table_query = """
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        sender TEXT,
        time TEXT,
        status TEXT,
        is_downloaded INTEGER
    )
"""
cursor.execute(create_files_table_query)
connection.commit()