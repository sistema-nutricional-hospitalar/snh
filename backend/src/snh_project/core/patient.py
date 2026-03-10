"""Schemas Pydantic para Paciente."""

from datetime import date
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, model_validator


def _validar_data_nascimento(valor: Optional[str]) -> Optional[str]:
    """Valida que a data de nascimento não é futura nem anterior a 1900."""
    if not valor:
        return valor
    try:
        nascimento = date.fromisoformat(valor)
    except ValueError:
        raise ValueError(f"Formato de data inválido: '{valor}'. Use AAAA-MM-DD.")
    if nascimento >= date.today():
        raise ValueError("Data de nascimento não pode ser hoje ou no futuro.")
    if nascimento < date(1900, 1, 1):
        raise ValueError("Data de nascimento inválida (anterior a 1900).")
    return valor


class PatientCreate(BaseModel):
    """Payload para cadastro de paciente.

    Aceita tanto o formato legado (data_nasc, setor_nome, leito int)
    quanto o formato do frontend React (data_nascimento, setor_id, quarto+leito).
    """
    nome: str

    # campos legado
    data_nasc: Optional[str] = None
    setor_nome: Optional[str] = None
    leito: Optional[Any] = None          # pode vir como int ou string
    data_internacao: Optional[str] = None
    risco: bool = False

    # campos extras do frontend
    data_nascimento: Optional[str] = None  # alias de data_nasc
    quarto: Optional[str] = None
    setor_id: Optional[str] = None         # id do setor (aceita em vez de setor_nome)
    sexo: Optional[str] = None
    peso_atual: Optional[float] = None
    altura: Optional[float] = None
    diagnostico: Optional[str] = None
    observacoes: Optional[str] = None
    alergias: List[str] = []
    restricoes_alimentares: List[str] = []
    ativo: bool = True

    @model_validator(mode="after")
    def normalizar_campos(self) -> "PatientCreate":
        # Aceita data_nascimento como alias de data_nasc
        if self.data_nascimento and not self.data_nasc:
            self.data_nasc = self.data_nascimento
        # Valida a data antes de usar
        _validar_data_nascimento(self.data_nasc)
        # data_nasc mínimo para não quebrar o domínio
        if not self.data_nasc:
            self.data_nasc = "1900-01-01"
        if not self.data_internacao:
            self.data_internacao = date.today().isoformat()
        return self


class PatientUpdate(BaseModel):
    """Payload para edição de paciente (PUT /patients/{id})."""
    nome: Optional[str] = None
    data_nasc: Optional[str] = None
    setor_nome: Optional[str] = None
    setor_id: Optional[str] = None
    leito: Optional[Any] = None
    quarto: Optional[str] = None
    data_internacao: Optional[str] = None
    risco: Optional[bool] = None
    sexo: Optional[str] = None
    peso_atual: Optional[float] = None
    altura: Optional[float] = None
    diagnostico: Optional[str] = None
    observacoes: Optional[str] = None
    alergias: Optional[List[str]] = None
    restricoes_alimentares: Optional[List[str]] = None

    @model_validator(mode="after")
    def validar_data(self) -> "PatientUpdate":
        _validar_data_nascimento(self.data_nasc)
        return self


class PatientResponse(BaseModel):
    """Resposta com dados de um paciente."""
    id: str
    nome: str
    data_nasc: Optional[str] = None
    setor_id: Optional[str] = None
    setor_nome: Optional[str] = None
    leito: Optional[Any] = None
    quarto: Optional[str] = None
    data_internacao: Optional[str] = None
    risco: bool = False
    criado_em: Optional[str] = None
    atualizado_em: Optional[str] = None
    # campos extras do frontend
    sexo: Optional[str] = None
    peso_atual: Optional[float] = None
    altura: Optional[float] = None
    diagnostico: Optional[str] = None
    observacoes: Optional[str] = None
    alergias: List[str] = []
    restricoes_alimentares: List[str] = []
    ativo: bool = True

    class Config:
        extra = "ignore"

        
Paciente = PatientResponse