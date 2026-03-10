"""Router de Notificações — leitura e marcação (US07, US09)."""

from typing import List, Optional
import os

from fastapi import APIRouter, HTTPException, status

from ..dependencies import CurrentUser, CopOuNutriUser
from ...infrastructure.notification_repository import NotificationRepository

router = APIRouter(prefix="/notifications", tags=["Notificações"])

DATA_DIR = os.getenv("SNH_DATA_DIR", "data")


def _get_repo() -> NotificationRepository:
    return NotificationRepository(f"{DATA_DIR}/notifications.json")


@router.get(
    "",
    summary="Listar notificações do usuário (US07)",
)
def listar_notificacoes(
    usuario: CopOuNutriUser,
    apenas_nao_lidas: bool = True,
) -> List[dict]:
    """Retorna notificações do usuário autenticado.

    **US07:** copeiro visualiza notificações de alterações de dieta.
    **Requer:** copeiro, nutricionista ou administrador.
    """
    repo = _get_repo()
    destinatario = usuario.get("email", usuario.get("user_id", ""))

    if apenas_nao_lidas:
        return repo.listar_nao_lidas(destinatario)
    return repo.listar_por_destinatario(destinatario)


@router.get(
    "/count",
    summary="Contagem de notificações não lidas",
)
def contar_nao_lidas(usuario: CopOuNutriUser) -> dict:
    """Retorna o número de notificações não lidas.

    Útil para o badge de notificações no frontend.
    """
    repo = _get_repo()
    destinatario = usuario.get("email", usuario.get("user_id", ""))
    return {"nao_lidas": repo.contar_nao_lidas(destinatario)}


@router.patch(
    "/{notif_id}/read",
    summary="Marcar notificação como lida",
    status_code=status.HTTP_200_OK,
)
def marcar_lida(
    notif_id: str,
    usuario: CopOuNutriUser,
) -> dict:
    """Marca uma notificação específica como lida."""
    repo = _get_repo()
    ok = repo.marcar_lida(notif_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificação não encontrada.")
    return {"sucesso": True, "id": notif_id}


@router.patch(
    "/read-all",
    summary="Marcar todas as notificações como lidas",
    status_code=status.HTTP_200_OK,
)
def marcar_todas_lidas(usuario: CopOuNutriUser) -> dict:
    """Marca todas as notificações não lidas do usuário como lidas."""
    repo = _get_repo()
    destinatario = usuario.get("email", usuario.get("user_id", ""))
    quantidade = repo.marcar_todas_lidas(destinatario)
    return {"sucesso": True, "marcadas": quantidade}
