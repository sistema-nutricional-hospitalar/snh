"""Schemas Pydantic para Usuário."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, computed_field


class UserCreate(BaseModel):
    """Payload para cadastro de usuário (POST /users)."""
    nome: str
    email: str
    senha: str
    tipo: str
    cpf: Optional[str] = None           # opcional — gerado se ausente
    crn: Optional[str] = None
    crm: Optional[str] = None
    especialidade: Optional[str] = None
    coren: Optional[str] = None
    setor_trabalho: Optional[str] = None
    setor: Optional[str] = None         # alias de setor_trabalho (frontend)
    turno: Optional[str] = None
    ativo: Optional[bool] = True


class UserStatusUpdate(BaseModel):
    """Payload para alterar status de usuário.

    Aceita tanto `status` (string: 'ativo'/'inativo'/'bloqueado')
    quanto `ativo` (bool) para compatibilidade com o frontend.
    """
    status: Optional[str] = None
    ativo: Optional[bool] = None

    def resolver_status(self) -> str:
        """Retorna o status como string normalizada."""
        if self.status:
            return self.status
        if self.ativo is not None:
            return "ativo" if self.ativo else "bloqueado"
        raise ValueError("Informe 'status' ou 'ativo'.")


class UserResponse(BaseModel):
    """Resposta com dados de um usuário (sem senha)."""
    id: str
    nome: str
    cpf: Optional[str] = None
    email: str
    tipo: str
    status: Optional[str] = "ativo"
    criado_em: Optional[str] = None
    dados_extras: Dict[str, Any] = {}

    @computed_field
    @property
    def ativo(self) -> bool:
        """Computed — verdadeiro se status == 'ativo'."""
        return self.status == "ativo"

    class Config:
        extra = "ignore"
