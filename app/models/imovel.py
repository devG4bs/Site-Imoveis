from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import column_property
import os
from ..database import Base

class Imovel(Base):
    __tablename__ = "imoveis"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50))  # venda, aluguel, leilao
    titulo = Column(String(200))
    descricao = Column(Text)
    valor = Column(Float)
    etiqueta = Column(String(50))  # destaque, novo, etc
    endereco = Column(String(200))
    area = Column(Float)
    quartos = Column(Integer)
    banheiros = Column(Integer)
    vagas = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def fotos(self):
        """Retorna a lista de fotos do imóvel"""
        upload_dir = f"uploads/imoveis/{self.id}"
        if not os.path.exists(upload_dir):
            return []
        return sorted([
            f for f in os.listdir(upload_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'))
        ]) 