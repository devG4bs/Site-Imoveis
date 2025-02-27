from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from .database import engine, Base, get_db
from .models.imovel import Imovel  # Importar o modelo
from .models.usuario import Usuario  # Importar o modelo de usuário
from .auth import obter_usuario_admin_atual
from sqlalchemy.orm import Session
import os

# Middleware personalizado para garantir codificação UTF-8
class UTF8Middleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if response.headers.get("content-type", "").startswith("text/html"):
            response.headers["content-type"] = "text/html; charset=utf-8"
        return response

# Criar as tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Gestão de Imóveis")

# Adicionar middleware para compressão
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Adicionar middleware para UTF-8
app.add_middleware(UTF8Middleware)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definir diretórios de uploads
UPLOAD_DIR = "uploads"
IMOVEIS_DIR = os.path.join(UPLOAD_DIR, "imoveis")

# Na Vercel, usar diretório temporário para uploads
if os.environ.get("VERCEL"):
    UPLOAD_DIR = "/tmp/uploads"
    IMOVEIS_DIR = os.path.join(UPLOAD_DIR, "imoveis")

# Criar diretórios de uploads se não existirem
os.makedirs(IMOVEIS_DIR, exist_ok=True)

# Configurar diretórios estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Configurar templates
templates = Jinja2Templates(directory="app/templates")
templates.env.globals.update({"charset": "utf-8"})

# Importar rotas
from .routes import imoveis, auth

# Incluir rotas
app.include_router(imoveis.router)
app.include_router(auth.router)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/admin")
async def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/imoveis/{imovel_id}/detalhes")
async def imovel_detalhes(request: Request, imovel_id: int, db: Session = Depends(get_db)):
    # Buscar o imóvel no banco de dados
    imovel = db.query(Imovel).filter(Imovel.id == imovel_id).first()
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    # Renderizar o template com os dados do imóvel
    return templates.TemplateResponse("imovel_detalhes.html", {
        "request": request,
        "imovel": imovel,
        "fotos": imovel.fotos
    }) 