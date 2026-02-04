from fastapi import FastAPI

app = FastAPI(
    title='SNH',
    description='Sistema de Nutrição Hospitalar',
    version='0.1.0',
)


@app.get('/')
def read_root():
    return {'Status': 'Tá rodando papai'}