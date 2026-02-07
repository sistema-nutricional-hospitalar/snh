from fastapi import APIRouter

paciente_router = APIRouter(
    prefix='/pacientes',
    tags=['Pacientes']
)  

# use get para rotas de leitura
# use post para rotas de criação
# use put para rotas de atualização
# use delete para rotas de exclusão


@paciente_router.get('/')
def read_pacientes():
    return {'Pacientes': 'Lista de pacientes'} 

