from datetime import datetime
from typing import Optional

from .base import AuditoriaMixin, Dieta
from .patient import Paciente
from ..services.notifier import NotificadorService


class HistoricoAlteracao:
    """
    Registra uma alteração realizada em uma prescrição.

    Funciona como um Value Object imutável — após criado, não pode ser alterado.
    Compõe a Prescricao (◆): não existe sem ela.

    Atributos:
        _data_hora: Momento exato da alteração (automático)
        _tipo_alteracao: Categoria da mudança (ex: "Alteração de dieta")
        _descricao: Detalhes sobre o que foi alterado
        _usuario: Responsável pela ação (default: "sistema")
    """

    def __init__(
        self,
        tipo_alteracao: str,
        descricao: str,
        usuario: str = "sistema"
    ):
        """
        Cria um registro imutável de alteração.

        Args:
            tipo_alteracao: Categoria da mudança (não pode ser vazio)
            descricao: Detalhes da mudança (não pode ser vazio)
            usuario: Quem realizou a ação (default: "sistema")

        Raises:
            ValueError: Se tipo_alteracao ou descricao forem vazios
        """
        if not tipo_alteracao or not tipo_alteracao.strip():
            raise ValueError("tipo_alteracao não pode ser vazio")

        if not descricao or not descricao.strip():
            raise ValueError("descricao não pode ser vazia")

        self._data_hora: datetime = datetime.now()
        self._tipo_alteracao: str = tipo_alteracao.strip()
        self._descricao: str = descricao.strip()
        self._usuario: str = usuario.strip() if usuario and usuario.strip() else "sistema"

    @property
    def data_hora(self) -> datetime:
        """Retorna o momento da alteração"""
        return self._data_hora

    @property
    def tipo_alteracao(self) -> str:
        """Retorna o tipo/categoria da alteração"""
        return self._tipo_alteracao

    @property
    def descricao(self) -> str:
        """Retorna a descrição detalhada da alteração"""
        return self._descricao

    @property
    def usuario(self) -> str:
        """Retorna quem realizou a alteração"""
        return self._usuario

    def __repr__(self) -> str:
        return (
            f"HistoricoAlteracao("
            f"tipo='{self._tipo_alteracao}', "
            f"usuario='{self._usuario}', "
            f"data='{self._data_hora.strftime('%Y-%m-%d %H:%M:%S')}')"
        )

class Prescricao(AuditoriaMixin):

    def __init__(
        self,
        paciente: Paciente,
        dieta: Dieta,
        notificador: NotificadorService,
        usuario_responsavel: str = "sistema"
    ):
        if not isinstance(paciente, Paciente):
            raise TypeError(
                f"paciente deve ser instância de Paciente, recebido: {type(paciente).__name__}"
            )

        if not isinstance(dieta, Dieta):
            raise TypeError(
                f"dieta deve ser instância de Dieta, recebido: {type(dieta).__name__}"
            )

        if not isinstance(notificador, NotificadorService):
            raise TypeError(
                f"notificador deve ser instância de NotificadorService, recebido: {type(notificador).__name__}"
            )

        super().__init__(usuario_responsavel)

        self._paciente: Paciente = paciente
        self._dieta: Dieta = dieta
        self._notificador: NotificadorService = notificador
        self._historico: list[HistoricoAlteracao] = []
        self._ativa: bool = True
        self._id: int = id(self)

        self._historico.append(HistoricoAlteracao(
            tipo_alteracao="Criação de prescrição",
            descricao=f"Prescrição criada com dieta {type(dieta).__name__}",
            usuario=usuario_responsavel
        ))

    @property
    def paciente(self) -> Paciente:
        return self._paciente

    @property
    def dieta(self) -> Dieta:
        return self._dieta

    @property
    def ativa(self) -> bool:
        return self._ativa

    @property
    def historico(self) -> list[HistoricoAlteracao]:
        return self._historico.copy()

    @property
    def id_prescricao(self) -> int:
        return self._id