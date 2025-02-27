from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

class ContatoModel(BaseModel):
    nome: str
    email: str
    telefone: Optional[str] = None
    assunto: str
    mensagem: str

@router.get("/contatos")
async def contatos(request: Request):
    return templates.TemplateResponse("contatos.html", {"request": request})

@router.post("/api/contatos")
async def enviar_contato(contato: ContatoModel):
    # Redirecionar para WhatsApp
    return {
        "status": "success",
        "message": "Redirecionando para WhatsApp..."
    } 