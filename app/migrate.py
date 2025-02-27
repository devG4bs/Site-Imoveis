from sqlalchemy import create_engine, text
import os
from app.models.imovel import Base

def migrate():
    # Obter o caminho absoluto do diretório atual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "database.sqlite")
    
    # Criar a URL do banco de dados
    database_url = f"sqlite:///{db_path}"
    
    # Criar engine
    engine = create_engine(database_url)
    
    # Criar todas as tabelas definidas nos modelos
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas/atualizadas com sucesso!")
    
    with engine.connect() as conn:
        try:
            # Verificar se a coluna já existe
            conn.execute(text("SELECT comodos FROM imoveis LIMIT 1"))
            print("A coluna 'comodos' já existe.")
        except Exception:
            # Adicionar a coluna comodos
            conn.execute(text("ALTER TABLE imoveis ADD COLUMN comodos INTEGER"))
            conn.commit()
            print("Coluna 'comodos' adicionada com sucesso!")

if __name__ == "__main__":
    migrate() 