import os
import psycopg2
from datetime import datetime
from psycopg2.extras import RealDictCursor

# URL de conexão e dias grátis padrão
DATABASE_URL = os.getenv("DATABASE_URL")
DEFAULT_FREE_DAYS = 5


def conectar():
    """
    Retorna conexão ao PostgreSQL com autocommit.
    """
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn


def registrar_usuario(user_id: str, nome: str) -> None:
    """
    Insere novo usuário ou ignora se já existir.
    """
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
    """
    Retorna True se usuário ativo e dentro do período grátis.
    """
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
    """
    Marca o usuário como ativo.
    """
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE usuarios SET ativo = TRUE WHERE user_id = %s;",
            (user_id,)
        )
    conn.close()


def bloquear_usuario(user_id: str) -> None:
    """
    Marca o usuário como inativo.
    """
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE usuarios SET ativo = FALSE WHERE user_id = %s;",
            (user_id,)
        )
    conn.close()


def renovar_acesso(user_id: str, dias: int) -> None:
    """
    Renova o período: atualiza dias_restantes e reseta data_cadastro.
    """
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
    """
    Deleta o usuário e seu histórico de chat.
    """
    conn = conectar()
    with conn.cursor() as cur:
        # Remove acesso
        cur.execute(
            "DELETE FROM usuarios WHERE user_id = %s;",
            (user_id,)
        )
        # Limpa chat history
        cur.execute(
            "DELETE FROM chat WHERE user_id = %s;",
            (user_id,)
        )
    conn.close()


def limpar_usuarios() -> None:
    """
    Remove todos os usuários e históricos de chat.
    """
    conn = conectar()
    with conn.cursor() as cur:
        # Trunca ambas as tabelas para reset completo
        cur.execute("TRUNCATE TABLE usuarios, chat;")
    conn.close()
