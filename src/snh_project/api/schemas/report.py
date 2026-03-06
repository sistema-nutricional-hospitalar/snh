"""Schemas Pydantic para Relatórios."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ReportFilters(BaseModel):
    """Filtros para geração de relatório (query params)."""
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    setor_nome: Optional[str] = None
    tipo_dieta: Optional[str] = None
    apenas_ativas: bool = False


class ReportResponse(BaseModel):
    """Resposta de um relatório gerado."""
    total: int
    gerado_em: str
    filtros: Dict[str, Any]
    resumo_por_tipo: Dict[str, int] = {}
    prescricoes: List[Dict[str, Any]] = []
