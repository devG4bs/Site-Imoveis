import sqlite3

def add_comodos_column():
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect('imoveis.db')
        cursor = conn.cursor()
        
        # Adicionar a coluna comodos
        cursor.execute('ALTER TABLE imoveis ADD COLUMN comodos INTEGER')
        
        # Commit das alterações
        conn.commit()
        print("Coluna 'comodos' adicionada com sucesso!")
        
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print("A coluna 'comodos' já existe na tabela.")
        else:
            print(f"Erro ao adicionar coluna: {e}")
    finally:
        # Fechar a conexão
        conn.close()

if __name__ == '__main__':
    add_comodos_column() 