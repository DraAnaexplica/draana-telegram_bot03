import os
import logging
import requests

logger = logging.getLogger("draana.telegram_utils")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

async def processar_mensagem(payload: dict) -> None:
    from app.chat_db import add_chat_message, get_chat_history, clear_chat_history
    from app.openrouter_utils import gerar_resposta_openrouter

    chat = payload.get("message", {}).get("chat", {})
    chat_id = chat.get("id")
    texto = payload.get("message", {}).get("text", "").strip()

    # Reset de histórico no comando /start
    if texto.lower() == "/start":
        clear_chat_history(str(chat_id))

    add_chat_message(str(chat_id), "user", texto)
    historico = get_chat_history(str(chat_id))
    resposta = gerar_resposta_openrouter(historico)
    await enviar_mensagem(chat_id, resposta)

async def enviar_mensagem(chat_id: str, texto: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto}
    logger.info(f"📤 Enviando mensagem - URL: {url}, payload: {payload}")
    try:
        resp = requests.post(url, json=payload, timeout=10)
        logger.info(f"📥 Telegram respondeu: {resp.status_code} - {resp.text}")
    except Exception as e:
        logger.error(f"❌ Erro ao enviar mensagem: {e}")