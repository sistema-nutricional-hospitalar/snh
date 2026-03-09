"""
Testes para NotificacaoInApp.

Cobertura: envio com persistência, obter notificações não lidas,
           marcar lidas, integração com NotificationRepository.

Inclui 2 testes com MagicMock para isolar o repositório de persistência.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.snh_project.services.strategies import NotificacaoInApp, EstrategiaNotificacao


@pytest.fixture
def inapp(tmp_path):
    """NotificacaoInApp com diretório temporário isolado."""
    return NotificacaoInApp(data_dir=str(tmp_path))


class TestContrato:

    def test_e_instancia_de_estrategia_notificacao(self, inapp):
        """NotificacaoInApp deve respeitar o contrato de EstrategiaNotificacao (LSP)."""
        assert isinstance(inapp, EstrategiaNotificacao)

    def test_enviar_retorna_true_em_sucesso(self, inapp):
        """enviar() deve retornar True quando o repositório aceitar."""
        resultado = inapp.enviar("Dieta alterada", "copeiro@h.com")
        assert resultado is True

    def test_enviar_retorna_false_quando_repo_falha(self, tmp_path):
        """enviar() deve retornar False sem lançar exceção quando repositório falha (mock)."""
        inapp = NotificacaoInApp(data_dir=str(tmp_path))
        # Substitui o repositório por um mock que lança exceção
        inapp._repo = MagicMock()
        inapp._repo.salvar_notificacao.side_effect = OSError("disco cheio")

        resultado = inapp.enviar("msg", "x@h.com")
        assert resultado is False


class TestPersistencia:

    def test_obter_notificacoes_retorna_nao_lidas(self, inapp):
        """obter_notificacoes deve retornar as notificações não lidas."""
        inapp.enviar("msg1", "copeiro@h.com")
        inapp.enviar("msg2", "copeiro@h.com")
        lista = inapp.obter_notificacoes("copeiro@h.com")
        assert len(lista) == 2

    def test_obter_notificacoes_nao_vaza_entre_destinatarios(self, inapp):
        """Notificações de destinatários distintos não devem se misturar."""
        inapp.enviar("para A", "a@h.com")
        inapp.enviar("para B", "b@h.com")
        assert len(inapp.obter_notificacoes("a@h.com")) == 1
        assert len(inapp.obter_notificacoes("b@h.com")) == 1

    def test_marcar_lida_remove_das_nao_lidas(self, inapp):
        """Após marcar_lida, obter_notificacoes não deve mais retornar a notificação."""
        inapp.enviar("teste", "x@h.com")
        inapp.marcar_lida("x@h.com")
        assert inapp.obter_notificacoes("x@h.com") == []

    def test_marcar_lida_retorna_quantidade(self, inapp):
        """marcar_lida deve retornar o número de notificações marcadas."""
        inapp.enviar("a", "x@h.com")
        inapp.enviar("b", "x@h.com")
        qtd = inapp.marcar_lida("x@h.com")
        assert qtd == 2


class TestMockRepositorio:

    def test_enviar_chama_repositorio_com_parametros_corretos(self, tmp_path):
        """Verifica que enviar() repassa mensagem e destinatário ao repositório (mock)."""
        inapp = NotificacaoInApp(data_dir=str(tmp_path))
        mock_repo = MagicMock()
        mock_repo.salvar_notificacao.return_value = {"id": "fake-id", "lida": False}
        inapp._repo = mock_repo

        inapp.enviar("Dieta de oral para pastosa", "copeiro@hospital.com", prioridade="urgente")

        mock_repo.salvar_notificacao.assert_called_once_with(
            destinatario="copeiro@hospital.com",
            mensagem="Dieta de oral para pastosa",
            prioridade="urgente",
        )

    def test_enviar_polimorfismo_na_lista(self, tmp_path):
        """Itera sobre lista de estratégias distintas chamando o mesmo método (polimorfismo)."""
        from src.snh_project.services.strategies import NotificacaoEmail, NotificacaoPush

        estrategias = [
            NotificacaoEmail(),
            NotificacaoPush(),
            NotificacaoInApp(data_dir=str(tmp_path)),
        ]

        resultados = [e.enviar("Teste polimórfico", "dest") for e in estrategias]
        # Todas devem retornar True (contrato da interface)
        assert all(resultados)
