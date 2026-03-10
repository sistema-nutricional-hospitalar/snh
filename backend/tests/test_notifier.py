import pytest
from unittest.mock import MagicMock
from src.snh_project.services.notifier import NotificadorService
from src.snh_project.services.strategies import NotificacaoEmail, EstrategiaNotificacao

# --- Fixtures ---
@pytest.fixture
def servico():
    return NotificadorService()

@pytest.fixture
def estrategia_email():
    return NotificacaoEmail()

# --- Testes de Registro e Gerenciamento (Happy Path) ---

def test_registrar_observador_sucesso(servico, estrategia_email):
    """Testa se consegue registrar um canal corretamente."""
    destinatarios = ["admin@hospital.com", "nutri@hospital.com"]
    servico.registrar_observador("email_admin", estrategia_email, destinatarios)
    
    assert servico.total_observadores == 1
    assert "email_admin" in servico.listar_canais_ativos()
    assert len(servico.obter_destinatarios("email_admin")) == 2

def test_remover_observador(servico, estrategia_email):
    """Testa a remoção de um canal existente."""
    servico.registrar_observador("email_temp", estrategia_email, ["teste@teste.com"])
    assert servico.total_observadores == 1
    removido = servico.remover_observador("email_temp")
    assert removido is True
    assert servico.total_observadores == 0

def test_remover_observador_inexistente(servico):
    removido = servico.remover_observador("canal_fantasma")
    assert removido is False

# --- Testes de Validação e Edge Cases ---

def test_erro_registrar_estrategia_invalida(servico):
    with pytest.raises(TypeError, match="Estratégia deve implementar EstrategiaNotificacao"):
        servico.registrar_observador("erro", "Isso não é uma classe", ["a@b.com"])

def test_erro_canal_vazio(servico, estrategia_email):
    with pytest.raises(ValueError, match="Nome do canal não pode ser vazio"):
        servico.registrar_observador("", estrategia_email, ["a@b.com"])

def test_erro_destinatarios_vazios(servico, estrategia_email):
    with pytest.raises(ValueError, match="precisa de ao menos um destinatário"):
        servico.registrar_observador("email", estrategia_email, [])

def test_erro_destinatario_invalido_na_lista(servico, estrategia_email):
    """Testa se um item inválido dentro da lista de destinatários gera erro."""
    destinatarios_mistos = ["email@ok.com", 12345] # Número inválido
    with pytest.raises(ValueError, match="Destinatário inválido no canal"):
        servico.registrar_observador("canal_misto", estrategia_email, destinatarios_mistos)

def test_obter_destinatarios_canal_inexistente(servico):
    """Testa se retorna lista vazia para canal que não existe."""
    lista = servico.obter_destinatarios("canal_fantasma")
    assert lista == []

def test_repr_notifier(servico):
    """Garante que o __repr__ não quebra."""
    assert "NotificadorService" in repr(servico)

# --- Testes com MOCK (Requisito 8.1 - OBRIGATÓRIO) ---

def test_notificar_sucesso_com_mock(servico):
    """Testa o fluxo de notificação usando um MOCK."""
    mock_estrategia = MagicMock(spec=EstrategiaNotificacao)
    mock_estrategia.enviar.return_value = True 
    
    destinatarios = ["user1", "user2"]
    servico.registrar_observador("mock_channel", mock_estrategia, destinatarios)
    
    resultado = servico.notificar_mudanca(123, "Mudança de Dieta")
    
    assert resultado['total_enviados'] == 2
    assert resultado['sucessos'] == 2
    assert resultado['falhas'] == 0
    assert mock_estrategia.enviar.call_count == 2

def test_notificar_tratamento_de_erro_com_mock(servico):
    """Testa robustez quando estratégia lança exceção."""
    mock_estrategia_quebrada = MagicMock(spec=EstrategiaNotificacao)
    mock_estrategia_quebrada.enviar.side_effect = Exception("Servidor offline")
    
    servico.registrar_observador("canal_quebrado", mock_estrategia_quebrada, ["user_azarado"])
    
    resultado = servico.notificar_mudanca(999, "Teste de Erro")
    
    assert resultado['total_enviados'] == 1
    assert resultado['sucessos'] == 0
    assert resultado['falhas'] == 1 

def test_notificacao_falha_silenciosa(servico):
    """Testa quando a estratégia retorna False (falha de envio sem quebrar o sistema)."""
    mock_estrategia = MagicMock(spec=EstrategiaNotificacao)
    mock_estrategia.enviar.return_value = False 
    
    servico.registrar_observador("canal_falho", mock_estrategia, ["user"])
    resultado = servico.notificar_mudanca(1, "Teste")
    
    assert resultado['falhas'] == 1
    assert resultado['sucessos'] == 0