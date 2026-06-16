# 🚀 CTC Reader

API desenvolvida com FastAPI para leitura de arquivos CTC - Certidão de Tempo de Contribuição do INSS.

## 🛠 Tecnologias

- Python 3.13.1
- FastAPI
- Uvicorn
- Pydantic
- PDFPlumber

## 🐍 Ambiente Virtual

Este projeto utiliza um ambiente virtual (`.venv`) para isolamento das dependências.

Para criar o ambiente:

```
python -m venv .venv
```

Para ativar:

Windows

```
.venv\Scripts\activate
```

Linux/Mac

```
source .venv/bin/activate
```

Instalar dependências

```
pip install -r requirements.txt
```

## ▶️ Rodar a aplicação

```
uvicorn main:app --reload
```

A API estará disponível em

```
http://127.0.0.1:8000/
```

Documentação automática (Via Swagger)

```
http://127.0.0.1:8000/ctc-reader/docs
```

## ⚙️ Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```
API_TOKEN=seu_token_super_secreto
```

## 📂 Estrutura do Projeto

```
|.env
│.env.example
│.gitignore
│dependencies.py
│leitura_pdf.py
│main.py
|README.md
|requirements.txt
│schemas.py
```

![Python](https://img.shields.io/badge/python-3.13.1-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128.7-green)
