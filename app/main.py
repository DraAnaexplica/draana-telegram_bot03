from fastapi import FastAPI, Request
from app import telegram_utils, db, painel
import uvicorn

app = FastAPI()

# ⬇️ Inclui o painel de controle de usuárias
app.include_router(painel.router)

@app.get("/")
def home():
    return {"mensagem": "API da Dra. Ana está ativa."}

@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()
    try:
        user_id = str(payload["message"]["from"]["id"])
        nome = payload["message"]["from"].get("first_name", "Desconhecida")

        # Registra usuária, se for nova
        db.registrar_usuario(user_id, nome)

        # Verifica se ainda tem acesso
        if not db.verificar_acesso(user_id):
            texto_bloqueio = (
                "❌ Seu período de uso gratuito terminou.\n\n"
                "Entre em contato com o suporte para continuar usando a Dra. Ana ❤️"
            )
            telegram_utils.enviar_mensagem(user_id, texto_bloqueio)
            return {"status": "bloqueado"}

        return await telegram_utils.processar_mensagem(payload)

    except Exception as e:
        print("Erro no webhook:", e)
        return {"erro": "Falha ao processar a mensagem"}

@app.get("/simular_usuario/{user_id}")
def simular_usuario(user_id: str):
    db.registrar_usuario(user_id)
    acesso = db.verificar_acesso(user_id)
    if acesso:
        return {"status": "liberado", "mensagem": "Usuária tem acesso liberado."}
    else:
        return {"status": "bloqueado", "mensagem": "Acesso negado ou expirado."}
