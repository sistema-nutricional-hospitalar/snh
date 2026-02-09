from abc import ABC, abstractmethod

class EstrategiaNotificacao(ABC):
    """
    Interface (Classe Abstrata) do Padrão Strategy.
    
    Define o contrato obrigatório para qualquer mecanismo de notificação.
    Todas as subclasses DEVEM implementar o método 'enviar'.
    """

    @abstractmethod
    def enviar(self, mensagem: str, destinatario: str) -> bool:
        """
        Envia uma notificação para o destinatário.

        Args:
            mensagem (str): O conteúdo da notificação.
            destinatario (str): O endereço/ID do destinatário (ex: email ou device_id).

        Returns:
            bool: True se o envio foi simulado com sucesso, False caso contrário.
        """
        pass

class NotificacaoEmail(EstrategiaNotificacao):
    """
    Estratégia concreta para envio de notificações via E-mail.
    """
    
    def enviar(self, mensagem: str, destinatario: str) -> bool:
        # Aqui entraria a lógica real de SMTP (ex: smtplib)
        # Como é um projeto acadêmico, usamos um Mock (print simulado)
        print(f"[EMAIL] Enviando para: {destinatario}")
        print(f"        Conteúdo: {mensagem}")
        print("-" * 30)
        return True

class NotificacaoPush(EstrategiaNotificacao):
    """
    Estratégia concreta para envio de notificações via Push (App Mobile).
    """
    
    def enviar(self, mensagem: str, destinatario: str) -> bool:
        # Aqui entraria a lógica de integração com Firebase/OneSignal
        print(f"[PUSH] Notificando Dispositivo ID: {destinatario}")
        print(f"       Alerta: {mensagem}")
        print("-" * 30)
        return True