from fastapi import FastAPI
from leitura_pdf import leituraCTC
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(docs_url=None, title="CTC Reader", description="API responsável por processar os dados da CTC - Certidão de Tempo de Contribuição do INSS", version="v1")

# Libera o front-end Angular (dev) a chamar a API a partir do navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leituraCTC)

@app.get("/ctc-reader/docs", include_in_schema=False)
def custom_docs():
    return get_swagger_ui_html(openapi_url=app.openapi_url, title="Swagger UI", swagger_ui_parameters={"deepLinking": False})