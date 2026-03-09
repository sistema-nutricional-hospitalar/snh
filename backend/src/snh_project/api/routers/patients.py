"""Router de Pacientes — CRUD completo + prescrições."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from ..dependencies import (
    CurrentUser, NutricionistaUser,
    PatientCtrl, PrescriptionCtrl,
)
from ..schemas.patient import PatientCreate, PatientResponse, PatientUpdate
from ..schemas.prescription import PrescriptionCreate, PrescriptionResponse

router = APIRouter(prefix="/patients", tags=["Pacientes"])


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar paciente (US01)",
)
def cadastrar_paciente(
    body: PatientCreate,
    usuario: NutricionistaUser,
    ctrl: PatientCtrl,
) -> PatientResponse:
    """Cadastra um novo paciente no sistema.

    **Requer:** nutricionista ou administrador.
    **RN01:** todos os campos são obrigatórios.
    """
    try:
        resultado = ctrl.cadastrar(body.model_dump(), usuario_responsavel=usuario["nome"])
        return PatientResponse(**resultado)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get(
    "",
    response_model=List[PatientResponse],
    summary="Listar pacientes (US02)",
)
def listar_pacientes(
    usuario: CurrentUser,
    ctrl: PatientCtrl,
    setor: Optional[str] = Query(None, description="Filtrar por setor clínico"),
    nome: Optional[str] = Query(None, description="Buscar por nome parcial"),
) -> List[PatientResponse]:
    """Lista todos os pacientes, com filtro opcional por setor ou nome.

    **Requer:** qualquer usuário autenticado.
    """
    if nome:
        registros = ctrl.buscar_por_nome(nome)
    else:
        registros = ctrl.listar(setor_nome=setor)
    return [PatientResponse(**r) for r in registros]


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Obter paciente por ID",
)
def obter_paciente(
    patient_id: str,
    usuario: CurrentUser,
    ctrl: PatientCtrl,
) -> PatientResponse:
    """Retorna os dados de um paciente específico."""
    registro = ctrl.obter_por_id(patient_id)
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado.")
    return PatientResponse(**registro)


@router.put(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Editar paciente (US03)",
)
def editar_paciente(
    patient_id: str,
    body: PatientUpdate,
    usuario: NutricionistaUser,
    ctrl: PatientCtrl,
) -> PatientResponse:
    """Atualiza os dados de um paciente existente.

    **Requer:** nutricionista ou administrador.
    """
    resultado = ctrl.editar(patient_id, body.model_dump(exclude_none=True))
    if not resultado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado.")
    # Recarrega para ter setor_nome
    registro = ctrl.obter_por_id(patient_id)
    return PatientResponse(**registro)


@router.delete(
    "/{patient_id}",
    summary="Excluir paciente (US03, RN04)",
    status_code=status.HTTP_200_OK,
)
def excluir_paciente(
    patient_id: str,
    usuario: NutricionistaUser,
    ctrl: PatientCtrl,
) -> dict:
    """Remove um paciente do sistema.

    **RN04:** a exclusão é irreversível e requer confirmação explícita
    pelo nutricionista (a confirmação é implícita ao chamar este endpoint).
    **Requer:** nutricionista ou administrador.
    """
    resultado = ctrl.excluir(patient_id, confirmar=True)
    if not resultado["sucesso"]:
        if resultado.get("motivo") == "nao_encontrado":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado.")
    return resultado


# =============================================================================
# PRESCRIÇÕES DE UM PACIENTE
# =============================================================================

@router.post(
    "/{patient_id}/prescriptions",
    response_model=PrescriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Prescrever dieta (US04)",
)
def prescrever_dieta(
    patient_id: str,
    body: PrescriptionCreate,
    usuario: NutricionistaUser,
    presc_ctrl: PrescriptionCtrl,
    patient_ctrl: PatientCtrl,
) -> PrescriptionResponse:
    """Cria uma nova prescrição dietética para o paciente.

    **Requer:** nutricionista ou administrador.
    **RN03:** notificação disparada automaticamente ao copeiro.

    Exemplos de `dados_dieta` por tipo:

    - **oral:** `{"textura": "normal", "numero_refeicoes": 3, "tipo_refeicao": "almoco"}`
    - **enteral:** `{"via_infusao": "sng", "velocidade_ml_h": 60.0, "quantidade_gramas_por_porção": 300.0}`
    - **parenteral:** `{"tipo_acesso": "central", "volume_ml_dia": 1500.0, "composicao": "aminoacidos", "velocidade_ml_h": 62.5}`
    """
    if not patient_ctrl.obter_por_id(patient_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado.")
    try:
        resultado = presc_ctrl.prescrever(
            patient_id=patient_id,
            tipo_dieta=body.tipo_dieta,
            dados_dieta=body.dados_dieta,
            usuario_responsavel=usuario["nome"],
        )
        return PrescriptionResponse(**resultado)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get(
    "/{patient_id}/prescriptions",
    response_model=List[PrescriptionResponse],
    summary="Listar prescrições do paciente (US06)",
)
def listar_prescricoes(
    patient_id: str,
    usuario: CurrentUser,
    presc_ctrl: PrescriptionCtrl,
    patient_ctrl: PatientCtrl,
) -> List[PrescriptionResponse]:
    """Lista todas as prescrições de um paciente, em ordem cronológica."""
    if not patient_ctrl.obter_por_id(patient_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado.")
    registros = presc_ctrl.listar_por_paciente(patient_id)
    return [PrescriptionResponse(**r) for r in registros]
