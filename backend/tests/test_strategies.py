import pytest
from src.snh_project.services.strategies import (
    EstrategiaNotificacao, 
    NotificacaoEmail, 
    NotificacaoPush
)

# --- Testes de Abstração (Regra 3.1) ---

def test_nao_pode_instanciar_classe_abstrata():
    """
    Prova que a classe base 'EstrategiaNotificacao' é realmente abstrata.
    O Python deve impedir a criação de um objeto direto dela.
    """
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        # Tentar criar a estratégia genérica deve falhar
        _ = EstrategiaNotificacao()

# --- Testes de Polimorfismo e Comportamento (Regra 3.3) ---

def test_estrategia_email_envia_corretamente(capsys):
    """
    Testa se a estratégia de Email processa a mensagem corretamente.
    Usa 'capsys' do pytest para capturar o print do console.
    """
    # 1. Instancia a estratégia concreta
    estrategia = NotificacaoEmail()
    
    # 2. Verifica herança (prova de polimorfismo)
    assert isinstance(estrategia, EstrategiaNotificacao)
    
    # 3. Executa o método
    resultado = estrategia.enviar("Olá Paciente", "paciente@email.com")
    
    # 4. Captura o que foi 'impresso' no terminal
    captured = capsys.readouterr()
    
    # 5. Validações
    assert resultado is True
    assert "[EMAIL]" in captured.out
    assert "paciente@email.com" in captured.out
    assert "Olá Paciente" in captured.out

def test_estrategia_push_envia_corretamente(capsys):
    """
    Testa se a estratégia de Push processa a mensagem corretamente.
    Observe como o método chamado é o mesmo (.enviar), mas o resultado (print) é diferente.
    """
    # 1. Instancia a estratégia concreta
    estrategia = NotificacaoPush()
    
    # 2. Verifica herança
    assert isinstance(estrategia, EstrategiaNotificacao)
    
    # 3. Executa o método
    resultado = estrategia.enviar("Alerta de Dieta", "DEVICE_ID_123")
    
    # 4. Captura o output
    captured = capsys.readouterr()
    
    # 5. Validações
    assert resultado is True
    assert "[PUSH]" in captured.out  # Garante que usou a implementação de Push
    assert "DEVICE_ID_123" in captured.out

def test_polimorfismo_em_lista(capsys):
    """
    Itera sobre uma lista de estratégias diferentes tratando todas como iguais.
    Essa é a definição clássica de polimorfismo exigida no tópico 3.3.
    """
    estratégias = [NotificacaoEmail(), NotificacaoPush()]
    mensagem = "Teste Polimórfico"
    destinatario = "user"
    
    for est in estratégias:
        est.enviar(mensagem, destinatario)
        
    captured = capsys.readouterr()
    
    # Verifica se ambas as estratégias rodaram
    assert "[EMAIL]" in captured.out
    assert "[PUSH]" in captured.out