import os
import psycopg2
from datetime import datetime
from psycopg2.extras import RealDictCursor

# Configurações do banco e uso gratuito padrão
DATABASE_URL = os.getenv("DATABASE_URL")
DEFAULT_FREE_DAYS = 5


def conectar():
    """
    Cria e retorna conexão ao PostgreSQL com autocommit.
    """
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn


def registrar_usuario(user_id: str, nome: str) -> None:
    """
    Registra usuário com dias gratuitos iniciais, se não existir.
    """
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO usuarios(user_id, nome, ativo, data_cadastro, dias_restantes)
            VALUES (%s, %s, TRUE, NOW(), %s)
            ON CONFLICT(user_id) DO NOTHING;
            """,
            (user_id, nome, DEFAULT_FREE_DAYS)
        )
    conn.close()


def verificar_acesso(user_id: str) -> bool:
    """
    Verifica se usuário está ativo e dentro do período gratuito.
    """
    conn = conectar()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT ativo, data_cadastro, dias_restantes FROM usuarios WHERE user_id = %s;",
            (user_id,)
        )
        usuario = cur.fetchone()
    conn.close()

    if not usuario or not usuario['ativo']:
        return False
    dias_usados = (datetime.utcnow() - usuario['data_cadastro']).days
    return dias_usados < usuario['dias_restantes']


def get_all_users() -> list[dict]:
    """
    Retorna todos os usuários com campos: user_id, nome, ativo.
    """
    conn = conectar()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT user_id, nome, ativo FROM usuarios ORDER BY data_cadastro DESC;")
        rows = cur.fetchall()
    conn.close()
    return rows


def ativar_usuario(user_id: str) -> None:
    """
    Marca usuário como ativo.
    """
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute("UPDATE usuarios SET ativo = TRUE WHERE user_id = %s;", (user_id,))
    conn.close()


def bloquear_usuario(user_id: str) -> None:
    """
    Marca usuário como inativo.
    """
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute("UPDATE usuarios SET ativo = FALSE WHERE user_id = %s;", (user_id,))
    conn.close()


def renovar_acesso(user_id: str, dias: int) -> None:
    """
    Renova período gratuito: reseta data_cadastro e define novos dias_restantes.
    """
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE usuarios
               SET data_cadastro = NOW(),
                   dias_restantes = %s
             WHERE user_id = %s;
            """,
            (dias, user_id)
        )
    conn.close()


def excluir_usuario(user_id: str) -> None:
    """
    Remove usuário e todo o histórico de chat.
    """
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM usuarios WHERE user_id = %s;", (user_id,))
        cur.execute("DELETE FROM chat WHERE user_id = %s;", (user_id,))
    conn.close()


def limpar_usuarios() -> None:
    """
    Trunca tabelas de usuários e chat, reset completo.
    """
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE usuarios, chat;")
    conn.close()
