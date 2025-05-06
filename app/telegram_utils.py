import os
import logging
import requests

# Logger para este módulo
tp_logger = logging.getLogger("draana.telegram_utils")

# Obtém o token do bot e remove espaços/newlines extras
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

async def processar_mensagem(payload: dict) -> None:
    """
    Processa o payload do Telegram: armazena no histórico, gera resposta via OpenRouter e envia de volta.
    """
    from app.chat_db import add_chat_message, get_chat_history
    from app.openrouter_utils import gerar_resposta_openrouter

    # Extrai informações do usuário
    message = payload.get("message", {})
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    texto_usuario = message.get("text", "")
    tp_logger.info(f"📝 processar_mensagem - chat_id={chat_id}, texto='{texto_usuario}'")

    # Salva mensagem do usuário
    add_chat_message(str(chat_id), "user", texto_usuario)

    # Recupera histórico e obtém resposta da IA
    historico = get_chat_history(str(chat_id))
    resposta_ia = gerar_resposta_openrouter(historico)
    tp_logger.info(f"🤖 Resposta do modelo: '{resposta_ia}'")

    # Envia resposta para o usuário
    await enviar_mensagem(chat_id, resposta_ia)

async def enviar_mensagem(chat_id: str, texto: str) -> None:
    """
    Envia uma mensagem ao chat via API do Telegram.
    """
    # Constrói a URL corretamente, sem quebras ou espaços
    base_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
    url = f"{base_url}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto}
    tp_logger.info(f"📤 Enviando mensagem - URL: {url}, payload: {payload}")
    try:
        response = requests.post(url, json=payload, timeout=10)
        tp_logger.info(f"📥 Telegram respondeu: {response.status_code} - {response.text}")
    except Exception as e:
        tp_logger.error(f"❌ Erro ao enviar mensagem: {e}")
