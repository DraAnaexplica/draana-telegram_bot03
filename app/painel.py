from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

from app.db import (
    get_all_users,
    ativar_usuario,
    bloquear_usuario,
    renovar_acesso,
    excluir_usuario,
    limpar_usuarios,
)

router = APIRouter()
env = Environment(loader=FileSystemLoader("app/templates"))

@router.get("/painel", response_class=HTMLResponse)
async def view_painel(request: Request):
    usuarios = get_all_users()
    template = env.get_template("painel.html")
    return HTMLResponse(template.render(request=request, usuarios=usuarios))

@router.post("/painel/ativar")
async def action_ativar(user_id: str = Form(...)):
    ativar_usuario(user_id)
    return {"status": "ativado"}

@router.post("/painel/bloquear")
async def action_bloquear(user_id: str = Form(...)):
    bloquear_usuario(user_id)
    return {"status": "bloqueado"}

@router.post("/painel/renovar")
async def action_renovar(user_id: str = Form(...), dias: int = Form(...)):
    renovar_acesso(user_id, dias)
    return {"status": "renovado"}

@router.post("/painel/excluir")
async def action_excluir(user_id: str = Form(...)):
    excluir_usuario(user_id)
    return {"status": "excluido"}

@router.post("/painel/limpar")
async def action_limpar():
    limpar_usuarios()
    return {"status": "limpo"}