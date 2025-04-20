import psycopg2
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def conectar():
    return psycopg2.connect(DATABASE_URL)

def registrar_usuario(user_id, nome=None):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM usuarios WHERE user_id = %s", (user_id,))
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO usuarios (user_id, nome) VALUES (%s, %s)",
                (user_id, nome)
            )
            conn.commit()
    except Exception as e:
        print("Erro ao registrar usuário:", e)
    finally:
        cur.close()
        conn.close()

def verificar_acesso(user_id):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute("SELECT ativo, dias_restantes, data_cadastro FROM usuarios WHERE user_id = %s", (user_id,))
        resultado = cur.fetchone()
        if not resultado:
            return False  # Usuário não encontrado
        ativo, dias_restantes, data_cadastro = resultado
        if not ativo:
            return False
        dias_uso = (datetime.now() - data_cadastro).days
        return dias_uso < dias_restantes
    except Exception as e:
        print("Erro ao verificar acesso:", e)
        return False
    finally:
        cur.close()
        conn.close()

def bloquear_usuario(user_id):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE usuarios SET ativo = FALSE WHERE user_id = %s", (user_id,))
        conn.commit()
    except Exception as e:
        print("Erro ao bloquear usuário:", e)
    finally:
        cur.close()
        conn.close()

def ativar_usuario(user_id):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE usuarios SET ativo = TRUE WHERE user_id = %s", (user_id,))
        conn.commit()
    except Exception as e:
        print("Erro ao ativar usuário:", e)
    finally:
        cur.close()
        conn.close()

def renovar_acesso(user_id, dias):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE usuarios SET dias_restantes = %s WHERE user_id = %s", (dias, user_id))
        conn.commit()
    except Exception as e:
        print("Erro ao renovar acesso:", e)
    finally:
        cur.close()
        conn.close()
