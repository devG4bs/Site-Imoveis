from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Definir o caminho do banco de dados
# Na Vercel, precisamos usar um caminho que seja gravável
# Em produção, você pode querer usar um banco de dados PostgreSQL
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./imoveis.db")

# Se estiver na Vercel, use um diretório temporário
if os.environ.get("VERCEL"):
    DATABASE_URL = "sqlite:////tmp/imoveis.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 