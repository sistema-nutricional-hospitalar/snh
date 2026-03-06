"""Router de autenticação — POST /auth/login."""

from fastapi import APIRouter, HTTPException, status, Depends

from ..auth import criar_token
from ..dependencies import get_user_ctrl, UserCtrl
from ..schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login de usuário",
    description="Autentica com e-mail e senha. Retorna JWT Bearer token válido por 8 horas.",
)
def login(body: LoginRequest, user_ctrl: UserCtrl) -> TokenResponse:
    """Autentica o usuário e retorna um token JWT.

    Implementa US16, RN08.

    - **email**: e-mail cadastrado no sistema
    - **senha**: senha em texto puro (transmitida via HTTPS)

    Retorna `access_token` para usar como `Authorization: Bearer <token>`.
    """
    usuario = user_ctrl.autenticar(body.email, body.senha)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = criar_token({
        "sub": usuario["id"],
        "user_id": usuario["id"],
        "tipo": usuario["tipo"],
        "nome": usuario["nome"],
    })

    return TokenResponse(
        access_token=token,
        tipo_usuario=usuario["tipo"],
        nome=usuario["nome"],
        user_id=usuario["id"],
    )
