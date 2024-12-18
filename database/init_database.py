import sqlite3
import os
from sqlite3 import Error

def create_database_folder():
    if not os.path.exists('database'):
        os.makedirs('database')

def create_connection():
    try:
        create_database_folder()
        conn = sqlite3.connect('database/database.db')
        return conn
    except Error as e:
        print(f"Ошибка при подключении к базе данных: {e}")
    return None

def create_tables(conn):
    try:
        cursor = conn.cursor()
        # Создание таблицы users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # Создание таблицы tasks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status INTEGER CHECK(status IN (0, 1)) NOT NULL,
                priority INTEGER CHECK(priority BETWEEN 1 AND 10) NOT NULL,
                user_id INTEGER,
                date DATE NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        ''')

        # Создание таблицы plans
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE    
            );
        ''')

        conn.commit()
        print("Таблицы созданы успешно")
    except Error as e:
        print(f"Ошибка при создании таблиц: {e}")

# Подключаемся и создаем таблицы
conn = create_connection()
if conn:
    create_tables(conn)
    conn.close()
