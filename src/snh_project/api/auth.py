"""
Utilitários de autenticação JWT.

Responsável por gerar e verificar tokens JWT.
Princípio SRP: este módulo faz apenas uma coisa — lidar com tokens.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt

# Compatível com PyJWT 2.x e 3.x
try:
    from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
except ImportError:
    ExpiredSignatureError = jwt.ExpiredSignatureError  # type: ignore
    InvalidTokenError = jwt.InvalidTokenError  # type: ignore

# Configurações do token — em produção, SECRET_KEY vem de variável de ambiente
SECRET_KEY = os.getenv("SNH_SECRET_KEY", "snh-dev-secret-key-troque-em-producao")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 8


def criar_token(payload: Dict[str, Any]) -> str:
    """Gera um token JWT assinado com expiração de 8 horas.

    Args:
        payload: Dados a embutir no token (ex: user_id, tipo, nome).

    Returns:
        String JWT assinada.
    """
    dados = payload.copy()
    expiracao = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    dados["exp"] = expiracao
    dados["iat"] = datetime.now(timezone.utc)
    return jwt.encode(dados, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodifica e valida um token JWT.

    Args:
        token: String JWT a verificar.

    Returns:
        Payload decodificado se válido, None se inválido ou expirado.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        return None
    except InvalidTokenError:
        return None