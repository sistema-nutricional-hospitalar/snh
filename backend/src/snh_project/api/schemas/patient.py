"""Schemas Pydantic para Paciente."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, model_validator


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
    quarto: Optional[int] = None
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
        # data_nasc mínimo para não quebrar o domínio
        if not self.data_nasc:
            self.data_nasc = "1900-01-01"
        if not self.data_internacao:
            from datetime import date
            self.data_internacao = date.today().isoformat()
        return self


class PatientUpdate(BaseModel):
    """Payload para edição de paciente (PUT /patients/{id})."""
    nome: Optional[str] = None
    data_nasc: Optional[str] = None
    setor_nome: Optional[str] = None
    setor_id: Optional[str] = None
    leito: Optional[Any] = None
    quarto: Optional[int] = None
    data_internacao: Optional[str] = None
    risco: Optional[bool] = None
    sexo: Optional[str] = None
    peso_atual: Optional[float] = None
    altura: Optional[float] = None
    diagnostico: Optional[str] = None
    observacoes: Optional[str] = None
    alergias: Optional[List[str]] = None
    restricoes_alimentares: Optional[List[str]] = None


class PatientResponse(BaseModel):
    """Resposta com dados de um paciente."""
    id: str
    nome: str
    data_nasc: Optional[str] = None
    setor_id: Optional[str] = None
    setor_nome: Optional[str] = None
    leito: Optional[Any] = None
    quarto: Optional[int] = None
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