"""Schemas Pydantic para Prescrição."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class PrescriptionCreate(BaseModel):
    """Payload para criar prescrição (POST /patients/{id}/prescriptions)."""
    tipo_dieta: str
    dados_dieta: Dict[str, Any]


class PrescriptionUpdate(BaseModel):
    """Payload para alterar dieta (PUT /prescriptions/{id})."""
    tipo_dieta: str
    dados_dieta: Dict[str, Any]


class HistoricoItem(BaseModel):
    """Item individual do histórico de alterações."""
    data_hora: str
    tipo_alteracao: str
    descricao: str
    usuario: str


class PrescriptionResponse(BaseModel):
    """Resposta resumida de uma prescrição."""
    id: str
    patient_id: str
    paciente: str
    setor: str
    dieta_tipo: str
    ativa: bool
    total_alteracoes: int
    criado_em: str
    criado_por: str
