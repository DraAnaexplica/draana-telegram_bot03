import os
import requests
from app.db import add_chat_message, get_chat_history
from app.openrouter_utils import gerar_resposta_openrouter

TOKEN_TELEGRAM = os.getenv("TELEGRAM_BOT_TOKEN")
URL_BASE_TELEGRAM = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"

async def processar_mensagem(request):
    body = await request.json()
    try:
        mensagem = body["message"]["text"]
        user_id = str(body["message"]["from"]["id"])
        chat_id = body["message"]["chat"]["id"]

        add_chat_message(user_id, "user", mensagem)
        historico = get_chat_history(user_id)
        resposta = gerar_resposta_openrouter(historico)
        add_chat_message(user_id, "assistant", resposta)

        payload = {
            "chat_id": chat_id,
            "text": resposta
        }
        requests.post(URL_BASE_TELEGRAM, json=payload)

    except Exception as e:
        print("Erro ao processar mensagem:", e)

    return {"status": "ok"}
