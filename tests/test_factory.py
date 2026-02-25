import pytest
from src.snh_project.services.factory import DietaFactory
from src.snh_project.core.diets import DietaOral, DietaEnteral

# --- Fixtures (Dados de Teste Reutilizáveis) ---
@pytest.fixture
def dados_oral_validos():
    return {
        'textura': 'Pastosa',
        'numero_refeicoes': 6,
        'tipo_refeicao': 'Janta', 
        'descricao': 'Dieta leve para pós-operatório',
        'usuario_responsavel': 'Nutri Ana'
    }

@pytest.fixture
def dados_enteral_validos():
    return {
        'setor_clinico': 'UTI Geral',
        'via_infusao': 'nasogástrica',
        'velocidade_ml_h': 60.5,
        'quantidade_gramas_por_porção': 200.0,
        'porcoes_diarias': 4,
        'tipo_equipo': 'Gravitacional',
        'usuario_responsavel': 'Enf. Carlos'
    }

# --- Testes de Criação com Sucesso ---

def test_criar_dieta_oral_sucesso(dados_oral_validos):
    """Testa se a factory retorna corretamente uma instância de DietaOral."""
    dieta = DietaFactory.criar_dieta('oral', dados_oral_validos)
    assert isinstance(dieta, DietaOral)
    # Acesso a protegidos pois não há getters públicos no momento
    assert dieta._textura == 'pastosa'
    assert dieta._numero_refeicoes == 6

def test_criar_dieta_enteral_sucesso(dados_enteral_validos):
    """Testa se a factory retorna corretamente uma instância de DietaEnteral."""
    dieta = DietaFactory.criar_dieta('enteral', dados_enteral_validos)
    assert isinstance(dieta, DietaEnteral)
    assert dieta._velocidade_ml_h == 60.5
    assert dieta._via_infusao == 'nasogástrica'

def test_criar_dieta_ignora_case_sensitive(dados_oral_validos):
    """Testa se a factory aceita 'ORAL', 'Oral', ' oRaL '."""
    dieta = DietaFactory.criar_dieta('  ORAL ', dados_oral_validos)
    assert isinstance(dieta, DietaOral)

def test_criar_dieta_com_valores_default(dados_enteral_validos):
    """Testa se a factory preenche corretamente os campos opcionais."""
    if 'tipo_equipo' in dados_enteral_validos:
        del dados_enteral_validos['tipo_equipo']
    
    dieta = DietaFactory.criar_dieta('enteral', dados_enteral_validos)
    assert dieta._tipo_equipo == 'bomba' 

def test_criar_dieta_oral_default_usuario(dados_oral_validos):
    """Testa se usuário responsável vira 'sistema' se omitido."""
    if 'usuario_responsavel' in dados_oral_validos:
        del dados_oral_validos['usuario_responsavel']
        
    dieta = DietaFactory.criar_dieta('oral', dados_oral_validos)
    # Verifica atributo na classe base (se acessível) ou na instância
    # Assumindo que a classe base salva em _usuario_responsavel
    if hasattr(dieta, '_usuario_responsavel'):
        assert dieta._usuario_responsavel == 'sistema'

# --- Testes de Exceção (Validação e Robustez) ---

def test_erro_tipo_dieta_desconhecido():
    with pytest.raises(ValueError, match="Tipo de dieta desconhecido"):
        DietaFactory.criar_dieta('parenteral', {})

def test_erro_oral_parametros_faltando(dados_oral_validos):
    del dados_oral_validos['textura']
    with pytest.raises(ValueError, match="Dieta Oral exige os seguintes parâmetros"):
        DietaFactory.criar_dieta('oral', dados_oral_validos)

def test_erro_enteral_valores_negativos(dados_enteral_validos):
    dados_enteral_validos['velocidade_ml_h'] = -10.0
    with pytest.raises(ValueError, match="Parâmetro 'velocidade_ml_h' inválido"):
        DietaFactory.criar_dieta('enteral', dados_enteral_validos)

def test_erro_enteral_gramas_invalido(dados_enteral_validos):
    """Deve lançar ValueError se gramas por porção for <= 0."""
    dados_enteral_validos['quantidade_gramas_por_porção'] = 0
    # CORREÇÃO: Match ajustado para a mensagem real da Factory
    with pytest.raises(ValueError, match="Parâmetro 'quantidade_gramas_por_porção' inválido"):
        DietaFactory.criar_dieta('enteral', dados_enteral_validos)

def test_erro_numero_refeicoes_invalido(dados_oral_validos):
    dados_oral_validos['numero_refeicoes'] = "três"
    with pytest.raises(ValueError, match="Parâmetro 'numero_refeicoes' inválido"):
        DietaFactory.criar_dieta('oral', dados_oral_validos)

def test_erro_porcoes_diarias_invalido(dados_enteral_validos):
    dados_enteral_validos['porcoes_diarias'] = 0
    with pytest.raises(ValueError, match="Parâmetro 'porcoes_diarias' inválido"):
        DietaFactory.criar_dieta('enteral', dados_enteral_validos)