"""Schemas Pydantic para autenticação."""

from typing import Optional
from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Payload do POST /auth/login.
    
    Aceita email+senha (padrão interno) ou email+password (frontend).
    """
    email: str
    senha: Optional[str] = None
    password: Optional[str] = None  # alias vindo do frontend


class TokenResponse(BaseModel):
    """Resposta do login com token JWT."""
    access_token: str
    token_type: str = "bearer"
    tipo_usuario: str
    nome: str
    user_id: str