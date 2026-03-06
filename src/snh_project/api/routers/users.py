"""Router de Usuários — gestão administrativa (US15, US16)."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from ..dependencies import AdminUser, CurrentUser, UserCtrl
from ..schemas.user import UserCreate, UserResponse, UserStatusUpdate

router = APIRouter(prefix="/users", tags=["Usuários"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar usuário (US15, RN06)",
)
def cadastrar_usuario(
    body: UserCreate,
    usuario: AdminUser,
    ctrl: UserCtrl,
) -> UserResponse:
    """Cadastra um novo usuário no sistema.

    **Requer:** administrador (RN06).

    Tipos válidos: `nutricionista`, `medico`, `enfermeiro`, `copeiro`, `administrador`.
    """
    dados = body.model_dump(exclude_none=True)
    try:
        resultado = ctrl.cadastrar_usuario(dados, solicitante_tipo=usuario["tipo"])
        return UserResponse(**resultado)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get(
    "",
    response_model=List[UserResponse],
    summary="Listar usuários (US15, RN06)",
)
def listar_usuarios(
    usuario: AdminUser,
    ctrl: UserCtrl,
    tipo: Optional[str] = Query(None, description="Filtrar por tipo de usuário"),
) -> List[UserResponse]:
    """Lista todos os usuários do sistema.

    **Requer:** administrador (RN06).
    """
    try:
        registros = ctrl.listar_usuarios(tipo=tipo, solicitante_tipo=usuario["tipo"])
        return [UserResponse(**r) for r in registros]
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Dados do usuário logado",
)
def meu_perfil(
    usuario: CurrentUser,
    ctrl: UserCtrl,
) -> UserResponse:
    """Retorna os dados do usuário autenticado."""
    registro = ctrl.obter_por_id(usuario["user_id"])
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return UserResponse(**registro)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obter usuário por ID",
)
def obter_usuario(
    user_id: str,
    usuario: AdminUser,
    ctrl: UserCtrl,
) -> UserResponse:
    """Retorna os dados de um usuário específico. **Requer:** administrador."""
    registro = ctrl.obter_por_id(user_id)
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return UserResponse(**registro)


@router.patch(
    "/{user_id}/status",
    summary="Alterar status de usuário (RN06)",
    status_code=status.HTTP_200_OK,
)
def alterar_status(
    user_id: str,
    body: UserStatusUpdate,
    usuario: AdminUser,
    ctrl: UserCtrl,
) -> dict:
    """Ativa, inativa ou bloqueia um usuário.

    **Requer:** administrador (RN06).
    Status válidos: `ativo`, `inativo`, `bloqueado`.
    """
    try:
        ok = ctrl.alterar_status(user_id, body.status, solicitante_tipo=usuario["tipo"])
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
        return {"sucesso": True, "user_id": user_id, "novo_status": body.status}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
