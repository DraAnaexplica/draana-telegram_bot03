# app/main.py

from fastapi import FastAPI, Request
from app.telegram_utils import processar_mensagem_telegram
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

@app.post("/webhook")
async def receber_webhook(request: Request):
    try:
        data = await request.json()
        processar_mensagem_telegram(data)
        return {"status": "mensagem recebida"}
    except Exception as e:
        return {"erro": str(e)}

@app.get("/")
def raiz():
    return {"status": "Bot Dra. Ana Telegram ativo"}
