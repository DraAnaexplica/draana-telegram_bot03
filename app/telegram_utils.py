# app/telegram_utils.py

import os
import requests
from app.chat_db import add_chat_message, get_chat_history

from app.openrouter_utils import gerar_resposta_openrouter
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def enviar_mensagem_telegram(chat_id, texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def processar_mensagem_telegram(data):
    try:
        chat_id = data["message"]["chat"]["id"]
        texto_usuario = data["message"]["text"]

        # Salva a mensagem do usuário
        add_chat_message(str(chat_id), "user", texto_usuario)

        # Recupera o histórico
        historico = get_chat_history(str(chat_id), limit=10)
        mensagens = [{"role": m["role"], "content": m["content"]} for m in historico]

        # Gera resposta da IA
        resposta = gerar_resposta_openrouter(mensagens)

        # Salva resposta da IA
        add_chat_message(str(chat_id), "assistant", resposta)

        # Envia resposta ao Telegram
        enviar_mensagem_telegram(chat_id, resposta)

    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
