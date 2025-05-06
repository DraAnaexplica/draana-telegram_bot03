from app.db import conectar

def add_chat_message(user_id: str, role: str, message: str) -> None:
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO chat(user_id, role, message, timestamp) VALUES (%s, %s, %s, NOW());",
            (user_id, role, message)
        )
    conn.close()

def get_chat_history(user_id: str) -> list[dict]:
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT role, message FROM chat WHERE user_id = %s ORDER BY timestamp ASC;",
            (user_id,)
        )
        rows = cur.fetchall()
    conn.close()
    return [{"role": r, "content": m} for r, m in rows]

def clear_chat_history(user_id: str) -> None:
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM chat WHERE user_id = %s;", (user_id,))
    conn.close()