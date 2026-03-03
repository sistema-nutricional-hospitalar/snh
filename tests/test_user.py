"""
Testes para a hierarquia de usuários do SNH.

Cobre: enums, validações do construtor, properties,
       métodos concretos (ativar/inativar/bloquear/registrar_acesso),
       polimorfismo dos métodos abstratos e GerenciadorUsuarios.
"""
import pytest
from datetime import datetime

from src.snh_project.core.user import (
    TipoUsuario,
    StatusUsuario,
    Nutricionista,
    Medico,
    Enfermeiro,
    Copeiro,
    Administrador,
    GerenciadorUsuarios,
)


# ===========================================================================
# FIXTURES
# ===========================================================================

@pytest.fixture
def nutricionista():
    return Nutricionista(
        nome="Ana Lima",
        cpf="12345678901",
        email="ana.lima@hospital.com",
        crn="CRN-3/12345",
    )


@pytest.fixture
def medico():
    return Medico(
        nome="Dr. Carlos Souza",
        cpf="98765432100",
        email="carlos.souza@hospital.com",
        crm="CRM-SP-98765",
        especialidade="Clínica Geral",
    )


@pytest.fixture
def enfermeiro():
    return Enfermeiro(
        nome="Beatriz Costa",
        cpf="11122233344",
        email="beatriz.costa@hospital.com",
        coren="COREN-SP-55555",
        setor="UTI",
    )


@pytest.fixture
def copeiro():
    return Copeiro(
        nome="João Mendes",
        cpf="55566677788",
        email="joao.mendes@hospital.com",
        turno="manhã",
    )


@pytest.fixture
def administrador():
    return Administrador(
        nome="Maria Admin",
        cpf="99988877766",
        email="maria.admin@hospital.com",
    )


@pytest.fixture
def gerenciador():
    return GerenciadorUsuarios()


# ===========================================================================
# TESTES DOS ENUMS
# ===========================================================================

class TestEnums:
    """Testa os valores dos enums TipoUsuario e StatusUsuario."""

    def test_tipo_usuario_valores(self):
        assert TipoUsuario.ADMINISTRADOR.value  == "administrador"
        assert TipoUsuario.MEDICO.value         == "medico"
        assert TipoUsuario.NUTRICIONISTA.value  == "nutricionista"
        assert TipoUsuario.ENFERMEIRO.value     == "enfermeiro"
        assert TipoUsuario.COPEIRO.value        == "copeiro"

    def test_status_usuario_valores(self):
        assert StatusUsuario.ATIVO.value     == "ativo"
        assert StatusUsuario.INATIVO.value   == "inativo"
        assert StatusUsuario.BLOQUEADO.value == "bloqueado"


# ===========================================================================
# TESTES DE VALIDAÇÃO NO CONSTRUTOR
# ===========================================================================

class TestValidacoesConstrutor:
    """Testa as validações na criação de usuários."""

    def test_nome_vazio_levanta_erro(self):
        with pytest.raises(ValueError, match="Nome do usuário não pode ser vazio"):
            Nutricionista(nome="", cpf="12345678901", email="a@b.com", crn="CRN-1")

    def test_nome_apenas_espacos_levanta_erro(self):
        with pytest.raises(ValueError, match="Nome do usuário não pode ser vazio"):
            Medico(nome="   ", cpf="12345678901", email="a@b.com",
                   crm="CRM-1", especialidade="Geral")

    def test_cpf_com_menos_de_11_digitos_levanta_erro(self):
        with pytest.raises(ValueError, match="CPF deve conter exatamente 11 dígitos"):
            Copeiro(nome="X", cpf="1234567890", email="x@x.com", turno="manhã")

    def test_cpf_com_mais_de_11_digitos_levanta_erro(self):
        with pytest.raises(ValueError, match="CPF deve conter exatamente 11 dígitos"):
            Copeiro(nome="X", cpf="123456789012", email="x@x.com", turno="manhã")

    def test_cpf_com_formatacao_aceito(self):
        """CPF com pontos e traço deve ser aceito e armazenado limpo."""
        u = Copeiro(nome="X", cpf="123.456.789-01", email="x@x.com", turno="tarde")
        assert u.cpf == "12345678901"

    def test_email_sem_arroba_levanta_erro(self):
        with pytest.raises(ValueError, match="E-mail inválido"):
            Administrador(nome="X", cpf="12345678901", email="invalido.com")

    def test_email_sem_ponto_levanta_erro(self):
        with pytest.raises(ValueError, match="E-mail inválido"):
            Administrador(nome="X", cpf="12345678901", email="invalido@com")

    def test_tipo_invalido_levanta_tipo_error(self):
        """Passar string em vez de enum deve levantar TypeError."""
        with pytest.raises(TypeError, match="tipo deve ser TipoUsuario"):
            # Força chamada ao __init__ do Usuario via subclasse "fake"
            # O caminho mais direto é verificar que o construtor de Usuario
            # valida corretamente — instanciar subclasse com super() errado.
            # Aqui usamos Nutricionista e monkey-patch apenas para testar
            # a lógica do pai sem criar nova subclasse concreta.
            from src.snh_project.core.user import Usuario, TipoUsuario
            class _Fake(Usuario):
                def pode_prescrever_dieta(self): return False
                def pode_alterar_prescricao(self): return False
                def pode_visualizar_prescricoes(self): return False
            _Fake("Nome", "12345678901", "a@b.com", "nao_e_enum")

    def test_crn_vazio_levanta_erro(self):
        with pytest.raises(ValueError, match="CRN do nutricionista não pode ser vazio"):
            Nutricionista(nome="X", cpf="12345678901", email="a@b.com", crn="")

    def test_crm_vazio_levanta_erro(self):
        with pytest.raises(ValueError, match="CRM do médico não pode ser vazio"):
            Medico(nome="X", cpf="12345678901", email="a@b.com",
                   crm="", especialidade="Geral")


# ===========================================================================
# TESTES DE PROPERTIES
# ===========================================================================

class TestProperties:
    """Testa que as properties retornam os valores corretos."""

    def test_nutricionista_properties(self, nutricionista):
        assert nutricionista.nome   == "Ana Lima"
        assert nutricionista.cpf    == "12345678901"
        assert nutricionista.email  == "ana.lima@hospital.com"
        assert nutricionista.crn    == "CRN-3/12345"
        assert nutricionista.tipo   == TipoUsuario.NUTRICIONISTA
        assert nutricionista.status == StatusUsuario.ATIVO

    def test_medico_properties(self, medico):
        assert medico.crm          == "CRM-SP-98765"
        assert medico.especialidade == "Clínica Geral"
        assert medico.tipo         == TipoUsuario.MEDICO

    def test_enfermeiro_properties(self, enfermeiro):
        assert enfermeiro.coren == "COREN-SP-55555"
        assert enfermeiro.setor == "UTI"
        assert enfermeiro.tipo  == TipoUsuario.ENFERMEIRO

    def test_copeiro_properties(self, copeiro):
        assert copeiro.turno == "manhã"
        assert copeiro.tipo  == TipoUsuario.COPEIRO

    def test_administrador_tipo(self, administrador):
        assert administrador.tipo == TipoUsuario.ADMINISTRADOR

    def test_ultimo_acesso_none_inicialmente(self, nutricionista):
        assert nutricionista.ultimo_acesso is None

    def test_data_cadastro_e_datetime(self, medico):
        assert isinstance(medico.data_cadastro, datetime)


# ===========================================================================
# TESTES DE MÉTODOS CONCRETOS
# ===========================================================================

class TestMetodosConcretos:
    """Testa registrar_acesso, ativar, inativar e bloquear."""

    def test_registrar_acesso_atualiza_ultimo_acesso(self, nutricionista):
        assert nutricionista.ultimo_acesso is None
        nutricionista.registrar_acesso()
        assert isinstance(nutricionista.ultimo_acesso, datetime)

    def test_registrar_acesso_atualiza_a_cada_chamada(self, medico):
        medico.registrar_acesso()
        primeiro = medico.ultimo_acesso
        medico.registrar_acesso()
        assert medico.ultimo_acesso >= primeiro

    def test_inativar_usuario_ativo(self, copeiro):
        assert copeiro.status == StatusUsuario.ATIVO
        copeiro.inativar()
        assert copeiro.status == StatusUsuario.INATIVO

    def test_ativar_usuario_inativo(self, copeiro):
        copeiro.inativar()
        copeiro.ativar()
        assert copeiro.status == StatusUsuario.ATIVO

    def test_bloquear_usuario(self, enfermeiro):
        enfermeiro.bloquear()
        assert enfermeiro.status == StatusUsuario.BLOQUEADO

    def test_ativar_usuario_ja_ativo_levanta_erro(self, nutricionista):
        with pytest.raises(ValueError, match="já está ativo"):
            nutricionista.ativar()

    def test_inativar_usuario_ja_inativo_levanta_erro(self, medico):
        medico.inativar()
        with pytest.raises(ValueError, match="já está inativo"):
            medico.inativar()

    def test_bloquear_usuario_ja_bloqueado_levanta_erro(self, administrador):
        administrador.bloquear()
        with pytest.raises(ValueError, match="já está bloqueado"):
            administrador.bloquear()

    def test_inativar_atualiza_timestamp_auditoria(self, enfermeiro):
        antes = enfermeiro.atualizado_em
        enfermeiro.inativar()
        assert enfermeiro.atualizado_em >= antes


# ===========================================================================
# TESTES DE POLIMORFISMO (permissões)
# ===========================================================================

class TestPolimorfismoPermissoes:
    """Verifica as permissões de cada tipo de usuário."""

    def test_nutricionista_pode_tudo(self, nutricionista):
        assert nutricionista.pode_prescrever_dieta()     is True
        assert nutricionista.pode_alterar_prescricao()   is True
        assert nutricionista.pode_visualizar_prescricoes() is True

    def test_medico_pode_tudo(self, medico):
        assert medico.pode_prescrever_dieta()     is True
        assert medico.pode_alterar_prescricao()   is True
        assert medico.pode_visualizar_prescricoes() is True

    def test_enfermeiro_so_visualiza(self, enfermeiro):
        assert enfermeiro.pode_prescrever_dieta()     is False
        assert enfermeiro.pode_alterar_prescricao()   is False
        assert enfermeiro.pode_visualizar_prescricoes() is True

    def test_copeiro_so_visualiza(self, copeiro):
        assert copeiro.pode_prescrever_dieta()     is False
        assert copeiro.pode_alterar_prescricao()   is False
        assert copeiro.pode_visualizar_prescricoes() is True

    def test_administrador_nao_prescreve_mas_altera_e_visualiza(self, administrador):
        assert administrador.pode_prescrever_dieta()     is False
        assert administrador.pode_alterar_prescricao()   is True
        assert administrador.pode_visualizar_prescricoes() is True


# ===========================================================================
# TESTES DO GERENCIADOR DE USUÁRIOS
# ===========================================================================

class TestGerenciadorUsuarios:
    """Testa o repositório de usuários."""

    def test_cadastrar_usuario_retorna_true(self, gerenciador, nutricionista):
        assert gerenciador.cadastrar_usuario(nutricionista) is True

    def test_buscar_por_cpf_encontra_usuario(self, gerenciador, medico):
        gerenciador.cadastrar_usuario(medico)
        encontrado = gerenciador.buscar_por_cpf("98765432100")
        assert encontrado is medico

    def test_buscar_por_cpf_formatado_encontra_usuario(self, gerenciador, medico):
        """CPF com pontos/traço também deve funcionar na busca."""
        gerenciador.cadastrar_usuario(medico)
        encontrado = gerenciador.buscar_por_cpf("987.654.321-00")
        assert encontrado is medico

    def test_buscar_por_cpf_inexistente_retorna_none(self, gerenciador):
        assert gerenciador.buscar_por_cpf("00000000000") is None

    def test_buscar_por_email_encontra_usuario(self, gerenciador, enfermeiro):
        gerenciador.cadastrar_usuario(enfermeiro)
        encontrado = gerenciador.buscar_por_email("beatriz.costa@hospital.com")
        assert encontrado is enfermeiro

    def test_buscar_por_email_inexistente_retorna_none(self, gerenciador):
        assert gerenciador.buscar_por_email("ninguem@hospital.com") is None

    def test_cpf_duplicado_levanta_erro(self, gerenciador, nutricionista):
        gerenciador.cadastrar_usuario(nutricionista)
        duplicado = Nutricionista(
            nome="Outra Ana",
            cpf="12345678901",  # mesmo CPF
            email="outra@hospital.com",
            crn="CRN-3/99999",
        )
        with pytest.raises(ValueError, match="CPF '12345678901' já está cadastrado"):
            gerenciador.cadastrar_usuario(duplicado)

    def test_email_duplicado_levanta_erro(self, gerenciador, nutricionista):
        gerenciador.cadastrar_usuario(nutricionista)
        duplicado = Nutricionista(
            nome="Ana Diferente",
            cpf="00011122233",  # CPF diferente
            email="ana.lima@hospital.com",  # mesmo e-mail
            crn="CRN-3/77777",
        )
        with pytest.raises(ValueError, match="E-mail 'ana.lima@hospital.com' já está cadastrado"):
            gerenciador.cadastrar_usuario(duplicado)

    def test_tipo_invalido_levanta_tipo_error(self, gerenciador):
        with pytest.raises(TypeError, match="usuario deve ser instância de Usuario"):
            gerenciador.cadastrar_usuario("não sou um usuario")

    def test_listar_por_tipo(self, gerenciador, nutricionista, medico, enfermeiro):
        gerenciador.cadastrar_usuario(nutricionista)
        gerenciador.cadastrar_usuario(medico)
        gerenciador.cadastrar_usuario(enfermeiro)

        nutris    = gerenciador.listar_por_tipo(TipoUsuario.NUTRICIONISTA)
        medicos   = gerenciador.listar_por_tipo(TipoUsuario.MEDICO)
        enfs      = gerenciador.listar_por_tipo(TipoUsuario.ENFERMEIRO)
        admins    = gerenciador.listar_por_tipo(TipoUsuario.ADMINISTRADOR)

        assert len(nutris)  == 1
        assert len(medicos) == 1
        assert len(enfs)    == 1
        assert len(admins)  == 0

    def test_listar_todos(self, gerenciador, nutricionista, medico, copeiro):
        gerenciador.cadastrar_usuario(nutricionista)
        gerenciador.cadastrar_usuario(medico)
        gerenciador.cadastrar_usuario(copeiro)
        assert len(gerenciador.listar_todos()) == 3

    def test_listar_todos_vazio(self, gerenciador):
        assert gerenciador.listar_todos() == []


# ===========================================================================
# TESTE DE __repr__
# ===========================================================================

class TestRepr:
    """Verifica que __repr__ retorna string com informações essenciais."""

    def test_repr_contem_tipo_e_status(self, nutricionista):
        r = repr(nutricionista)
        assert "Nutricionista" in r
        assert "nutricionista" in r
        assert "ativo"         in r

    def test_repr_contem_nome(self, medico):
        assert "Dr. Carlos Souza" in repr(medico)