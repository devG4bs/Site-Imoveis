from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
from datetime import datetime
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import json
import mimetypes
import logging
import traceback
from fastapi.templating import Jinja2Templates

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from ..database import get_db
from ..models.imovel import Imovel
from ..schemas.imovel import ImovelCreate, Imovel as ImovelSchema
from ..models.usuario import Usuario
from ..auth import obter_usuario_admin_atual

router = APIRouter(prefix="/imoveis", tags=["imoveis"])
templates = Jinja2Templates(directory="app/templates")

def is_valid_image(filename: str) -> bool:
    # Lista de extensões permitidas
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    return os.path.splitext(filename.lower())[1] in valid_extensions

# Função auxiliar para salvar imagem
async def save_image(imovel_id: int, file: UploadFile) -> str:
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nome do arquivo não fornecido")
        
        logger.info(f"Processando arquivo: {file.filename}")
        
        # Verifica se é uma imagem válida pela extensão
        if not is_valid_image(file.filename):
            raise HTTPException(status_code=400, detail="O arquivo deve ser uma imagem (jpg, jpeg, png, gif, bmp, webp)")
        
        # Cria o diretório se não existir
        upload_dir = f"uploads/imoveis/{imovel_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Gera um nome único para o arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        file_extension = os.path.splitext(file.filename)[1].lower()
        new_filename = f"{timestamp}{file_extension}"
        file_path = f"{upload_dir}/{new_filename}"
        
        logger.info(f"Salvando arquivo em: {file_path}")
        
        # Verifica se o arquivo está aberto e pode ser lido
        if file.file.closed:
            raise ValueError("O arquivo está fechado e não pode ser lido")
            
        # Salva o arquivo
        file.file.seek(0)  # Volta para o início do arquivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Arquivo salvo com sucesso: {new_filename}")
        return new_filename
    except Exception as e:
        error_msg = f"Erro ao salvar imagem: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/lista", response_class=HTMLResponse)
async def listar_imoveis(
    request: Request,
    page: int = 1,
    tipo: str = None,
    tipo_imovel: str = None,
    valor_min: float = None,
    valor_max: float = None,
    db: Session = Depends(get_db)
):
    per_page = 9
    query = db.query(Imovel)
    
    if tipo:
        query = query.filter(Imovel.tipo == tipo)
    if tipo_imovel:
        query = query.filter(Imovel.tipo_imovel == tipo_imovel)
    if valor_min is not None:
        query = query.filter(Imovel.valor >= valor_min)
    if valor_max is not None:
        query = query.filter(Imovel.valor <= valor_max)
    
    query = query.order_by(Imovel.created_at.desc())
    total = query.count()
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) * per_page
    imoveis = query.offset(offset).limit(per_page).all()
    
    return templates.TemplateResponse("imoveis.html", {
        "request": request,
        "imoveis": imoveis,
        "page": page,
        "total_pages": total_pages
    })

@router.post("/", response_model=ImovelSchema)
async def create_imovel(
    tipo: str = Form(...),
    tipo_imovel: str = Form(...),
    titulo: str = Form(...),
    descricao: str = Form(...),
    valor: float = Form(...),
    etiqueta: str = Form(...),
    endereco: str = Form(...),
    area: float = Form(...),
    comodos: int = Form(...),
    quartos: int = Form(...),
    banheiros: int = Form(...),
    vagas: int = Form(...),
    fotos: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    admin: Usuario = Depends(obter_usuario_admin_atual)
):
    try:
        logger.info("Iniciando criação de novo imóvel")
        
        # Verificar se foram enviadas fotos
        if not fotos:
            raise HTTPException(status_code=400, detail="É necessário enviar pelo menos uma foto")

        # Criar objeto do imóvel
        imovel_data = {
            "tipo": tipo,
            "tipo_imovel": tipo_imovel,
            "titulo": titulo,
            "descricao": descricao,
            "valor": float(valor),
            "etiqueta": etiqueta,
            "endereco": endereco,
            "area": float(area),
            "comodos": int(comodos),
            "quartos": int(quartos),
            "banheiros": int(banheiros),
            "vagas": int(vagas)
        }
        
        logger.info(f"Dados do imóvel: {imovel_data}")
        
        # Criar e salvar o imóvel
        db_imovel = Imovel(**imovel_data)
        db.add(db_imovel)
        db.commit()
        db.refresh(db_imovel)
        
        logger.info(f"Imóvel criado com ID: {db_imovel.id}")
        
        # Salvar as fotos
        saved_photos = []
        for foto in fotos:
            try:
                filename = await save_image(db_imovel.id, foto)
                saved_photos.append(filename)
                logger.info(f"Foto salva: {filename}")
            except Exception as e:
                error_msg = f"Erro ao salvar foto: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
                # Se houver erro ao salvar as fotos, remove o imóvel e as fotos já salvas
                db.delete(db_imovel)
                db.commit()
                shutil.rmtree(f"uploads/imoveis/{db_imovel.id}", ignore_errors=True)
                raise HTTPException(status_code=500, detail=error_msg)
        
        logger.info(f"Todas as {len(saved_photos)} fotos foram salvas com sucesso")
        return db_imovel
        
    except ValueError as e:
        error_msg = f"Erro de validação: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = f"Erro inesperado: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/", response_model=List[ImovelSchema])
def list_imoveis(
    tipo: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Imovel)
    if tipo:
        query = query.filter(Imovel.tipo == tipo)
    return query.all()

@router.get("/{imovel_id}", response_model=ImovelSchema)
def get_imovel(imovel_id: int, db: Session = Depends(get_db)):
    imovel = db.query(Imovel).filter(Imovel.id == imovel_id).first()
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    return imovel

@router.put("/{imovel_id}", response_model=ImovelSchema)
async def update_imovel(
    imovel_id: int,
    tipo: str = Form(...),
    titulo: str = Form(...),
    descricao: str = Form(...),
    valor: float = Form(...),
    etiqueta: str = Form(...),
    endereco: str = Form(...),
    area: float = Form(...),
    comodos: int = Form(...),
    quartos: int = Form(...),
    banheiros: int = Form(...),
    vagas: int = Form(...),
    fotos: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    admin: Usuario = Depends(obter_usuario_admin_atual)
):
    try:
        logger.info(f"Iniciando atualização do imóvel {imovel_id}")
        
        # Buscar o imóvel existente
        imovel = db.query(Imovel).filter(Imovel.id == imovel_id).first()
        if not imovel:
            raise HTTPException(status_code=404, detail="Imóvel não encontrado")

        # Atualizar os dados do imóvel
        imovel.tipo = tipo
        imovel.titulo = titulo
        imovel.descricao = descricao
        imovel.valor = float(valor)
        imovel.etiqueta = etiqueta
        imovel.endereco = endereco
        imovel.area = float(area)
        imovel.comodos = int(comodos)
        imovel.quartos = int(quartos)
        imovel.banheiros = int(banheiros)
        imovel.vagas = int(vagas)
        
        # Se novas fotos foram enviadas
        if fotos and any(foto.filename for foto in fotos):
            logger.info("Processando novas fotos")
            
            # Remover fotos antigas
            upload_dir = f"uploads/imoveis/{imovel_id}"
            if os.path.exists(upload_dir):
                shutil.rmtree(upload_dir)
            
            # Salvar novas fotos
            for foto in fotos:
                if foto.filename:
                    await save_image(imovel_id, foto)

        # Salvar alterações no banco
        db.commit()
        db.refresh(imovel)
        
        logger.info(f"Imóvel {imovel_id} atualizado com sucesso")
        return imovel
        
    except ValueError as e:
        error_msg = f"Erro de validação: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = f"Erro inesperado: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.delete("/{imovel_id}")
def delete_imovel(
    imovel_id: int, 
    db: Session = Depends(get_db),
    admin: Usuario = Depends(obter_usuario_admin_atual)
):
    imovel = db.query(Imovel).filter(Imovel.id == imovel_id).first()
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    # Remover diretório de fotos
    shutil.rmtree(f"uploads/imoveis/{imovel_id}", ignore_errors=True)
    
    db.delete(imovel)
    db.commit()
    return {"message": "Imóvel removido com sucesso"}

@router.get("/{imovel_id}/pdf")
def generate_pdf(imovel_id: int, db: Session = Depends(get_db)):
    imovel = db.query(Imovel).filter(Imovel.id == imovel_id).first()
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    # Carregar template
    env = Environment(loader=FileSystemLoader("app/templates"))
    template = env.get_template("imovel_pdf.html")
    
    # Gerar HTML
    fotos = [f for f in os.listdir(f"uploads/imoveis/{imovel_id}") 
             if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    html_content = template.render(
        imovel=imovel,
        fotos=fotos,
        base_url=f"http://localhost:8000/uploads/imoveis/{imovel_id}"
    )
    
    # Gerar PDF
    pdf_path = f"uploads/imoveis/{imovel_id}/imovel_{imovel_id}.pdf"
    HTML(string=html_content).write_pdf(pdf_path)
    
    return FileResponse(pdf_path, filename=f"imovel_{imovel_id}.pdf") 