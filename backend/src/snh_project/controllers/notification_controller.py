"""
Controller de Notificações.

Gerencia o registro de canais de notificação e o histórico
de notificações enviadas.

Responsabilidades:
    - Registrar/remover canais (copeiros, empresa terceirizada)
    - Manter histórico de notificações (US07, US09)
    - Marcar notificações como lidas
"""

from datetime import datetime
from typing import Any, Dict, List

from ..services.notifier import NotificadorService
from ..services.strategies import EstrategiaNotificacao


class NotificationController:
    """
    Gerencia canais de notificação e histórico de alertas.

    O histórico fica em memória durante a sessão do servidor.
    Para persistência completa, um repositório de notificações
    pode ser adicionado futuramente (OCP — sem modificar esta classe).

    Atributos:
        _notificador: Serviço Observer de notificações
        _historico: Lista de notificações enviadas (em memória)
    """

    def __init__(self, notificador: NotificadorService) -> None:
        """
        Args:
            notificador: Instância de NotificadorService
        """
        self._notificador = notificador
        self._historico: List[Dict[str, Any]] = []

    def registrar_canal(
        self,
        nome_canal: str,
        estrategia: EstrategiaNotificacao,
        destinatarios: List[str],
    ) -> Dict[str, Any]:
        """
        Registra um novo canal de notificação.

        Args:
            nome_canal: Identificador do canal (ex: 'copeiros_manha')
            estrategia: Estratégia de envio (Email, Push, etc.)
            destinatarios: Lista de endereços/tokens dos destinatários

        Returns:
            Dict confirmando o registro
        """
        self._notificador.registrar_observador(nome_canal, estrategia, destinatarios)
        return {
            "canal": nome_canal,
            "destinatarios": destinatarios,
            "registrado": True,
        }

    def remover_canal(self, nome_canal: str) -> Dict[str, Any]:
        """
        Remove um canal de notificação.

        Args:
            nome_canal: Nome do canal a remover

        Returns:
            Dict com resultado da operação
        """
        removido = self._notificador.remover_observador(nome_canal)
        return {"canal": nome_canal, "removido": removido}

    def listar_canais(self) -> List[str]:
        """
        Retorna os nomes dos canais ativos.

        Returns:
            Lista de nomes dos canais registrados
        """
        return self._notificador.listar_canais_ativos()

    def historico_notificacoes(self, limite: int = 50) -> List[Dict[str, Any]]:
        """
        Retorna o histórico recente de notificações (US07).

        Args:
            limite: Quantidade máxima de registros a retornar

        Returns:
            Lista das últimas notificações (mais recente primeiro)
        """
        return list(reversed(self._historico[-limite:]))

    def registrar_no_historico(
        self,
        mensagem: str,
        paciente_id: str,
        resultado: Dict[str, Any],
        urgente: bool = False,
    ) -> None:
        """
        Adiciona uma notificação ao histórico interno.

        Chamado pelo PrescricaoController após disparar notificação.

        Args:
            mensagem: Texto da notificação
            paciente_id: UUID do paciente relacionado
            resultado: Dict com total_enviados, sucessos, falhas
            urgente: Se a notificação é urgente (RN05)
        """
        self._historico.append({
            "id": len(self._historico) + 1,
            "data_hora": datetime.now().isoformat(),
            "mensagem": mensagem,
            "paciente_id": paciente_id,
            "urgente": urgente,
            "total_enviados": resultado.get("total_enviados", 0),
            "sucessos": resultado.get("sucessos", 0),
            "falhas": resultado.get("falhas", 0),
        })
