from abc import ABC

class EstrategiaNotificacao(ABC):
    pass

class NotificacaoPush(EstrategiaNotificacao):
    pass

class NotificacaoEmail(EstrategiaNotificacao):
    pass