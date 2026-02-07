from fastapi import FastAPI

app = FastAPI(
    title='SNH',
    description='Sistema de Nutrição Hospitalar',
    version='0.1.0',
)
from .pac_routers import paciente_router

app.include_router(paciente_router)

@app.get('/')
def read_root():
    return {'Status': 'Tá rodando papai'}