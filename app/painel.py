
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.db import conectar

router = APIRouter()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Painel de Usuárias - Dra. Ana</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f9f9f9; padding: 20px; }
        table { border-collapse: collapse; width: 100%; background: #fff; }
        th, td { padding: 10px; border: 1px solid #ccc; text-align: left; }
        th { background: #f0f0f0; }
        form { display: inline; }
        button { padding: 5px 10px; margin: 0 5px; }
        h1 { margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>👩‍⚕️ Painel de Controle de Usuárias</h1>
    <table>
        <tr>
            <th>User ID</th>
            <th>Nome</th>
            <th>Ativo</th>
            <th>Dias Restantes</th>
            <th>Ações</th>
        </tr>
        {% for usuaria in usuarias %}
        <tr>
            <td>{{ usuaria.user_id }}</td>
            <td>{{ usuaria.nome or '' }}</td>
            <td>{{ '✅' if usuaria.ativo else '❌' }}</td>
            <td>{{ usuaria.dias_restantes }}</td>
            <td>
                <form method="post" action="/painel/bloquear">
                    <input type="hidden" name="user_id" value="{{ usuaria.user_id }}">
                    <button type="submit">Bloquear</button>
                </form>
                <form method="post" action="/painel/ativar">
                    <input type="hidden" name="user_id" value="{{ usuaria.user_id }}">
                    <button type="submit">Ativar</button>
                </form>
                <form method="post" action="/painel/renovar">
                    <input type="hidden" name="user_id" value="{{ usuaria.user_id }}">
                    <input type="number" name="dias" min="1" max="365" placeholder="Dias">
                    <button type="submit">Renovar</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
'''

@router.get("/painel", response_class=HTMLResponse)
def exibir_painel():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT user_id, nome, ativo, dias_restantes FROM usuarios ORDER BY data_cadastro DESC")
    usuarias = [dict(user_id=r[0], nome=r[1], ativo=r[2], dias_restantes=r[3]) for r in cur.fetchall()]
    cur.close()
    conn.close()

    from jinja2 import Template
    template = Template(HTML_TEMPLATE)
    return template.render(usuarias=usuarias)

@router.post("/painel/bloquear")
def bloquear_usuario_painel(user_id: str = Form(...)):
    from app.db import bloquear_usuario
    bloquear_usuario(user_id)
    return RedirectResponse(url="/painel", status_code=303)

@router.post("/painel/ativar")
def ativar_usuario_painel(user_id: str = Form(...)):
    from app.db import ativar_usuario
    ativar_usuario(user_id)
    return RedirectResponse(url="/painel", status_code=303)

@router.post("/painel/renovar")
def renovar_usuario_painel(user_id: str = Form(...), dias: int = Form(...)):
    from app.db import renovar_acesso
    renovar_acesso(user_id, dias)
    return RedirectResponse(url="/painel", status_code=303)
