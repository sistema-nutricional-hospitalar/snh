"""
Testes para NotificationRepository.

Cobertura: salvar notificação, listar não lidas, marcar lida,
           marcar todas lidas, contagem, persistência em disco.
"""

import json
import pytest

from src.snh_project.infrastructure.notification_repository import NotificationRepository


@pytest.fixture
def repo(tmp_path):
    """Repositório de notificações isolado por teste."""
    return NotificationRepository(str(tmp_path / "notifications.json"))


class TestSalvarNotificacao:

    def test_salvar_retorna_registro_com_id(self, repo):
        """salvar_notificacao deve retornar dict com campo 'id' gerado."""
        n = repo.salvar_notificacao("copeiro@h.com", "Dieta alterada")
        assert "id" in n
        assert n["id"] != ""

    def test_salvar_persiste_destinatario_e_mensagem(self, repo):
        """Campos destinatario e mensagem devem ser armazenados corretamente."""
        repo.salvar_notificacao("copeiro@h.com", "Troca de dieta")
        lista = repo.listar_por_destinatario("copeiro@h.com")
        assert lista[0]["destinatario"] == "copeiro@h.com"
        assert lista[0]["mensagem"] == "Troca de dieta"

    def test_salvar_inicia_como_nao_lida(self, repo):
        """Notificação recém-criada deve ter lida=False."""
        n = repo.salvar_notificacao("x@h.com", "msg")
        assert n["lida"] is False

    def test_salvar_prioridade_default_normal(self, repo):
        """Prioridade padrão deve ser 'normal'."""
        n = repo.salvar_notificacao("x@h.com", "msg")
        assert n["prioridade"] == "normal"

    def test_salvar_prioridade_urgente(self, repo):
        """Deve aceitar prioridade 'urgente'."""
        n = repo.salvar_notificacao("x@h.com", "Urgente!", prioridade="urgente")
        assert n["prioridade"] == "urgente"

    def test_salvar_cria_campo_criado_em(self, repo):
        """Campo criado_em deve ser um timestamp ISO."""
        n = repo.salvar_notificacao("x@h.com", "msg")
        assert "criado_em" in n
        assert "T" in n["criado_em"]  # formato ISO: 2024-01-01T00:00:00


class TestListarNaoLidas:

    def test_lista_apenas_nao_lidas(self, repo):
        """listar_nao_lidas deve retornar somente não lidas do destinatário."""
        repo.salvar_notificacao("a@h.com", "msg1")
        repo.salvar_notificacao("a@h.com", "msg2")
        lista = repo.listar_nao_lidas("a@h.com")
        assert len(lista) == 2

    def test_nao_retorna_notificacoes_de_outro_destinatario(self, repo):
        """Não deve vazar notificações entre destinatários diferentes."""
        repo.salvar_notificacao("a@h.com", "msg_a")
        repo.salvar_notificacao("b@h.com", "msg_b")
        assert len(repo.listar_nao_lidas("a@h.com")) == 1
        assert len(repo.listar_nao_lidas("b@h.com")) == 1

    def test_lista_vazia_sem_notificacoes(self, repo):
        """Deve retornar lista vazia se não houver notificações."""
        assert repo.listar_nao_lidas("ninguem@h.com") == []


class TestMarcarLida:

    def test_marcar_lida_retorna_true(self, repo):
        """marcar_lida deve retornar True para ID existente."""
        n = repo.salvar_notificacao("x@h.com", "msg")
        assert repo.marcar_lida(n["id"]) is True

    def test_marcar_lida_remove_das_nao_lidas(self, repo):
        """Após marcar lida, não deve aparecer em listar_nao_lidas."""
        n = repo.salvar_notificacao("x@h.com", "msg")
        repo.marcar_lida(n["id"])
        assert repo.listar_nao_lidas("x@h.com") == []

    def test_marcar_lida_id_inexistente_retorna_false(self, repo):
        """marcar_lida deve retornar False para ID inexistente."""
        assert repo.marcar_lida("id-que-nao-existe") is False

    def test_marcar_todas_lidas_retorna_quantidade(self, repo):
        """marcar_todas_lidas deve retornar o número de notificações marcadas."""
        repo.salvar_notificacao("z@h.com", "a")
        repo.salvar_notificacao("z@h.com", "b")
        repo.salvar_notificacao("z@h.com", "c")
        qtd = repo.marcar_todas_lidas("z@h.com")
        assert qtd == 3

    def test_marcar_todas_lidas_nao_afeta_outro_destinatario(self, repo):
        """marcar_todas_lidas não deve tocar notificações de outro destinatário."""
        repo.salvar_notificacao("a@h.com", "msg_a")
        repo.salvar_notificacao("b@h.com", "msg_b")
        repo.marcar_todas_lidas("a@h.com")
        # b ainda tem 1 não lida
        assert repo.contar_nao_lidas("b@h.com") == 1


class TestContar:

    def test_contar_nao_lidas_zero_inicial(self, repo):
        """Sem notificações, contagem deve ser 0."""
        assert repo.contar_nao_lidas("x@h.com") == 0

    def test_contar_nao_lidas_incrementa(self, repo):
        """Contagem deve refletir o número de não lidas."""
        repo.salvar_notificacao("x@h.com", "a")
        repo.salvar_notificacao("x@h.com", "b")
        assert repo.contar_nao_lidas("x@h.com") == 2

    def test_contar_diminui_apos_marcar(self, repo):
        """Após marcar como lida, contagem deve diminuir."""
        n = repo.salvar_notificacao("x@h.com", "msg")
        repo.marcar_lida(n["id"])
        assert repo.contar_nao_lidas("x@h.com") == 0


class TestPersistencia:

    def test_notificacoes_persistidas_em_disco(self, tmp_path):
        """Notificações devem sobreviver a uma nova instância do repositório."""
        caminho = str(tmp_path / "notif.json")
        repo1 = NotificationRepository(caminho)
        repo1.salvar_notificacao("x@h.com", "persistida")

        repo2 = NotificationRepository(caminho)
        lista = repo2.listar_nao_lidas("x@h.com")
        assert len(lista) == 1
        assert lista[0]["mensagem"] == "persistida"
