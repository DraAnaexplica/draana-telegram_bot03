from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.db import (
    conectar, ativar_usuario, bloquear_usuario,
    renovar_acesso, excluir_usuario, limpar_usuarios
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/painel", response_class=HTMLResponse)
def mostrar_painel(request: Request):
    conn = conectar()
    with conn.cursor() as cur:
        cur.execute("SELECT user_id, nome, ativo, dias_restantes FROM usuarios;")
        usuarias = cur.fetchall()
    conn.close()
    return templates.TemplateResponse("painel.html", {
        "request": request,
        "usuarias": usuarias
    })

@router.post("/painel/ativar")
def rota_ativar(user_id: str = Form(...)):
    ativar_usuario(user_id)
    return RedirectResponse("/painel", status_code=303)

@router.post("/painel/bloquear")
def rota_bloquear(user_id: str = Form(...)):
    bloquear_usuario(user_id)
    return RedirectResponse("/painel", status_code=303)

@router.post("/painel/renovar")
def rota_renovar(user_id: str = Form(...), dias: int = Form(...)):
    renovar_acesso(user_id, dias)
    return RedirectResponse("/painel", status_code=303)

@router.post("/painel/excluir")
def rota_excluir(user_id: str = Form(...)):
    excluir_usuario(user_id)
    return RedirectResponse("/painel", status_code=303)

@router.post("/painel/limpar")
def rota_limpar():
    limpar_usuarios()
    return RedirectResponse("/painel", status_code=303)
