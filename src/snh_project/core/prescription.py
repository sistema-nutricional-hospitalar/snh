from datetime import datetime
from typing import Optional

from .base import AuditoriaMixin, Dieta
from .patient import Paciente
from ..services.notifier import NotificadorService


class HistoricoAlteracao:
    
    def __init__(
        self,
        tipo_alteracao: str,
        descricao: str,
        usuario: str = "sistema"
    ):
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
        return self._data_hora

    @property
    def tipo_alteracao(self) -> str:
        return self._tipo_alteracao

    @property
    def descricao(self) -> str:
        return self._descricao

    @property
    def usuario(self) -> str:
        return self._usuario

class Prescricao:
    pass