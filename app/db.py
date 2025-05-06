import os
import psycopg2
from datetime import datetime
from psycopg2.extras import RealDictCursor

# URL de conexão (usada por todas as funções)
DATABASE_URL = os.getenv("DATABASE_URL")

def conectar():
    """
    Retorna uma nova conexão ao PostgreSQL com autocommit ativado.
    Usada pelo painel (app/painel.py) para listar e alterar usuárias.
    """
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn

# Número de dias grátis padrão
DEFAULT_FREE_DAYS = 5

def registrar_usuario(user_id: str, nome: str) -> None:
    """Insere novo usuário com dias grátis padrão."""
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
    """Retorna True se estiver ativo e dentro do período grátis."""
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

    data_cad = usuario['data_cadastro']
    dias_permitidos = usuario['dias_restantes']
    dias_usados = (datetime.utcnow() - data_cad).days

    return dias_usados < dias_permitidos

def ativar_usuario(user_id: str) -> None:
    """Marca o usuário como ativo (sem alterar datas)."""
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE usuarios
               SET ativo = TRUE
             WHERE user_id = %s;
            """,
            (user_id,)
        )
    conn.close()

def bloquear_usuario(user_id: str) -> None:
    """Marca o usuário como inativo."""
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE usuarios
               SET ativo = FALSE
             WHERE user_id = %s;
            """,
            (user_id,)
        )
    conn.close()

def renovar_acesso(user_id: str, dias: int) -> None:
    """
    Renova o período: atualiza dias_restantes e reseta data_cadastro
    para NOW(), garantindo que o novo ciclo comece na data da renovação.
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
