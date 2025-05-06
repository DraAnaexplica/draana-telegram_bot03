import os
import logging
import requests

# Configuração de logs para este módulo
tp_logger = logging.getLogger("draana.telegram_utils")

# Token do bot obtido das variáveis de ambiente
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

async def processar_mensagem(payload: dict) -> None:
    """
    Recebe o payload do Telegram, gera resposta via OpenRouter e envia de volta.
    """
    from app.db import add_chat_message, get_chat_history
    from app.openrouter_utils import gerar_resposta_openrouter

    # Extrai chat_id e texto
    chat_id = payload["message"]["chat"]["id"]
    texto_usuario = payload["message"]["text"]
    tp_logger.info(f"📝 processar_mensagem - chat_id={chat_id}, texto='{texto_usuario}'")

    # Salva mensagem do usuário
    add_chat_message(str(chat_id), "user", texto_usuario)

    # Recupera histórico e gera resposta
    mensagens = get_chat_history(str(chat_id))
    resposta_ia = gerar_resposta_openrouter(mensagens)
    tp_logger.info(f"🤖 Resposta do modelo: '{resposta_ia}'")

    # Envia resposta final ao Telegram
    await enviar_mensagem(chat_id, resposta_ia)

async def enviar_mensagem(chat_id: str, texto: str) -> None:
    """
    Envia uma mensagem ao chat especificado via API do Telegram, com logs de requisição e resposta.
    """
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto
    }
    tp_logger.info(f"📤 Enviando mensagem - URL: {url}, payload: {payload}")
    try:
        resp = requests.post(url, json=payload, timeout=10)
        tp_logger.info(f"📥 Telegram respondeu: {resp.status_code} - {resp.text}")
    except Exception as e:
        tp_logger.error(f"❌ Erro ao chamar sendMessage: {e}")
