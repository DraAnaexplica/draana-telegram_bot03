import os
import psycopg2
from datetime import datetime
from psycopg2.extras import RealDictCursor

# Conexão
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True

# Número de dias grátis padrão
DEFAULT_FREE_DAYS = 5

def registrar_usuario(user_id: str, nome: str) -> None:
    """Insere novo usuário com dias grátis padrão."""
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

def verificar_acesso(user_id: str) -> bool:
    """Retorna True se estiver ativo e dentro do período grátis."""
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
        if not usuario or not usuario['ativo']:
            return False

        # Calcula dias já usados
        data_cad = usuario['data_cadastro']
        dias_permitidos = usuario['dias_restantes']
        dias_usados = (datetime.utcnow() - data_cad).days

        return dias_usados < dias_permitidos

def ativar_usuario(user_id: str) -> None:
    """Marca o usuário como ativo (sem alterar datas)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE usuarios
               SET ativo = TRUE
             WHERE user_id = %s;
            """,
            (user_id,)
        )

def bloquear_usuario(user_id: str) -> None:
    """Marca o usuário como inativo."""
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE usuarios
               SET ativo = FALSE
             WHERE user_id = %s;
            """,
            (user_id,)
        )

def renovar_acesso(user_id: str, dias: int) -> None:
    """
    Renova o período: atualiza dias_restantes E reseta data_cadastro
    para NOW(), garantindo que o ciclo de expiração comece do dia da renovação.
    """
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
