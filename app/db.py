import os
import psycopg2
from datetime import datetime
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")
DEFAULT_FREE_DAYS = 5

def conectar():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn

def registrar_usuario(user_id: str, nome: str) -> None:
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO usuarios
              (user_id, nome, ativo, data_cadastro, dias_restantes)
            VALUES (%s, %s, TRUE, NOW(), %s)
            ON CONFLICT (user_id) DO NOTHING;
            """,
            (user_id, nome, DEFAULT_FREE_DAYS)
        )
    conn.close()

def verificar_acesso(user_id: str) -> bool:
    conn = conectar()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT ativo, data_cadastro, dias_restantes
              FROM usuarios
             WHERE user_id = %s;
            """,
            (user_id,)
        )
        usuario = cur.fetchone()
    conn.close()

    if not usuario or not usuario['ativo']:
        return False

    dias_usados = (datetime.utcnow() - usuario['data_cadastro']).days
    return dias_usados < usuario['dias_restantes']

def ativar_usuario(user_id: str) -> None:
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE usuarios SET ativo = TRUE WHERE user_id = %s;",
            (user_id,)
        )
    conn.close()

def bloquear_usuario(user_id: str) -> None:
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE usuarios SET ativo = FALSE WHERE user_id = %s;",
            (user_id,)
        )
    conn.close()

def renovar_acesso(user_id: str, dias: int) -> None:
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE usuarios
               SET dias_restantes = %s,
                   data_cadastro   = NOW()
             WHERE user_id = %s;
            """,
            (dias, user_id)
        )
    conn.close()

def excluir_usuario(user_id: str) -> None:
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM usuarios WHERE user_id = %s;",
            (user_id,)
        )
    conn.close()

def limpar_usuarios() -> None:
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE usuarios;")
    conn.close()
