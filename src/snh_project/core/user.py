from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from .base import AuditoriaMixin


# ===========================================================================
# ENUMS
# ===========================================================================

class TipoUsuario(Enum):
    """Define os tipos de usuário do sistema SNH."""
    ADMINISTRADOR  = "administrador"
    MEDICO         = "medico"
    NUTRICIONISTA  = "nutricionista"
    ENFERMEIRO     = "enfermeiro"
    COPEIRO        = "copeiro"


class StatusUsuario(Enum):
    """Define os possíveis status de um usuário."""
    ATIVO    = "ativo"
    INATIVO  = "inativo"
    BLOQUEADO = "bloqueado"

# ===========================================================================
# CLASSE ABSTRATA BASE
# ===========================================================================

class Usuario(ABC, AuditoriaMixin):
    """
    Classe abstrata base para todos os usuários do sistema SNH.

    Define o contrato de permissões via métodos abstratos polimórficos,
    garantindo que cada subclasse declare explicitamente o que pode fazer.

    Herda de:
        ABC         — força implementação dos métodos abstratos
        AuditoriaMixin — fornece criado_em, atualizado_em, registrar_atualizacao()

    Atributos:
        _nome           : Nome completo do usuário
        _cpf            : CPF (11 dígitos numéricos, armazenado limpo)
        _email          : E-mail (deve conter '@' e '.')
        _tipo           : TipoUsuario (enum)
        _status         : StatusUsuario (default: ATIVO)
        _data_cadastro  : datetime automático no momento da criação
        _ultimo_acesso  : Optional[datetime], None até o primeiro acesso
    """

    def __init__(
        self,
        nome: str,
        cpf: str,
        email: str,
        tipo: TipoUsuario,
        usuario_responsavel: str = "sistema"
    ):
        """
        Inicializa um usuário com validações e auditoria.

        Args:
            nome               : Nome completo (não pode ser vazio)
            cpf                : CPF com ou sem formatação (11 dígitos)
            email              : E-mail válido (deve conter '@' e '.')
            tipo               : TipoUsuario (enum)
            usuario_responsavel: Quem está criando (default: "sistema")

        Raises:
            ValueError: Se nome vazio, CPF inválido ou e-mail inválido
            TypeError : Se tipo não for TipoUsuario
        """
        # Validação: nome
        if not nome or not nome.strip():
            raise ValueError("Nome do usuário não pode ser vazio")

        # Validação: CPF — limpa e valida
        cpf_limpo = "".join(c for c in cpf if c.isdigit())
        if len(cpf_limpo) != 11:
            raise ValueError(
                f"CPF deve conter exatamente 11 dígitos numéricos, "
                f"recebido: '{cpf}' ({len(cpf_limpo)} dígitos)"
            )

        # Validação: e-mail
        if "@" not in email or "." not in email:
            raise ValueError(
                f"E-mail inválido: '{email}'. Deve conter '@' e '.'"
            )

        # Validação: tipo
        if not isinstance(tipo, TipoUsuario):
            raise TypeError(
                f"tipo deve ser TipoUsuario, recebido: {type(tipo).__name__}"
            )

        # Inicializa AuditoriaMixin
        AuditoriaMixin.__init__(self, usuario_responsavel)

        # Atributos
        self._nome: str = nome.strip()
        self._cpf: str = cpf_limpo
        self._email: str = email.strip()
        self._tipo: TipoUsuario = tipo
        self._status: StatusUsuario = StatusUsuario.ATIVO
        self._data_cadastro: datetime = datetime.now()
        self._ultimo_acesso: Optional[datetime] = None

    # -----------------------------------------------------------------------
    # PROPERTIES
    # -----------------------------------------------------------------------

    @property
    def nome(self) -> str:
        """Retorna o nome do usuário."""
        return self._nome

    @property
    def cpf(self) -> str:
        """Retorna o CPF (11 dígitos, sem formatação)."""
        return self._cpf

    @property
    def email(self) -> str:
        """Retorna o e-mail do usuário."""
        return self._email

    @property
    def tipo(self) -> TipoUsuario:
        """Retorna o tipo do usuário."""
        return self._tipo

    @property
    def status(self) -> StatusUsuario:
        """Retorna o status atual do usuário."""
        return self._status

    @property
    def data_cadastro(self) -> datetime:
        """Retorna a data/hora de cadastro."""
        return self._data_cadastro

    @property
    def ultimo_acesso(self) -> Optional[datetime]:
        """Retorna a data/hora do último acesso (None se nunca acessou)."""
        return self._ultimo_acesso

    # -----------------------------------------------------------------------
    # MÉTODOS ABSTRATOS (polimórficos)
    # -----------------------------------------------------------------------

    @abstractmethod
    def pode_prescrever_dieta(self) -> bool:
        """Indica se o usuário pode criar prescrições de dieta."""
        ...

    @abstractmethod
    def pode_alterar_prescricao(self) -> bool:
        """Indica se o usuário pode editar prescrições existentes."""
        ...

    @abstractmethod
    def pode_visualizar_prescricoes(self) -> bool:
        """Indica se o usuário pode visualizar prescrições."""
        ...

    # -----------------------------------------------------------------------
    # MÉTODOS CONCRETOS
    # -----------------------------------------------------------------------

    def registrar_acesso(self) -> None:
        """Atualiza o timestamp do último acesso para agora."""
        self._ultimo_acesso = datetime.now()

    def ativar(self) -> None:
        """
        Ativa o usuário (status → ATIVO).

        Raises:
            ValueError: Se o usuário já estiver ativo
        """
        if self._status == StatusUsuario.ATIVO:
            raise ValueError(f"Usuário '{self._nome}' já está ativo")
        self._status = StatusUsuario.ATIVO
        self.registrar_atualizacao()

    def inativar(self) -> None:
        """
        Inativa o usuário (status → INATIVO).

        Raises:
            ValueError: Se o usuário já estiver inativo
        """
        if self._status == StatusUsuario.INATIVO:
            raise ValueError(f"Usuário '{self._nome}' já está inativo")
        self._status = StatusUsuario.INATIVO
        self.registrar_atualizacao()

    def bloquear(self) -> None:
        """
        Bloqueia o usuário (status → BLOQUEADO).

        Raises:
            ValueError: Se o usuário já estiver bloqueado
        """
        if self._status == StatusUsuario.BLOQUEADO:
            raise ValueError(f"Usuário '{self._nome}' já está bloqueado")
        self._status = StatusUsuario.BLOQUEADO
        self.registrar_atualizacao()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"nome='{self._nome}', "
            f"cpf='{self._cpf}', "
            f"tipo={self._tipo.value}, "
            f"status={self._status.value})"
        )
