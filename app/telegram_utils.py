import requests
import os
from dotenv import load_dotenv
from app.chat_db import add_chat_message, get_chat_history
from app.openrouter_utils import gerar_resposta_openrouter
from app.db import verificar_acesso


load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

async def processar_mensagem(payload):
    try:
        mensagem = payload["message"]
        user_id = str(mensagem["from"]["id"])
        nome = mensagem["from"].get("first_name", "Desconhecida")
        texto = mensagem.get("text", "")

        # Registra usuária (caso nova)
        registrar_usuario(user_id, nome)

        # Verifica se usuária tem acesso
        if not verificar_acesso(user_id):
            texto_bloqueio = (
                "❌ Seu período de uso gratuito terminou.\n\n"
                "Entre em contato com o suporte para continuar usando a Dra. Ana ❤️"
            )
            enviar_mensagem(user_id, texto_bloqueio)
            return {"status": "bloqueado"}

        # Pega histórico da conversa
        historico = get_chat_history(user_id)

        # Adiciona a nova mensagem no histórico
        add_chat_message(user_id, "user", texto)

        # Gera resposta com IA
        resposta = gerar_resposta_openrouter(historico + [{"role": "user", "content": texto}])

        # Salva resposta no histórico
        add_chat_message(user_id, "assistant", resposta)

        # Envia resposta para o Telegram
        enviar_mensagem(user_id, resposta)
        return {"status": "respondido"}

    except Exception as e:
        print("Erro no processamento:", e)
        return {"erro": "Falha ao processar a mensagem"}

def enviar_mensagem(user_id, texto):
    payload = {
        "chat_id": user_id,
        "text": texto
    }
    try:
        requests.post(API_URL, json=payload)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)
