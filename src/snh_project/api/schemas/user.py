"""Schemas Pydantic para Usuário."""

from typing import Any, Dict, Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    """Payload para cadastro de usuário (POST /users)."""
    nome: str
    cpf: str
    email: str
    tipo: str
    senha: str
    # Campos extras por tipo
    crn: Optional[str] = None           # nutricionista
    crm: Optional[str] = None           # medico
    especialidade: Optional[str] = None # medico
    coren: Optional[str] = None         # enfermeiro
    setor_trabalho: Optional[str] = None# enfermeiro
    turno: Optional[str] = None         # copeiro


class UserStatusUpdate(BaseModel):
    """Payload para alterar status de usuário."""
    status: str  # 'ativo', 'inativo', 'bloqueado'


class UserResponse(BaseModel):
    """Resposta com dados de um usuário (sem senha)."""
    id: str
    nome: str
    cpf: str
    email: str
    tipo: str
    status: str
    criado_em: str
    dados_extras: Dict[str, Any] = {}
