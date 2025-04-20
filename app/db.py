import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def conectar():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def add_chat_message(user_id, role, content):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_history (user_id, role, content, timestamp) VALUES (%s, %s, %s, %s)",
        (user_id, role, content, datetime.now())
    )
    conn.commit()
    cur.close()
    conn.close()

def get_chat_history(user_id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        "SELECT role, content FROM chat_history WHERE user_id = %s ORDER BY timestamp ASC",
        (user_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_all_users():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT user_id FROM chat_history")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users
