import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.telegram_utils import processar_mensagem, enviar_mensagem
from app.db import registrar_usuario, verificar_acesso
from app.painel import router as painel_router

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("draana")

# Inicialização do FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

# Roteador do painel administrativo em /painel
app.include_router(painel_router)

@app.post("/webhook")
async def receive_webhook(request: Request):
    # 1. Leia todo o JSON do webhook e registre no log
    payload = await request.json()
    logger.info(f"📩 Payload recebido: {payload}")

    # 2. Extraia dados do usuário
    message = payload.get("message", {})
    user = message.get("from", {})
    user_id = str(user.get("id", ""))
    nome = user.get("first_name", "Desconhecida")

    # 3. Registre no banco e verifique acesso
    registrar_usuario(user_id, nome)
    if not verificar_acesso(user_id):
        await enviar_mensagem(
            user_id,
            "❌ Seu período de uso gratuito terminou.

"
            "Entre em contato com o suporte para continuar usando a Dra. Ana ❤️"
        )
        return {"status": "bloqueado"}

    # 4. Processe a mensagem: adicionar histórico, gerar resposta e enviar ao Telegram
    try:
        await processar_mensagem(payload)
        logger.info(f"✅ Mensagem processada para usuário {user_id}")
    except Exception as e:
        logger.error(f"❌ Erro ao processar mensagem: {e}")
    return {"status": "ok"}
