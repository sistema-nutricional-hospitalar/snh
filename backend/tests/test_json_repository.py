"""
Testes para JsonRepository — camada de persistência base.

Cobertura: CRUD completo, geração de ID, arquivo inexistente,
           persistência real em disco, busca por campo.
"""

import json
import os
import tempfile

import pytest

from src.snh_project.infrastructure.json_repository import JsonRepository


@pytest.fixture
def repo_tmp():
    """Cria um repositório em arquivo temporário isolado por teste."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        tmp_path = f.name
    yield JsonRepository(tmp_path)
    os.unlink(tmp_path)


@pytest.fixture
def repo_populado(repo_tmp):
    """Repositório com 3 registros pré-inseridos."""
    repo_tmp.save({"id": "id-001", "nome": "Alpha", "tipo": "A"})
    repo_tmp.save({"id": "id-002", "nome": "Beta",  "tipo": "B"})
    repo_tmp.save({"id": "id-003", "nome": "Gama",  "tipo": "A"})
    return repo_tmp


# =============================================================================
# CRIAÇÃO E INICIALIZAÇÃO
# =============================================================================

class TestInicializacao:

    def test_arquivo_criado_automaticamente(self):
        """Repositório cria o arquivo JSON se ele não existir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "subdir", "novo.json")
            repo = JsonRepository(path)
            assert os.path.exists(path)
            assert repo.count() == 0

    def test_arquivo_vazio_retorna_lista_vazia(self, repo_tmp):
        """find_all() em repositório vazio retorna []."""
        assert repo_tmp.find_all() == []

    def test_repr_inclui_nome_classe(self, repo_tmp):
        assert "JsonRepository" in repr(repo_tmp)


# =============================================================================
# SAVE — INSERT E UPDATE
# =============================================================================

class TestSave:

    def test_save_gera_id_automatico(self, repo_tmp):
        """save() sem 'id' no registro deve gerar UUID automaticamente."""
        record = repo_tmp.save({"nome": "Sem ID"})
        assert "id" in record
        assert len(record["id"]) == 36  # UUID v4

    def test_save_insert_persiste_em_disco(self, repo_tmp):
        """Dado salvo deve ser lido corretamente do arquivo JSON."""
        repo_tmp.save({"id": "id-x", "valor": 42})
        raw = json.loads(open(repo_tmp._path).read())
        assert len(raw) == 1
        assert raw[0]["valor"] == 42

    def test_save_update_substitui_registro_existente(self, repo_tmp):
        """save() com ID existente deve atualizar (não duplicar)."""
        repo_tmp.save({"id": "id-1", "status": "pendente"})
        repo_tmp.save({"id": "id-1", "status": "ativo"})
        assert repo_tmp.count() == 1
        assert repo_tmp.find_by_id("id-1")["status"] == "ativo"

    def test_save_multiplos_registros(self, repo_tmp):
        """Múltiplos saves devem acumular registros distintos."""
        for i in range(5):
            repo_tmp.save({"id": f"id-{i}", "seq": i})
        assert repo_tmp.count() == 5


# =============================================================================
# FIND
# =============================================================================

class TestFind:

    def test_find_by_id_existente(self, repo_populado):
        """find_by_id deve retornar o registro correto."""
        r = repo_populado.find_by_id("id-002")
        assert r is not None
        assert r["nome"] == "Beta"

    def test_find_by_id_inexistente_retorna_none(self, repo_populado):
        """find_by_id com ID inválido retorna None."""
        assert repo_populado.find_by_id("nao-existe") is None

    def test_find_all_retorna_todos(self, repo_populado):
        """find_all deve retornar todos os registros inseridos."""
        assert len(repo_populado.find_all()) == 3

    def test_find_all_by_field_filtra_corretamente(self, repo_populado):
        """find_by_field deve retornar apenas os registros com o campo igual."""
        resultado = repo_populado.find_all_by_field("tipo", "A")
        assert len(resultado) == 2
        assert all(r["tipo"] == "A" for r in resultado)

    def test_find_all_by_field_sem_resultado(self, repo_populado):
        """find_by_field sem correspondência retorna lista vazia."""
        assert repo_populado.find_all_by_field("tipo", "Z") == []


# =============================================================================
# DELETE
# =============================================================================

class TestDelete:

    def test_delete_remove_registro(self, repo_populado):
        """delete() deve remover o registro e retornar True."""
        ok = repo_populado.delete("id-001")
        assert ok is True
        assert repo_populado.count() == 2
        assert repo_populado.find_by_id("id-001") is None

    def test_delete_id_inexistente_retorna_false(self, repo_populado):
        """delete() com ID que não existe retorna False sem alterar dados."""
        ok = repo_populado.delete("fantasma")
        assert ok is False
        assert repo_populado.count() == 3

    def test_delete_todos_os_registros(self, repo_populado):
        """Deletar todos os registros deve resultar em repositório vazio."""
        for id_ in ["id-001", "id-002", "id-003"]:
            repo_populado.delete(id_)
        assert repo_populado.count() == 0
        assert repo_populado.find_all() == []
