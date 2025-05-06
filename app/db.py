from app.db import conectar


def add_chat_message(user_id: str, role: str, message: str) -> None:
    """
    Insere uma linha na tabela de chat para histórico de mensagens.
    """
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO chat (user_id, role, message, timestamp)
            VALUES (%s, %s, %s, NOW());
            """,
            (user_id, role, message)
        )
    conn.close()


def get_chat_history(user_id: str) -> list[dict]:
    """
    Retorna o histórico de chat do usuário como lista de dicts ordenada por timestamp.
    Cada dict tem chaves 'role' e 'content'.
    """
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT role, message
              FROM chat
             WHERE user_id = %s
             ORDER BY timestamp ASC;
            """,
            (user_id,)
        )
        rows = cur.fetchall()
    conn.close()
    # Transforma em lista de dicionários com role e content
    return [{"role": role, "content": message} for role, message in rows]


def clear_chat_history(user_id: str) -> None:
    """
    Apaga todo o histórico de chat do usuário.
    """
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM chat WHERE user_id = %s;",
            (user_id,)
        )
    conn.close()
