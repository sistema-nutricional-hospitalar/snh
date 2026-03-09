"""Router de autenticação — POST /auth/login."""

from fastapi import APIRouter, HTTPException, status

from ..auth import criar_token
from ..dependencies import UserCtrl
from ..schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login de usuário",
)
def login(body: LoginRequest, user_ctrl: UserCtrl) -> TokenResponse:
    """Autentica o usuário e retorna um token JWT (US16, RN08)."""

    # aceita tanto 'senha' quanto 'password' (compatibilidade com frontend)
    senha = body.senha or body.password

    usuario = user_ctrl.autenticar(body.email, senha)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = criar_token({
        "sub":     usuario["id"],
        "user_id": usuario["id"],
        "tipo":    usuario["tipo"],
        "nome":    usuario["nome"],
    })

    return TokenResponse(
        access_token=token,
        tipo_usuario=usuario["tipo"],
        nome=usuario["nome"],
        user_id=usuario["id"],
    )