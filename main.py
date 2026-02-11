from fastapi import FastAPI
from leitura_pdf import leituraCTC
from fastapi.openapi.docs import get_swagger_ui_html

app = FastAPI(docs_url=None, title="CTC Reader", description="API responsável por processar os dados da CTC", version="v1")

app.include_router(leituraCTC)

@app.get("/ctc-reader/docs", include_in_schema=False)
def custom_docs():
    return get_swagger_ui_html(openapi_url=app.openapi_url, title="Swagger UI", swagger_ui_parameters={"deepLinking": False})