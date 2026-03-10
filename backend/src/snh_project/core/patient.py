"""Modelo de domínio Paciente."""

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .setorclin import SetorClinico


class Paciente:
    """
    Representa um paciente internado no hospital.

    Gerencia sua alocação em um setor clínico e leito específico.
    Aplica automaticamente risco=True para pacientes na UTI.

    Atributos:
        _nome: Nome completo do paciente
        _dataNasc: Data de nascimento (string ISO YYYY-MM-DD)
        _setorClinico: Setor clínico onde está internado
        _leito: Número do leito ocupado
        _datain: Data/hora de internação
        _risco: Indica se paciente está em situação de risco
        _criado_em: Timestamp de criação do registro
        _atualizado_em: Timestamp da última atualização
    """

    def __init__(
        self,
        nome: str,
        dataNasc: str,
        setorClinico: "SetorClinico",
        leito: int,
        datain: datetime,
        risco: bool,
    ) -> None:
        """
        Cria um novo paciente e o registra no setor clínico.

        Args:
            nome: Nome completo do paciente.
            dataNasc: Data de nascimento no formato YYYY-MM-DD.
            setorClinico: Setor clínico onde o paciente será internado.
            leito: Número do leito (deve estar disponível no setor).
            datain: Data e hora de internação.
            risco: Indica risco elevado (forçado True em setores UTI).

        Raises:
            TypeError: Se setorClinico não for instância de SetorClinico.
            ValueError: Se o leito já estiver ocupado no setor.
        """
        from .setorclin import SetorClinico as SC

        if not isinstance(setorClinico, SC):
            raise TypeError(
                f"setorClinico deve ser uma instância de SetorClinico, "
                f"recebido: {type(setorClinico).__name__}"
            )

        self._nome = nome
        self._dataNasc = dataNasc
        self._setorClinico = setorClinico
        self._leito = leito
        self._datain = datain
        # Setor UTI força risco=True
        self._risco = True if "UTI" in setorClinico.nome.upper() else risco
        self._criado_em = datetime.now()
        self._atualizado_em = datetime.now()

        # Registra o paciente no setor — valida disponibilidade do leito
        resultado = setorClinico.adicionar_paciente(self, leito)
        if resultado is not True:
            raise ValueError(f"Leito {leito} já ocupado no setor '{setorClinico.nome}'")

    # ── Propriedades ──────────────────────────────────────────────────────────

    @property
    def nome(self) -> str:
        """Nome completo do paciente."""
        return self._nome

    @nome.setter
    def nome(self, value: str) -> None:
        self._nome = value
        self._atualizado_em = datetime.now()

    @property
    def dataNasc(self) -> str:
        """Data de nascimento (string ISO)."""
        return self._dataNasc

    @property
    def setorClinico(self) -> "SetorClinico":
        """Setor clínico atual do paciente."""
        return self._setorClinico

    @property
    def setor_nome(self) -> str:
        """Nome do setor clínico atual (atalho conveniente)."""
        return self._setorClinico.nome

    @property
    def leito(self) -> int:
        """Número do leito ocupado."""
        return self._leito

    @property
    def datain(self) -> datetime:
        """Data e hora de internação."""
        return self._datain

    @datain.setter
    def datain(self, value: datetime) -> None:
        self._datain = value
        self._atualizado_em = datetime.now()

    @property
    def risco(self) -> bool:
        """Indica se o paciente está em situação de risco."""
        return self._risco

    @risco.setter
    def risco(self, value: bool) -> None:
        self._risco = value
        self._atualizado_em = datetime.now()

    @property
    def criado_em(self) -> datetime:
        """Timestamp de criação do registro."""
        return self._criado_em

    @property
    def atualizado_em(self) -> datetime:
        """Timestamp da última atualização."""
        return self._atualizado_em

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def transferir_para_setor(self, novo_setor: "SetorClinico", novo_leito: int) -> None:
        """
        Transfere o paciente para outro setor e leito.

        Remove o paciente do setor atual, atualiza referências e
        recalcula o risco conforme o novo setor.

        Args:
            novo_setor: Setor de destino.
            novo_leito: Leito disponível no setor de destino.

        Raises:
            ValueError: Se o leito de destino estiver ocupado.
        """
        self._setorClinico.remover_paciente(self._leito)
        self._setorClinico = novo_setor
        self._leito = novo_leito
        # Recalcula risco conforme o novo setor
        self._risco = True if "UTI" in novo_setor.nome.upper() else False
        resultado = novo_setor.adicionar_paciente(self, novo_leito)
        if resultado is not True:
            raise ValueError(f"Leito {novo_leito} já ocupado no setor '{novo_setor.nome}'")
        self._atualizado_em = datetime.now()

    def obter_tempo_internacao(self) -> int:
        """
        Calcula o número de dias de internação até hoje.

        Returns:
            int: Número de dias desde a internação.
        """
        return (datetime.now() - self._datain).days

    # ── Dunder methods ────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"Paciente(nome='{self._nome}', leito={self._leito}, "
            f"setor='{self._setorClinico.nome}')"
        )

    def __str__(self) -> str:
        return f"{self._nome} - Leito {self._leito} ({self._setorClinico.nome})"
