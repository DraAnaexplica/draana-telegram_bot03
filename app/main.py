import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.telegram_utils import processar_mensagem, enviar_mensagem
from app.db import registrar_usuario, verificar_acesso
from app.painel import router as painel_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("draana")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

# Painel de usuárias sem prefixo duplicado
app.include_router(painel_router)

@app.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.json()
    logger.info("📩 Payload recebido: %s", payload)

    message = payload.get("message", {})
    user = message.get("from", {})
    user_id = str(user.get("id", ""))
    nome = user.get("first_name", "Desconhecida")

    registrar_usuario(user_id, nome)
    if not verificar_acesso(user_id):
        await enviar_mensagem(
            user_id,
            "❌ Seu período de uso gratuito terminou.\n\n"  
            "Entre em contato com o suporte para continuar usando a Dra. Ana ❤️"
        )
        return {"status": "bloqueado"}

    try:
        await processar_mensagem(payload)
        logger.info("✅ Mensagem processada para usuário %s", user_id)
    except Exception as e:
        logger.error("❌ Erro ao processar mensagem: %s", e)

    return {"status": "ok"}