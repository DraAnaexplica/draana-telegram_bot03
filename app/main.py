from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app import telegram_utils, painel

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.post("/webhook")
async def webhook(request: Request):
    return await telegram_utils.handle_telegram_webhook(await request.json())

@app.get("/painel", response_class=HTMLResponse)
def exibir_painel(request: Request):
    return painel.exibir_painel(request)

@app.post("/painel/bloquear")
def bloquear_usuario(user_id: str = Form(...)):
    return painel.bloquear_usuario(user_id)

@app.post("/painel/desbloquear")
def desbloquear_usuario(user_id: str = Form(...)):
    return painel.desbloquear_usuario(user_id)

@app.post("/painel/renovar")
def renovar_acesso(user_id: str = Form(...)):
    return painel.renovar_acesso(user_id)

@app.post("/painel/apagar")
def apagar_usuario(user_id: str = Form(...)):
    return painel.apagar_usuario(user_id)
