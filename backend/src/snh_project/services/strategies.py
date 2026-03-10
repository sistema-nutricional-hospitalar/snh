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


class NotificacaoInApp(EstrategiaNotificacao):
    """
    Estratégia de notificação in-app com persistência em JSON.

    Usada para notificações visíveis no dashboard dos copeiros (US07, US09).
    Persiste notificações via NotificationRepository para sobreviver a reinicializações.
    """

    def __init__(self, data_dir: str = "data"):
        """
        Args:
            data_dir: Diretório base dos arquivos JSON.
        """
        from ..infrastructure.notification_repository import NotificationRepository
        self._repo = NotificationRepository(f"{data_dir}/notifications.json")

    def enviar(self, mensagem: str, destinatario: str, prioridade: str = "normal", patient_id: str = None) -> bool:
        """Persiste notificação in-app para o destinatário.

        Args:
            mensagem: Texto da notificação.
            destinatario: E-mail ou identificador do destinatário.
            prioridade: 'normal' ou 'urgente' (RN05).
            patient_id: UUID do paciente relacionado (opcional).

        Returns:
            True se persistida com sucesso, False em caso de erro.
        """
        try:
            self._repo.salvar_notificacao(
                destinatario=destinatario,
                mensagem=mensagem,
                prioridade=prioridade,
                patient_id=patient_id,
            )
            return True
        except Exception:
            return False

    def obter_notificacoes(self, destinatario: str) -> list[dict]:
        """Retorna notificações não lidas de um destinatário (US07).

        Args:
            destinatario: E-mail ou identificador.

        Returns:
            Lista de notificações não lidas persistidas.
        """
        return self._repo.listar_nao_lidas(destinatario)

    def marcar_lida(self, destinatario: str) -> int:
        """Marca todas as notificações de um destinatário como lidas.

        Returns:
            Quantidade de notificações marcadas.
        """
        return self._repo.marcar_todas_lidas(destinatario)