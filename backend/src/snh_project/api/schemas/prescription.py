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
    """Item do histórico de alterações."""
    data_hora: str
    tipo_alteracao: str
    descricao: str
    usuario: str


class DietaResponse(BaseModel):
    """Dieta embutida — campos do JSON real."""
    tipo: Optional[str] = None
    dados: Dict[str, Any] = {}
    ativa: bool = True
    criado_em: Optional[str] = None
    usuario_responsavel: Optional[str] = None
    itens: List[Any] = []

    class Config:
        extra = "ignore"


class PrescriptionResponse(BaseModel):
    """Resposta de prescrição — mapeada diretamente do JSON persistido."""
    id: str
    patient_id: str
    setor_id: Optional[str] = None
    dieta: Optional[DietaResponse] = None
    historico: List[Any] = []
    ativa: bool = True
    criado_em: Optional[str] = None
    atualizado_em: Optional[str] = None
    usuario_responsavel: Optional[str] = None

    class Config:
        extra = "ignore"
