from abc import ABC, abstractmethod

class EstrategiaNotificacao(ABC):
    @abstractmethod
    def enviar(self, mensagem: str, destinatario: str) -> bool:
        pass

class NotificacaoEmail(EstrategiaNotificacao):
    def enviar(self, mensagem: str, destinatario: str) -> bool:
        print(f"[EMAIL] Enviando para {destinatario}: {mensagem}")
        return True

class NotificacaoPush(EstrategiaNotificacao):
    def enviar(self, mensagem: str, destinatario: str) -> bool:
        print(f"[PUSH] Enviando para {destinatario}: {mensagem}")
        return True
