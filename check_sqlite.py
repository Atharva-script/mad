
import sqlite3

def check_local_users():
    try:
        conn = sqlite3.connect('sql_app.db')
        cursor = conn.cursor()
        cursor.execute("SELECT phone, name FROM users;")
        users = cursor.fetchall()
        print(f"Local Users in SQLite: {users}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

check_local_users()
