"""
Testes para UserController.

Cobertura: autenticação (RN08), cadastro com validação de perfil (RN06),
           listagem restrita a admin, alteração de status, unicidade de CPF/e-mail.
"""

import pytest

from src.snh_project.controllers.user_controller import UserController


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def ctrl(tmp_path):
    """Controller usando diretório temporário com usuários padrão do seed."""
    # Cria usuários manualmente já que não há seed aqui
    c = UserController(data_dir=str(tmp_path))
    c.cadastrar_usuario({
        "nome": "Admin Teste", "cpf": "00000000000",
        "email": "admin@test.com", "tipo": "administrador", "senha": "admin123",
    })
    c.cadastrar_usuario({
        "nome": "Dra. Nutri", "cpf": "11111111111",
        "email": "nutri@test.com", "tipo": "nutricionista",
        "senha": "nutri123", "crn": "CRN-001",
    })
    c.cadastrar_usuario({
        "nome": "João Copeiro", "cpf": "22222222222",
        "email": "copeiro@test.com", "tipo": "copeiro",
        "senha": "cop123", "turno": "manha",
    })
    return c


# =============================================================================
# AUTENTICAÇÃO — US16 / RN08
# =============================================================================

class TestAutenticacao:

    def test_login_valido_retorna_dados_usuario(self, ctrl):
        """Login com credenciais corretas deve retornar dados do usuário."""
        resultado = ctrl.autenticar("admin@test.com", "admin123")
        assert resultado is not None
        assert resultado["nome"] == "Admin Teste"
        assert resultado["tipo"] == "administrador"

    def test_login_nao_retorna_senha_hash(self, ctrl):
        """Resposta de autenticação nunca deve expor senha_hash."""
        resultado = ctrl.autenticar("admin@test.com", "admin123")
        assert "senha_hash" not in resultado

    def test_login_senha_errada_retorna_none(self, ctrl):
        """RN08: senha incorreta deve retornar None."""
        assert ctrl.autenticar("admin@test.com", "senha_errada") is None

    def test_login_email_inexistente_retorna_none(self, ctrl):
        """E-mail não cadastrado deve retornar None."""
        assert ctrl.autenticar("naoexiste@test.com", "qualquer") is None

    def test_login_usuario_bloqueado_retorna_none(self, ctrl):
        """Usuário bloqueado não deve conseguir autenticar."""
        usuario = ctrl.autenticar("copeiro@test.com", "cop123")
        ctrl.alterar_status(usuario["id"], "bloqueado", solicitante_tipo="administrador")
        assert ctrl.autenticar("copeiro@test.com", "cop123") is None


# =============================================================================
# CADASTRO — US15 / RN06
# =============================================================================

class TestCadastro:

    def test_cadastrar_nutricionista_com_crn(self, ctrl):
        """Nutricionista deve ser criada com CRN nos dados extras."""
        dados = {
            "nome": "Nova Nutri", "cpf": "33333333333",
            "email": "nova@test.com", "tipo": "nutricionista",
            "senha": "abc123", "crn": "CRN-999",
        }
        resultado = ctrl.cadastrar_usuario(dados)
        assert resultado["tipo"] == "nutricionista"
        assert resultado["dados_extras"]["crn"] == "CRN-999"

    def test_cadastrar_sem_permissao_levanta_erro(self, ctrl):
        """RN06: não-admin não pode cadastrar usuários."""
        with pytest.raises(PermissionError, match="administradores"):
            ctrl.cadastrar_usuario(
                {"nome": "X", "cpf": "99999999999", "email": "x@test.com",
                 "tipo": "copeiro", "senha": "123"},
                solicitante_tipo="copeiro",
            )

    def test_cadastrar_cpf_duplicado_levanta_erro(self, ctrl):
        """CPF já existente deve levantar ValueError."""
        with pytest.raises(ValueError, match="CPF"):
            ctrl.cadastrar_usuario({
                "nome": "Outro Admin", "cpf": "00000000000",
                "email": "outro@test.com", "tipo": "administrador", "senha": "xyz",
            })

    def test_cadastrar_email_duplicado_levanta_erro(self, ctrl):
        """E-mail já existente deve levantar ValueError."""
        with pytest.raises(ValueError, match="E-mail"):
            ctrl.cadastrar_usuario({
                "nome": "Admin2", "cpf": "55555555555",
                "email": "admin@test.com", "tipo": "administrador", "senha": "xyz",
            })

    def test_cadastrar_tipo_invalido_levanta_erro(self, ctrl):
        """Tipo de usuário inválido deve levantar ValueError."""
        with pytest.raises(ValueError, match="inválido"):
            ctrl.cadastrar_usuario({
                "nome": "X", "cpf": "66666666666", "email": "x2@test.com",
                "tipo": "aliens", "senha": "123",
            })

    def test_cadastrar_campo_obrigatorio_faltando(self, ctrl):
        """Campos obrigatórios ausentes devem levantar ValueError."""
        with pytest.raises(ValueError):
            ctrl.cadastrar_usuario({"nome": "Sem Email", "cpf": "77777777777"})


# =============================================================================
# LISTAGEM — US15 / RN06
# =============================================================================

class TestListagem:

    def test_listar_todos_como_admin(self, ctrl):
        """Admin pode listar todos os usuários."""
        lista = ctrl.listar_usuarios(solicitante_tipo="administrador")
        assert len(lista) >= 3

    def test_listar_por_tipo_filtra(self, ctrl):
        """listar_usuarios(tipo=X) deve retornar apenas usuários daquele tipo."""
        lista = ctrl.listar_usuarios(tipo="nutricionista", solicitante_tipo="administrador")
        assert all(u["tipo"] == "nutricionista" for u in lista)

    def test_listar_sem_permissao_levanta_erro(self, ctrl):
        """RN06: copeiro não pode listar usuários."""
        with pytest.raises(PermissionError):
            ctrl.listar_usuarios(solicitante_tipo="copeiro")

    def test_listagem_nao_expoe_senha_hash(self, ctrl):
        """Nenhum item da listagem deve conter senha_hash."""
        lista = ctrl.listar_usuarios(solicitante_tipo="administrador")
        assert all("senha_hash" not in u for u in lista)


# =============================================================================
# STATUS — RN06
# =============================================================================

class TestStatus:

    def test_inativar_usuario(self, ctrl):
        """Administrador pode inativar um usuário."""
        usuario = ctrl.autenticar("copeiro@test.com", "cop123")
        ok = ctrl.alterar_status(usuario["id"], "inativo", solicitante_tipo="administrador")
        assert ok is True
        registro = ctrl.obter_por_id(usuario["id"])
        assert registro["status"] == "inativo"

    def test_status_invalido_levanta_erro(self, ctrl):
        """Status que não existe deve levantar ValueError."""
        usuario = ctrl.autenticar("admin@test.com", "admin123")
        with pytest.raises(ValueError, match="inválido"):
            ctrl.alterar_status(usuario["id"], "cancelado", solicitante_tipo="administrador")

    def test_alterar_status_sem_permissao(self, ctrl):
        """Não-admin não pode alterar status de usuários."""
        usuario = ctrl.autenticar("admin@test.com", "admin123")
        with pytest.raises(PermissionError):
            ctrl.alterar_status(usuario["id"], "inativo", solicitante_tipo="nutricionista")
