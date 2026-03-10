"""
Testes para os novos tipos suportados pela DietaFactory:
    - DietaParenteral
    - DietaMista (Composite)

Segue o mesmo estilo de test_factory.py já existente no projeto.
"""
import pytest
from src.snh_project.services.factory import DietaFactory
from src.snh_project.core.diets import (
    DietaOral,
    DietaEnteral,
    DietaParenteral,
    DietaMista,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def dados_parenteral_validos():
    """Dados mínimos válidos para criar uma DietaParenteral."""
    return {
        'tipo_acesso': 'central',
        'volume_ml_dia': 2000.0,
        'composicao': 'Glicose 50% + Aminoácidos 10% + Lipídios 20%',
        'velocidade_ml_h': 83.3,           # 83.3 * 24 ≈ 1999.2 ml (~100%)
        'descricao': 'NPT pós-cirurgia',
        'usuario_responsavel': 'Dr. João',
    }


@pytest.fixture
def dieta_oral_simples():
    """DietaOral pré-criada para usar como componente de DietaMista."""
    return DietaOral(
        textura='normal',
        numero_refeicoes=5,
        tipo_refeicao='almoço',
        descricao='Oral simples',
    )


@pytest.fixture
def dieta_enteral_simples():
    """DietaEnteral pré-criada para usar como componente de DietaMista."""
    return DietaEnteral(
        setor_clinico='UTI',
        via_infusao='nasogástrica',
        velocidade_ml_h=60.0,
        quantidade_gramas_por_porção=200.0,
    )


@pytest.fixture
def dados_mista_validos(dieta_oral_simples, dieta_enteral_simples):
    """Dados válidos para criar uma DietaMista com 2 componentes (soma = 100%)."""
    return {
        'componentes': [
            {'dieta': dieta_oral_simples,    'percentual': 70.0},
            {'dieta': dieta_enteral_simples, 'percentual': 30.0},
        ],
        'descricao': 'Transição oral/enteral',
        'usuario_responsavel': 'Nutri Ana',
    }


# =============================================================================
# TESTES — DietaParenteral via Factory
# =============================================================================

class TestFactoryParenteral:

    def test_criar_parenteral_sucesso(self, dados_parenteral_validos):
        """Factory deve retornar instância de DietaParenteral com dados válidos."""
        dieta = DietaFactory.criar_dieta('parenteral', dados_parenteral_validos)
        assert isinstance(dieta, DietaParenteral)

    def test_parenteral_atributos_corretos(self, dados_parenteral_validos):
        """Atributos devem ser armazenados corretamente."""
        dieta = DietaFactory.criar_dieta('parenteral', dados_parenteral_validos)
        assert dieta._tipo_acesso   == 'central'
        assert dieta._volume_ml_dia == 2000.0
        assert dieta._velocidade_ml_h == 83.3
        assert 'Glicose' in dieta._composicao

    def test_parenteral_case_insensitive(self, dados_parenteral_validos):
        """Tipo 'PARENTERAL', 'Parenteral', ' parenteral ' devem ser aceitos."""
        assert isinstance(DietaFactory.criar_dieta('PARENTERAL', dados_parenteral_validos), DietaParenteral)
        assert isinstance(DietaFactory.criar_dieta('  Parenteral  ', dados_parenteral_validos), DietaParenteral)

    def test_parenteral_usuario_responsavel_default(self, dados_parenteral_validos):
        """Sem 'usuario_responsavel', deve usar 'sistema'."""
        del dados_parenteral_validos['usuario_responsavel']
        dieta = DietaFactory.criar_dieta('parenteral', dados_parenteral_validos)
        assert dieta._usuario_responsavel == 'sistema'

    def test_parenteral_erro_parametros_faltando(self, dados_parenteral_validos):
        """Deve lançar ValueError se parâmetro obrigatório estiver ausente."""
        del dados_parenteral_validos['composicao']
        with pytest.raises(ValueError, match="Dieta Parenteral exige os seguintes parâmetros"):
            DietaFactory.criar_dieta('parenteral', dados_parenteral_validos)

    def test_parenteral_erro_volume_negativo(self, dados_parenteral_validos):
        """volume_ml_dia <= 0 deve lançar ValueError."""
        dados_parenteral_validos['volume_ml_dia'] = -500.0
        with pytest.raises(ValueError, match="Parâmetro 'volume_ml_dia' inválido"):
            DietaFactory.criar_dieta('parenteral', dados_parenteral_validos)

    def test_parenteral_erro_volume_zero(self, dados_parenteral_validos):
        dados_parenteral_validos['volume_ml_dia'] = 0
        with pytest.raises(ValueError, match="Parâmetro 'volume_ml_dia' inválido"):
            DietaFactory.criar_dieta('parenteral', dados_parenteral_validos)

    def test_parenteral_erro_velocidade_negativa(self, dados_parenteral_validos):
        """velocidade_ml_h <= 0 deve lançar ValueError."""
        dados_parenteral_validos['velocidade_ml_h'] = -10.0
        with pytest.raises(ValueError, match="Parâmetro 'velocidade_ml_h' inválido"):
            DietaFactory.criar_dieta('parenteral', dados_parenteral_validos)

    def test_parenteral_erro_volume_nao_numerico(self, dados_parenteral_validos):
        """volume_ml_dia não numérico deve lançar ValueError."""
        dados_parenteral_validos['volume_ml_dia'] = 'dois litros'
        with pytest.raises(ValueError, match="Parâmetro 'volume_ml_dia' inválido"):
            DietaFactory.criar_dieta('parenteral', dados_parenteral_validos)

    def test_parenteral_erro_tipo_acesso_invalido(self, dados_parenteral_validos):
        """Tipo de acesso fora do conjunto válido deve lançar ValueError."""
        dados_parenteral_validos['tipo_acesso'] = 'subcutaneo'
        with pytest.raises(ValueError):
            DietaFactory.criar_dieta('parenteral', dados_parenteral_validos)

    def test_parenteral_picc_valido(self, dados_parenteral_validos):
        """'picc' é um tipo de acesso válido."""
        dados_parenteral_validos['tipo_acesso'] = 'picc'
        dieta = DietaFactory.criar_dieta('parenteral', dados_parenteral_validos)
        assert dieta._tipo_acesso == 'picc'


# =============================================================================
# TESTES — DietaMista via Factory
# =============================================================================

class TestFactoryMista:

    def test_criar_mista_sucesso(self, dados_mista_validos):
        """Factory deve retornar instância de DietaMista com dados válidos."""
        dieta = DietaFactory.criar_dieta('mista', dados_mista_validos)
        assert isinstance(dieta, DietaMista)

    def test_mista_componentes_adicionados(self, dados_mista_validos):
        """Ambos os componentes devem estar na DietaMista."""
        dieta = DietaFactory.criar_dieta('mista', dados_mista_validos)
        assert dieta.quantidade_componentes == 2

    def test_mista_percentual_total_correto(self, dados_mista_validos):
        """Soma dos percentuais deve ser 100%."""
        dieta = DietaFactory.criar_dieta('mista', dados_mista_validos)
        assert dieta.percentual_total == pytest.approx(100.0)

    def test_mista_esta_valida(self, dados_mista_validos):
        """DietaMista criada com dados corretos deve estar válida."""
        dieta = DietaFactory.criar_dieta('mista', dados_mista_validos)
        assert dieta.esta_valida is True

    def test_mista_case_insensitive(self, dados_mista_validos):
        """Tipo 'MISTA', 'Mista', ' mista ' devem ser aceitos."""
        assert isinstance(DietaFactory.criar_dieta('MISTA', dados_mista_validos), DietaMista)
        assert isinstance(DietaFactory.criar_dieta('  Mista  ', dados_mista_validos), DietaMista)

    def test_mista_usuario_responsavel_default(self, dados_mista_validos):
        """Sem 'usuario_responsavel', deve usar 'sistema'."""
        del dados_mista_validos['usuario_responsavel']
        dieta = DietaFactory.criar_dieta('mista', dados_mista_validos)
        assert dieta._usuario_responsavel == 'sistema'

    def test_mista_descricao_personalizada(self, dados_mista_validos):
        """Descricao passada nos dados deve ser usada."""
        dieta = DietaFactory.criar_dieta('mista', dados_mista_validos)
        assert dieta.descricao == 'Transição oral/enteral'

    def test_mista_descricao_default(self, dados_mista_validos):
        """Sem 'descricao', deve usar 'Dieta Mista'."""
        del dados_mista_validos['descricao']
        dieta = DietaFactory.criar_dieta('mista', dados_mista_validos)
        assert dieta.descricao == 'Dieta Mista'

    def test_mista_erro_sem_componentes(self):
        """Ausência da chave 'componentes' deve lançar ValueError."""
        with pytest.raises(ValueError, match="'componentes'"):
            DietaFactory.criar_dieta('mista', {'descricao': 'sem componentes'})

    def test_mista_erro_componentes_lista_vazia(self):
        """Lista vazia de componentes deve lançar ValueError."""
        with pytest.raises(ValueError, match="lista não vazia"):
            DietaFactory.criar_dieta('mista', {'componentes': []})

    def test_mista_erro_componente_sem_chave_dieta(self, dieta_oral_simples):
        """Componente sem a chave 'dieta' deve lançar ValueError."""
        with pytest.raises(ValueError, match="'dieta'"):
            DietaFactory.criar_dieta('mista', {
                'componentes': [{'percentual': 100.0}]
            })

    def test_mista_erro_componente_sem_chave_percentual(self, dieta_oral_simples):
        """Componente sem a chave 'percentual' deve lançar ValueError."""
        with pytest.raises(ValueError, match="'percentual'"):
            DietaFactory.criar_dieta('mista', {
                'componentes': [{'dieta': dieta_oral_simples}]
            })

    def test_mista_erro_dieta_nao_e_instancia_dieta(self):
        """Componente com 'dieta' inválido deve lançar TypeError."""
        with pytest.raises(TypeError, match="instância de Dieta"):
            DietaFactory.criar_dieta('mista', {
                'componentes': [
                    {'dieta': 'nao_e_dieta', 'percentual': 50.0},
                    {'dieta': 'nao_e_dieta', 'percentual': 50.0},
                ]
            })

    def test_mista_erro_percentual_invalido(self, dieta_oral_simples, dieta_enteral_simples):
        """Percentual fora do intervalo (0, 100] deve lançar ValueError."""
        with pytest.raises(ValueError, match="'percentual'"):
            DietaFactory.criar_dieta('mista', {
                'componentes': [
                    {'dieta': dieta_oral_simples,    'percentual': -10.0},
                    {'dieta': dieta_enteral_simples, 'percentual': 110.0},
                ]
            })

    def test_mista_tres_componentes(self, dieta_oral_simples, dieta_enteral_simples):
        """Deve aceitar até 4 componentes."""
        dieta_parenteral = DietaParenteral(
            tipo_acesso='central',
            volume_ml_dia=500.0,
            composicao='Glicose 50%',
            velocidade_ml_h=20.8,   # ~499.2 ml em 24h
        )
        dieta = DietaFactory.criar_dieta('mista', {
            'componentes': [
                {'dieta': dieta_oral_simples,    'percentual': 50.0},
                {'dieta': dieta_enteral_simples, 'percentual': 30.0},
                {'dieta': dieta_parenteral,      'percentual': 20.0},
            ]
        })
        assert dieta.quantidade_componentes == 3
        assert dieta.percentual_total == pytest.approx(100.0)


# =============================================================================
# TESTES — Mensagem de erro atualizada para tipos inválidos
# =============================================================================

class TestFactoryTipoInvalido:

    def test_tipo_invalido_menciona_todos_os_tipos(self):
        """Mensagem de erro deve listar os 4 tipos válidos."""
        with pytest.raises(ValueError) as exc:
            DietaFactory.criar_dieta('subcutanea', {})
        mensagem = str(exc.value)
        assert 'oral'       in mensagem
        assert 'enteral'    in mensagem
        assert 'parenteral' in mensagem
        assert 'mista'      in mensagem

    def test_tipo_invalido_contem_tipo_informado(self):
        """Mensagem de erro deve incluir o tipo que foi passado."""
        with pytest.raises(ValueError, match="Tipo de dieta desconhecido: 'subcutanea'"):
            DietaFactory.criar_dieta('subcutanea', {})