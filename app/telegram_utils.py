import os
import logging
import requests

# Configuração de logs para este módulo
logger = logging.getLogger("draana.telegram_utils")

# Base da URL da API do Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

async def processar_mensagem(payload: dict) -> None:
    """
    Processa o payload do Telegram: salva histórico, gera resposta via OpenRouter e envia ao usuário.
    """
    # Importa funções de histórico de chat
    from app.chat_db import add_chat_message, get_chat_history
    from app.openrouter_utils import gerar_resposta_openrouter

    # Extrai chat_id e texto do usuário
    chat_id = payload["message"]["chat"]["id"]
    texto_usuario = payload["message"]["text"]
    logger.info(f"📝 processar_mensagem - chat_id={chat_id}, texto='{texto_usuario}'")

    # Salva mensagem do usuário no banco
    add_chat_message(str(chat_id), "user", texto_usuario)

    # Recupera histórico e obtém resposta da IA
    mensagens = get_chat_history(str(chat_id))
    resposta_ia = gerar_resposta_openrouter(mensagens)
    logger.info(f"🤖 Resposta do modelo: '{resposta_ia}'")

    # Envia resposta final ao Telegram
    await enviar_mensagem(chat_id, resposta_ia)

async def enviar_mensagem(chat_id: str, texto: str) -> None:
    """
    Envia uma mensagem ao Telegram via endpoint sendMessage, com logs de requisição e resposta.
    """
    url = f"{BASE_URL}/sendMessage"
    body = {
        "chat_id": chat_id,
        "text": texto
    }
    logger.info(f"📤 Enviando mensagem - URL: {url}, payload: {body}")
    try:
        resp = requests.post(url, json=body, timeout=10)
        logger.info(f"📥 Telegram respondeu: {resp.status_code} - {resp.text}")
    except Exception as e:
        logger.error(f"❌ Erro ao chamar sendMessage: {e}")
