from fastapi import FastAPI, Request
from app import telegram_utils, db
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    return {"mensagem": "API da Dra. Ana está ativa."}

@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()
    try:
        user_id = str(payload["message"]["from"]["id"])
        nome = payload["message"]["from"].get("first_name", "Desconhecida")

        # REGISTRA USUÁRIA CASO NOVA
        db.registrar_usuario(user_id, nome)

        # VERIFICA ACESSO
        if not db.verificar_acesso(user_id):
            return {"mensagem": "Acesso negado. Seu período de uso expirou."}

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
