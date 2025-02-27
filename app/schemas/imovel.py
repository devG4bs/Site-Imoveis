from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ImovelBase(BaseModel):
    tipo: str
    titulo: str
    descricao: str
    valor: float
    etiqueta: str
    endereco: str
    area: float
    quartos: int
    banheiros: int
    vagas: int

class ImovelCreate(ImovelBase):
    pass

class Imovel(ImovelBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    fotos: List[str] = []

    class Config:
        from_attributes = True 