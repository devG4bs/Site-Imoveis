from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from ..database import get_db
from ..models.usuario import Usuario
from ..schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioLogin, UsuarioUpdate
from ..auth import (
    verificar_senha, 
    gerar_hash_senha, 
    criar_token_acesso, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    obter_usuario_atual,
    obter_usuario_admin_atual
)

router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)

@router.post("/registrar", response_model=UsuarioResponse)
async def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registra um novo usuário no sistema.
    Apenas o primeiro usuário registrado será automaticamente um administrador.
    """
    # Verificar se o email já está em uso
    db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registrado"
        )
    
    # Verificar se é o primeiro usuário (será admin)
    is_primeiro_usuario = db.query(Usuario).count() == 0
    
    # Criar o novo usuário
    senha_hash = gerar_hash_senha(usuario.senha)
    novo_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=senha_hash,
        is_admin=is_primeiro_usuario or usuario.is_admin  # Primeiro usuário ou explicitamente admin
    )
    
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    
    return novo_usuario

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Autentica um usuário e retorna um token de acesso.
    """
    # Buscar usuário pelo email
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    
    # Verificar se o usuário existe e a senha está correta
    if not usuario or not verificar_senha(form_data.password, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Criar token de acesso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = criar_token_acesso(
        data={"sub": usuario.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": usuario.id,
        "is_admin": usuario.is_admin
    }

@router.post("/login")
async def login_json(usuario: UsuarioLogin, db: Session = Depends(get_db)):
    """
    Autentica um usuário usando JSON e retorna um token de acesso.
    """
    # Buscar usuário pelo email
    db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    
    # Verificar se o usuário existe e a senha está correta
    if not db_usuario or not verificar_senha(usuario.senha, db_usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Criar token de acesso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = criar_token_acesso(
        data={"sub": db_usuario.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_usuario.id,
        "is_admin": db_usuario.is_admin
    }

@router.get("/me", response_model=UsuarioResponse)
async def ler_usuario_atual(usuario_atual: Usuario = Depends(obter_usuario_atual)):
    """
    Retorna informações do usuário atualmente autenticado.
    """
    return usuario_atual

@router.get("/usuarios", response_model=List[UsuarioResponse])
async def listar_usuarios(
    usuario_admin: Usuario = Depends(obter_usuario_admin_atual),
    db: Session = Depends(get_db)
):
    """
    Lista todos os usuários (apenas para administradores).
    """
    usuarios = db.query(Usuario).all()
    return usuarios

@router.get("/usuarios/{usuario_id}", response_model=UsuarioResponse)
async def obter_usuario(
    usuario_id: int,
    usuario_admin: Usuario = Depends(obter_usuario_admin_atual),
    db: Session = Depends(get_db)
):
    """
    Obtém um usuário específico pelo ID (apenas para administradores).
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@router.post("/usuarios", response_model=UsuarioResponse)
async def criar_usuario(
    usuario: UsuarioCreate,
    usuario_admin: Usuario = Depends(obter_usuario_admin_atual),
    db: Session = Depends(get_db)
):
    """
    Cria um novo usuário (apenas para administradores).
    """
    # Verificar se o email já está em uso
    db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registrado"
        )
    
    # Criar o novo usuário
    senha_hash = gerar_hash_senha(usuario.senha)
    novo_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=senha_hash,
        is_admin=usuario.is_admin
    )
    
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    
    return novo_usuario

@router.put("/usuarios/{usuario_id}", response_model=UsuarioResponse)
async def atualizar_usuario(
    usuario_id: int,
    usuario_data: UsuarioUpdate,
    usuario_admin: Usuario = Depends(obter_usuario_admin_atual),
    db: Session = Depends(get_db)
):
    """
    Atualiza um usuário existente (apenas para administradores).
    """
    # Buscar o usuário
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar se o email já está em uso por outro usuário
    if usuario_data.email and usuario_data.email != db_usuario.email:
        email_existente = db.query(Usuario).filter(Usuario.email == usuario_data.email).first()
        if email_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já registrado para outro usuário"
            )
    
    # Atualizar os campos
    if usuario_data.nome:
        db_usuario.nome = usuario_data.nome
    if usuario_data.email:
        db_usuario.email = usuario_data.email
    if usuario_data.senha:
        db_usuario.senha_hash = gerar_hash_senha(usuario_data.senha)
    if usuario_data.is_admin is not None:
        db_usuario.is_admin = usuario_data.is_admin
    
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario

@router.delete("/usuarios/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_usuario(
    usuario_id: int,
    usuario_admin: Usuario = Depends(obter_usuario_admin_atual),
    db: Session = Depends(get_db)
):
    """
    Exclui um usuário (apenas para administradores).
    """
    # Buscar o usuário
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Impedir a exclusão do próprio usuário administrador
    if db_usuario.id == usuario_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível excluir o próprio usuário"
        )
    
    db.delete(db_usuario)
    db.commit()
    
    return None 