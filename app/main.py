import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.telegram_utils import processar_mensagem, enviar_mensagem
from app.db import registrar_usuario, verificar_acesso
from app.painel import router as painel_router

# Configurações de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("draana")

# Inicialização do FastAPI\app = FastAPI()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

# Inclusão do roteador de painel administrativo
app.include_router(painel_router, prefix="/painel")

@app.post("/webhook")
async def receive_webhook(request: Request):
    # 1. Recebe e loga o payload
    payload = await request.json()
    logger.info("📩 Payload recebido: %s", payload)

    # 2. Extrai informações do usuário
    message = payload.get("message", {})
    user = message.get("from", {})
    user_id = str(user.get("id", ""))
    nome = user.get("first_name", "Desconhecida")

    # 3. Registro e verificação de acesso
    registrar_usuario(user_id, nome)
    if not verificar_acesso(user_id):
        await enviar_mensagem(
            user_id,
            "❌ Seu período de uso gratuito terminou.\n\n" +
            "Entre em contato com o suporte para continuar usando a Dra. Ana ❤️"
        )
        return {"status": "bloqueado"}

    # 4. Processa a mensagem e envia resposta
    try:
        await processar_mensagem(payload)
        logger.info("✅ Mensagem processada para usuário %s", user_id)
    except Exception as e:
        logger.error("❌ Erro ao processar mensagem: %s", e)

    return {"status": "ok"}
