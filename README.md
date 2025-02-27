# Sistema de Gestão de Imóveis

Sistema local para gestão de imóveis com funcionalidades de cadastro, gerenciamento e geração de PDF.

## Funcionalidades

- Cadastro de imóveis com fotos
- Gerenciamento de imóveis
- Geração de PDF para divulgação
- Filtros por tipo de imóvel
- Armazenamento local com SQLite

## Requisitos

- Python 3.8+
- Dependências listadas em requirements.txt

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/Scripts/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute o servidor:
```bash
uvicorn app.main:app --reload
```

5. Acesse o sistema em: http://localhost:8000

## Estrutura do Projeto

```
.
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── routes/
│   ├── static/
│   └── templates/
├── uploads/
│   └── imoveis/
├── requirements.txt
└── README.md
``` # sitei-moveis
# sitei-moveis
# Site-Imoveis
