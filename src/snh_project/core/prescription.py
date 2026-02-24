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
    """
    Classe CENTRAL do sistema — integra Paciente, Dieta e Notificações.

    Gerencia o ciclo de vida completo de uma prescrição dietética hospitalar:
    criação, alterações, encerramento e notificações automáticas.

    Relações:
        - Agregação com Paciente (◇)
        - Agregação com Dieta (◇)
        - Agregação com NotificadorService (◇)
        - Composição com HistoricoAlteracao (◆)

    Atributos:
        _paciente: Paciente que recebe a dieta
        _dieta: Dieta prescrita atualmente
        _notificador: Serviço de notificações
        _historico: Lista append-only de alterações
        _ativa: Status da prescrição
        _id: Identificador único
    """

    def __init__(
        self,
        paciente: Paciente,
        dieta: Dieta,
        notificador: NotificadorService,
        usuario_responsavel: str = "sistema"
    ):
        """
        Cria uma nova prescrição ativa para o paciente.

        Args:
            paciente: Paciente que receberá a dieta (deve ser Paciente)
            dieta: Dieta a ser prescrita (deve ser Dieta)
            notificador: Serviço de notificações (deve ser NotificadorService)
            usuario_responsavel: Quem está prescrevendo (default: "sistema")

        Raises:
            TypeError: Se paciente, dieta ou notificador forem de tipos incorretos
        """
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

        # Inicializa AuditoriaMixin
        super().__init__(usuario_responsavel)

        self._paciente: Paciente = paciente
        self._dieta: Dieta = dieta
        self._notificador: NotificadorService = notificador
        self._historico: list[HistoricoAlteracao] = []
        self._ativa: bool = True
        self._id: int = id(self)

        # Registra criação no histórico
        self._historico.append(HistoricoAlteracao(
            tipo_alteracao="Criação de prescrição",
            descricao=f"Prescrição criada com dieta {type(dieta).__name__}",
            usuario=usuario_responsavel
        ))

    @property
    def paciente(self) -> Paciente:
        """Retorna o paciente da prescrição"""
        return self._paciente

    @property
    def dieta(self) -> Dieta:
        """Retorna a dieta atual da prescrição"""
        return self._dieta

    @property
    def ativa(self) -> bool:
        """Retorna True se a prescrição está ativa"""
        return self._ativa

    @property
    def historico(self) -> list[HistoricoAlteracao]:
        """Retorna uma CÓPIA do histórico (append-only, nunca remove)"""
        return self._historico.copy()

    @property
    def id_prescricao(self) -> int:
        """Retorna o identificador único da prescrição"""
        return self._id


    def alterar_dieta(self, nova_dieta: Dieta, usuario: str = "sistema") -> None:
    
        if not self._ativa:
            raise ValueError("Não é possível alterar uma prescrição encerrada")

        if not isinstance(nova_dieta, Dieta):
            raise TypeError(
                f"nova_dieta deve ser instância de Dieta, recebido: {type(nova_dieta).__name__}"
            )

        tipo_anterior = type(self._dieta).__name__
        tipo_novo = type(nova_dieta).__name__

        self._historico.append(HistoricoAlteracao(
            tipo_alteracao="Alteração de dieta",
            descricao=f"Dieta alterada de {tipo_anterior} para {tipo_novo}",
            usuario=usuario
        ))

        self._dieta = nova_dieta

        self._notificador.notificar_mudanca(
            id_paciente=self._id,
            mensagem=(
                f"[SNH] Prescrição #{self._id} - Alteração de dieta\n"
                f"Paciente: {self._paciente.nome} | "
                f"Setor: {self._paciente.setor_nome}\n"
                f"Dieta alterada de {tipo_anterior} para {tipo_novo}"
            )
        )

        self.registrar_atualizacao()

    def encerrar(self, usuario: str = "sistema") -> None:
        
        if not self._ativa:
            raise ValueError("Prescrição já está encerrada")

        self._ativa = False

        self._historico.append(HistoricoAlteracao(
            tipo_alteracao="Encerramento",
            descricao=f"Prescrição encerrada pelo usuário '{usuario}'",
            usuario=usuario
        ))

        self._dieta.encerrar_dieta()

        self._notificador.notificar_mudanca(
            id_paciente=self._id,
            mensagem=(
                f"[SNH] Prescrição #{self._id} - Encerramento\n"
                f"Paciente: {self._paciente.nome} | "
                f"Setor: {self._paciente.setor_nome}\n"
                f"Prescrição encerrada por '{usuario}'"
            )
        )

        self.registrar_atualizacao()

    def obter_resumo(self) -> dict:
        
        return {
            "id": self._id,
            "paciente": self._paciente.nome,
            "setor": self._paciente.setor_nome,
            "dieta_tipo": type(self._dieta).__name__,
            "ativa": self._ativa,
            "total_alteracoes": len(self._historico),
            "criado_em": self.criado_em,
            "criado_por": self.usuario_responsavel
        }

    def __repr__(self) -> str:
        return (
            f"Prescricao("
            f"id={self._id}, "
            f"paciente='{self._paciente.nome}', "
            f"dieta={type(self._dieta).__name__}, "
            f"ativa={self._ativa})"
        )
