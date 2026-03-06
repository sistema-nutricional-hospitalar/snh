"""Schemas Pydantic para Paciente."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


def _normalizar_data(valor: str) -> str:
    """Converte qualquer formato de data para YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS.

    Aceita:
      - YYYY-MM-DD         (ISO, padrão)
      - DD/MM/YYYY         (brasileiro)
      - DD.MM.YYYY         (europeu)
      - YYYY-MM-DDTHH:MM:SS (ISO com hora)
      - DD/MM/YYYYTHH:MM:SS
    """
    v = valor.strip()

    # Separa parte de data e hora se houver 'T'
    partes = v.split("T", 1)
    data_str = partes[0]
    hora_str = partes[1] if len(partes) > 1 else None

    # Detecta formato DD/MM/YYYY ou DD.MM.YYYY
    for sep in ("/", "."):
        if sep in data_str:
            segmentos = data_str.split(sep)
            if len(segmentos) == 3 and len(segmentos[0]) <= 2:
                # dia.mes.ano → ano-mes-dia
                data_str = f"{segmentos[2]}-{segmentos[1].zfill(2)}-{segmentos[0].zfill(2)}"
            break

    return f"{data_str}T{hora_str}" if hora_str else data_str


class PatientCreate(BaseModel):
    """Payload para cadastro de paciente (POST /patients)."""
    nome: str
    data_nasc: str
    setor_nome: str
    leito: int
    data_internacao: str
    risco: bool = False

    @field_validator("nome")
    @classmethod
    def nome_nao_vazio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("nome não pode ser vazio")
        return v.strip()

    @field_validator("leito")
    @classmethod
    def leito_positivo(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("leito deve ser positivo")
        return v

    @field_validator("data_nasc", "data_internacao", mode="before")
    @classmethod
    def normalizar_data(cls, v: str) -> str:
        return _normalizar_data(v)


class PatientUpdate(BaseModel):
    """Payload para edição de paciente (PUT /patients/{id})."""
    nome: Optional[str] = None
    data_nasc: Optional[str] = None
    setor_nome: Optional[str] = None
    leito: Optional[int] = None
    data_internacao: Optional[str] = None
    risco: Optional[bool] = None

    @field_validator("data_nasc", "data_internacao", mode="before")
    @classmethod
    def normalizar_data(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _normalizar_data(v)


class PatientResponse(BaseModel):
    """Resposta com dados de um paciente."""
    id: str
    nome: str
    data_nasc: str
    setor_id: str
    setor_nome: str
    leito: int
    data_internacao: str
    risco: bool
    criado_em: str
    atualizado_em: str