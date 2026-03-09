"""Repositório de Notificações — persistência em JSON."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .json_repository import JsonRepository


class NotificationRepository(JsonRepository):
    """
    Repositório de notificações com persistência em JSON.

    Implementa US07 (copeiro recebe notificações) e US09 (prioridade).
    Notificações são armazenadas com destinatário, mensagem, timestamp e status de leitura.
    """

    def __init__(self, filepath: str = "data/notifications.json") -> None:
        """
        Args:
            filepath: Caminho do arquivo JSON de notificações.
        """
        super().__init__(filepath)

    def salvar_notificacao(
        self,
        destinatario: str,
        mensagem: str,
        patient_id: Optional[str] = None,
        prioridade: str = "normal",
    ) -> Dict[str, Any]:
        """Persiste uma nova notificação.

        Args:
            destinatario: E-mail ou identificador do destinatário.
            mensagem: Texto da notificação.
            patient_id: UUID do paciente relacionado (opcional).
            prioridade: 'normal' ou 'urgente' (US09 — RN05).

        Returns:
            Dicionário da notificação salva com 'id' gerado.
        """
        record = {
            "id": self._novo_id(),
            "destinatario": destinatario,
            "mensagem": mensagem,
            "patient_id": patient_id,
            "prioridade": prioridade,
            "lida": False,
            "criado_em": datetime.now().isoformat(),
        }
        return self.save(record)

    def listar_nao_lidas(self, destinatario: str) -> List[Dict[str, Any]]:
        """Retorna notificações não lidas de um destinatário (US07).

        Args:
            destinatario: E-mail ou identificador.

        Returns:
            Lista de notificações não lidas, ordenadas por data (mais recentes primeiro).
        """
        nao_lidas = [
            r for r in self.find_all()
            if r.get("destinatario") == destinatario and not r.get("lida", False)
        ]
        return sorted(nao_lidas, key=lambda r: r.get("criado_em", ""), reverse=True)

    def listar_por_destinatario(self, destinatario: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retorna todas as notificações de um destinatário.

        Args:
            destinatario: E-mail ou identificador.
            limit: Número máximo de notificações a retornar (padrão 50).

        Returns:
            Lista ordenada por data decrescente.
        """
        todas = [
            r for r in self.find_all()
            if r.get("destinatario") == destinatario
        ]
        ordenadas = sorted(todas, key=lambda r: r.get("criado_em", ""), reverse=True)
        return ordenadas[:limit]

    def marcar_lida(self, notif_id: str) -> bool:
        """Marca uma notificação como lida.

        Args:
            notif_id: UUID da notificação.

        Returns:
            True se marcada, False se não encontrada.
        """
        registro = self.find_by_id(notif_id)
        if not registro:
            return False
        registro["lida"] = True
        registro["lida_em"] = datetime.now().isoformat()
        self.save(registro)
        return True

    def marcar_todas_lidas(self, destinatario: str) -> int:
        """Marca todas as notificações não lidas de um destinatário como lidas.

        Args:
            destinatario: E-mail ou identificador.

        Returns:
            Quantidade de notificações marcadas.
        """
        nao_lidas = self.listar_nao_lidas(destinatario)
        for n in nao_lidas:
            n["lida"] = True
            n["lida_em"] = datetime.now().isoformat()
            self.save(n)
        return len(nao_lidas)

    def contar_nao_lidas(self, destinatario: str) -> int:
        """Retorna quantidade de notificações não lidas.

        Args:
            destinatario: E-mail ou identificador.

        Returns:
            Número inteiro de notificações não lidas.
        """
        return len(self.listar_nao_lidas(destinatario))
