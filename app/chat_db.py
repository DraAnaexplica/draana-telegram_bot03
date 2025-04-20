import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def conectar():
    return psycopg2.connect(DATABASE_URL)

def add_chat_message(user_id, role, content):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO chat_history (user_id, role, content, timestamp) VALUES (%s, %s, %s, %s)",
            (user_id, role, content, datetime.now())
        )
        conn.commit()
    except Exception as e:
        print("Erro ao adicionar mensagem ao histórico:", e)
    finally:
        cur.close()
        conn.close()

def get_chat_history(user_id, limite=10):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT role, content FROM chat_history WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s",
            (user_id, limite)
        )
        resultados = cur.fetchall()
        return [{"role": r, "content": c} for r, c in reversed(resultados)]
    except Exception as e:
        print("Erro ao buscar histórico:", e)
        return []
    finally:
        cur.close()
        conn.close()
