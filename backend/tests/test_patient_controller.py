"""
Testes para PatientController.

Cobertura: cadastro válido, campos obrigatórios (RN01), listagem por setor,
           edição, exclusão com confirmação (RN04), busca por nome.
"""

import tempfile
import os

import pytest

from src.snh_project.controllers.patient_controller import PatientController


@pytest.fixture
def ctrl(tmp_path):
    """Controller usando diretório temporário isolado."""
    return PatientController(data_dir=str(tmp_path))


@pytest.fixture
def dados_validos():
    return {
        "nome": "Maria Oliveira",
        "data_nasc": "1985-03-15",
        "setor_nome": "Enfermaria Geral",
        "leito": 4,
        "data_internacao": "2024-06-01T08:00:00",
        "risco": False,
    }


@pytest.fixture
def paciente_cadastrado(ctrl, dados_validos):
    """Paciente já persistido, disponível nos testes que precisam de um ID."""
    return ctrl.cadastrar(dados_validos)


# =============================================================================
# CADASTRO — US01 / RN01
# =============================================================================

class TestCadastro:

    def test_cadastrar_paciente_retorna_id(self, ctrl, dados_validos):
        """Cadastro bem-sucedido deve retornar dicionário com 'id' gerado."""
        resultado = ctrl.cadastrar(dados_validos)
        assert "id" in resultado
        assert len(resultado["id"]) == 36

    def test_cadastrar_persiste_dados_corretos(self, ctrl, dados_validos):
        """Dados informados devem ser preservados na persistência."""
        resultado = ctrl.cadastrar(dados_validos)
        assert resultado["nome"] == "Maria Oliveira"
        assert resultado["leito"] == 4
        assert resultado["setor_nome"] == "Enfermaria Geral"

    def test_cadastrar_campo_nome_faltando_levanta_erro(self, ctrl, dados_validos):
        """RN01: campo obrigatório ausente deve levantar ValueError."""
        del dados_validos["nome"]
        with pytest.raises(ValueError, match="nome"):
            ctrl.cadastrar(dados_validos)

    def test_cadastrar_campo_leito_faltando_levanta_erro(self, ctrl, dados_validos):
        """RN01: leito é campo obrigatório."""
        del dados_validos["leito"]
        with pytest.raises(ValueError, match="leito"):
            ctrl.cadastrar(dados_validos)

    def test_cadastrar_campo_setor_faltando_levanta_erro(self, ctrl, dados_validos):
        """RN01: setor é campo obrigatório."""
        del dados_validos["setor_nome"]
        with pytest.raises(ValueError, match="setor_nome"):
            ctrl.cadastrar(dados_validos)

    def test_cadastrar_cria_setor_automaticamente(self, ctrl, dados_validos):
        """Setor informado deve ser criado automaticamente se não existir."""
        dados_validos["setor_nome"] = "Setor Novo XYZ"
        resultado = ctrl.cadastrar(dados_validos)
        assert resultado["setor_nome"] == "Setor Novo XYZ"

    def test_cadastrar_leito_ja_ocupado_levanta_erro(self, ctrl, dados_validos):
        """Dois pacientes não podem ocupar o mesmo leito no mesmo setor."""
        ctrl.cadastrar(dados_validos)
        dados_duplicados = {**dados_validos, "nome": "Outro Paciente"}
        with pytest.raises(ValueError):
            ctrl.cadastrar(dados_duplicados)


# =============================================================================
# LISTAGEM — US02
# =============================================================================

class TestListagem:

    def test_listar_todos_retorna_pacientes(self, ctrl, dados_validos):
        """listar() sem filtro deve retornar todos os pacientes."""
        ctrl.cadastrar(dados_validos)
        lista = ctrl.listar()
        assert len(lista) == 1
        assert lista[0]["nome"] == "Maria Oliveira"

    def test_listar_por_setor_filtra_corretamente(self, ctrl, dados_validos):
        """listar(setor_nome=X) deve retornar apenas pacientes daquele setor."""
        ctrl.cadastrar(dados_validos)
        ctrl.cadastrar({**dados_validos, "nome": "João UTI", "setor_nome": "UTI", "leito": 10})

        resultado = ctrl.listar(setor_nome="Enfermaria Geral")
        assert len(resultado) == 1
        assert resultado[0]["nome"] == "Maria Oliveira"

    def test_listar_setor_inexistente_retorna_vazio(self, ctrl):
        """listar() com setor que não existe deve retornar lista vazia."""
        assert ctrl.listar(setor_nome="Setor Fantasma") == []

    def test_listar_inclui_setor_nome(self, ctrl, dados_validos):
        """Cada item da listagem deve incluir 'setor_nome' enriquecido."""
        ctrl.cadastrar(dados_validos)
        lista = ctrl.listar()
        assert "setor_nome" in lista[0]

    def test_buscar_por_nome_parcial(self, ctrl, dados_validos):
        """buscar_por_nome deve encontrar paciente por substring do nome."""
        ctrl.cadastrar(dados_validos)
        resultado = ctrl.buscar_por_nome("Maria")
        assert len(resultado) == 1
        assert "Maria" in resultado[0]["nome"]

    def test_buscar_por_nome_sem_resultado(self, ctrl):
        """buscar_por_nome sem correspondência retorna lista vazia."""
        assert ctrl.buscar_por_nome("Zzzz") == []


# =============================================================================
# EDIÇÃO — US03
# =============================================================================

class TestEdicao:

    def test_editar_nome_atualiza_corretamente(self, ctrl, paciente_cadastrado):
        """Editar o nome deve persistir o novo valor."""
        pid = paciente_cadastrado["id"]
        ctrl.editar(pid, {"nome": "Maria Silva Atualizada"})
        atualizado = ctrl.obter_por_id(pid)
        assert atualizado["nome"] == "Maria Silva Atualizada"

    def test_editar_risco_atualiza_corretamente(self, ctrl, paciente_cadastrado):
        """Editar risco deve persistir o novo booleano."""
        pid = paciente_cadastrado["id"]
        ctrl.editar(pid, {"risco": True})
        assert ctrl.obter_por_id(pid)["risco"] is True

    def test_editar_paciente_inexistente_retorna_none(self, ctrl):
        """editar() com ID inválido deve retornar None."""
        assert ctrl.editar("id-fantasma", {"nome": "X"}) is None

    def test_editar_sem_campos_nao_altera_nada(self, ctrl, paciente_cadastrado):
        """editar() com dicionário vazio não deve falhar."""
        pid = paciente_cadastrado["id"]
        resultado = ctrl.editar(pid, {})
        assert resultado is not None


# =============================================================================
# EXCLUSÃO — US03 / RN04
# =============================================================================

class TestExclusao:

    def test_excluir_sem_confirmacao_retorna_aviso(self, ctrl, paciente_cadastrado):
        """RN04: excluir sem confirmar=True deve retornar motivo de confirmação."""
        pid = paciente_cadastrado["id"]
        resultado = ctrl.excluir(pid, confirmar=False)
        assert resultado["sucesso"] is False
        assert resultado["motivo"] == "confirmacao_necessaria"

    def test_excluir_com_confirmacao_remove_paciente(self, ctrl, paciente_cadastrado):
        """excluir(confirmar=True) deve remover o paciente."""
        pid = paciente_cadastrado["id"]
        resultado = ctrl.excluir(pid, confirmar=True)
        assert resultado["sucesso"] is True
        assert ctrl.obter_por_id(pid) is None

    def test_excluir_id_inexistente_retorna_nao_encontrado(self, ctrl):
        """excluir() com ID que não existe deve retornar motivo nao_encontrado."""
        resultado = ctrl.excluir("id-fantasma", confirmar=True)
        assert resultado["sucesso"] is False
        assert resultado["motivo"] == "nao_encontrado"

    def test_paciente_removido_nao_aparece_na_listagem(self, ctrl, paciente_cadastrado):
        """Após exclusão, paciente não deve aparecer em listar()."""
        pid = paciente_cadastrado["id"]
        ctrl.excluir(pid, confirmar=True)
        assert ctrl.listar() == []
