"""
Dependências reutilizáveis da FastAPI.

Fornece injeção de dependência para:
- Autenticação via Bearer token (RNF04, RN08)
- Guards de acesso por tipo de usuário (RN06)
- Instâncias dos controllers (compartilhadas por request)

Uso nos routers:
    @router.get("/patients")
    def listar(usuario=Depends(get_current_user)):
        ...

    @router.post("/users")
    def criar(usuario=Depends(require_admin)):
        ...
"""

import os
from typing import Annotated, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .auth import verificar_token
from ..controllers.patient_controller import PatientController
from ..controllers.prescription_controller import PrescriptionController
from ..controllers.report_controller import RelatorioController
from ..controllers.user_controller import UserController

# Esquema de autenticação Bearer
_bearer = HTTPBearer(auto_error=False)

# Diretório de dados — configurável por variável de ambiente
DATA_DIR = os.getenv("SNH_DATA_DIR", "data")


# =============================================================================
# AUTENTICAÇÃO
# =============================================================================

def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_bearer)
    ] = None,
) -> Dict[str, Any]:
    """Extrai e valida o usuário atual a partir do Bearer token.

    Implementa RNF04 (autenticação obrigatória) e RN08.

    Args:
        credentials: Credenciais HTTP Bearer do header Authorization.

    Returns:
        Payload do token com user_id, tipo, nome.

    Raises:
        HTTPException 401: Se token ausente, inválido ou expirado.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verificar_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


CurrentUser = Annotated[Dict[str, Any], Depends(get_current_user)]


# =============================================================================
# GUARDS DE ACESSO POR PERFIL (RN06)
# =============================================================================

def require_nutricionista(usuario: CurrentUser) -> Dict[str, Any]:
    """Garante que o usuário logado é nutricionista ou admin.

    Implementa RN06: somente nutricionistas prescrevem dietas.

    Raises:
        HTTPException 403: Se o tipo não for permitido.
    """
    tipos_permitidos = {"nutricionista", "administrador"}
    if usuario.get("tipo") not in tipos_permitidos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a nutricionistas.",
        )
    return usuario


def require_admin(usuario: CurrentUser) -> Dict[str, Any]:
    """Garante que o usuário logado é administrador.

    Implementa RN06: somente admin gerencia usuários e permissões.

    Raises:
        HTTPException 403: Se o tipo não for administrador.
    """
    if usuario.get("tipo") != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores.",
        )
    return usuario


def require_copeiro_ou_nutricionista(usuario: CurrentUser) -> Dict[str, Any]:
    """Garante que o usuário é copeiro, nutricionista ou admin.

    Usado para endpoints de visualização de dietas (US07, US08).
    """
    tipos_permitidos = {"copeiro", "nutricionista", "administrador"}
    if usuario.get("tipo") not in tipos_permitidos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado.",
        )
    return usuario


NutricionistaUser = Annotated[Dict[str, Any], Depends(require_nutricionista)]
AdminUser = Annotated[Dict[str, Any], Depends(require_admin)]
CopOuNutriUser = Annotated[Dict[str, Any], Depends(require_copeiro_ou_nutricionista)]


# =============================================================================
# INJEÇÃO DE CONTROLLERS
# =============================================================================

def get_patient_ctrl() -> PatientController:
    """Instancia PatientController com data_dir configurado."""
    return PatientController(data_dir=DATA_DIR)


def get_prescription_ctrl() -> PrescriptionController:
    """Instancia PrescriptionController com data_dir configurado."""
    return PrescriptionController(data_dir=DATA_DIR)


def get_report_ctrl() -> RelatorioController:
    """Instancia RelatorioController com data_dir configurado."""
    return RelatorioController(data_dir=DATA_DIR)


def get_user_ctrl() -> UserController:
    """Instancia UserController com data_dir configurado."""
    return UserController(data_dir=DATA_DIR)


PatientCtrl = Annotated[PatientController, Depends(get_patient_ctrl)]
PrescriptionCtrl = Annotated[PrescriptionController, Depends(get_prescription_ctrl)]
ReportCtrl = Annotated[RelatorioController, Depends(get_report_ctrl)]
UserCtrl = Annotated[UserController, Depends(get_user_ctrl)]
