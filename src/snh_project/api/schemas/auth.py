"""Schemas Pydantic para autenticação."""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Payload do POST /auth/login."""
    email: str
    senha: str


class TokenResponse(BaseModel):
    """Resposta do login com token JWT."""
    access_token: str
    token_type: str = "bearer"
    tipo_usuario: str
    nome: str
    user_id: str
