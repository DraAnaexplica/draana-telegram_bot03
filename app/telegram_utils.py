import os
import logging
import requests

# Logger para este módulo
tp_logger = logging.getLogger("draana.telegram_utils")

# Token do bot da variável de ambiente
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def processar_mensagem(payload: dict) -> None:
    """
    Processa o update do Telegram: armazena no histórico, gera resposta via OpenRouter e envia ao usuário.
    """
    # Importações locais para evitar circularidades
    from app.chat_db import add_chat_message, get_chat_history
    from app.openrouter_utils import gerar_resposta_openrouter

    # Extrai informações do payload
    chat = payload.get("message", {}).get("chat", {})
    chat_id = chat.get("id")
    texto_usuario = payload.get("message", {}).get("text", "")
    tp_logger.info(f"📝 processar_mensagem - chat_id={chat_id}, texto='{texto_usuario}'")

    # Salva mensagem do usuário
    add_chat_message(str(chat_id), "user", texto_usuario)

    # Recupera histórico e obtém resposta da IA
    historico = get_chat_history(str(chat_id))
    resposta_ia = gerar_resposta_openrouter(historico)
    tp_logger.info(f"🤖 Resposta do modelo: '{resposta_ia}'")

    # Envia a resposta
    await enviar_mensagem(chat_id, resposta_ia)

async def enviar_mensagem(chat_id: str, texto: str) -> None:
    """
    Envia uma mensagem ao chat via API do Telegram.
    """
    # Montagem da URL sem quebras de linha
    url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage"
    payload = {"chat_id": chat_id, "text": texto}
    tp_logger.info(f"📤 Enviando mensagem - URL: {url}, payload: {payload}")
    try:
        response = requests.post(url, json=payload, timeout=10)
        tp_logger.info(f"📥 Telegram respondeu: {response.status_code} - {response.text}")
    except Exception as e:
        tp_logger.error(f"❌ Erro ao enviar mensagem: {e}")
