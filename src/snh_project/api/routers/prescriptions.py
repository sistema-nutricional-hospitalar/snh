"""Router de Prescrições — alteração, histórico e encerramento."""

from typing import List

from fastapi import APIRouter, HTTPException, status

from ..dependencies import CurrentUser, NutricionistaUser, CopOuNutriUser, PrescriptionCtrl
from ..schemas.prescription import (
    PrescriptionResponse,
    PrescriptionUpdate,
    HistoricoItem,
)

router = APIRouter(prefix="/prescriptions", tags=["Prescrições"])


@router.get(
    "/{prescription_id}",
    response_model=PrescriptionResponse,
    summary="Obter prescrição por ID",
)
def obter_prescricao(
    prescription_id: str,
    usuario: CurrentUser,
    ctrl: PrescriptionCtrl,
) -> PrescriptionResponse:
    """Retorna os dados de uma prescrição específica."""
    registro = ctrl.obter_por_id(prescription_id)
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescrição não encontrada.")
    return PrescriptionResponse(**registro) if "paciente" in registro else _enriquecer(registro)


@router.put(
    "/{prescription_id}",
    response_model=PrescriptionResponse,
    summary="Alterar dieta (US05, RN02, RN03)",
)
def alterar_dieta(
    prescription_id: str,
    body: PrescriptionUpdate,
    usuario: NutricionistaUser,
    ctrl: PrescriptionCtrl,
) -> PrescriptionResponse:
    """Altera a dieta de uma prescrição ativa.

    **Requer:** nutricionista ou administrador.
    **RN02:** data/hora da alteração registrada automaticamente.
    **RN03:** notificação disparada automaticamente ao copeiro.
    """
    try:
        resultado = ctrl.alterar_dieta(
            prescription_id=prescription_id,
            tipo_dieta=body.tipo_dieta,
            dados_dieta=body.dados_dieta,
            usuario_responsavel=usuario["nome"],
        )
        return PrescriptionResponse(**resultado)
    except ValueError as e:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "não encontrada" in str(e)
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=status_code, detail=str(e))


@router.get(
    "/{prescription_id}/history",
    response_model=List[HistoricoItem],
    summary="Histórico de alterações (US06, RN02)",
)
def obter_historico(
    prescription_id: str,
    usuario: CurrentUser,
    ctrl: PrescriptionCtrl,
) -> List[HistoricoItem]:
    """Retorna o histórico completo de alterações de uma prescrição.

    **RN02:** cada entrada tem data/hora exata e responsável pela alteração.
    """
    historico = ctrl.obter_historico(prescription_id)
    if historico is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescrição não encontrada.")
    return [HistoricoItem(**h) for h in historico]


@router.post(
    "/{prescription_id}/encerrar",
    summary="Encerrar prescrição",
    status_code=status.HTTP_200_OK,
)
def encerrar_prescricao(
    prescription_id: str,
    usuario: NutricionistaUser,
    ctrl: PrescriptionCtrl,
) -> dict:
    """Encerra uma prescrição ativa.

    **Requer:** nutricionista ou administrador.
    """
    resultado = ctrl.encerrar(prescription_id, usuario_responsavel=usuario["nome"])
    if not resultado["sucesso"]:
        motivo = resultado.get("motivo", "")
        if motivo == "nao_encontrado":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescrição não encontrada.")
        if motivo == "ja_encerrada":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Prescrição já está encerrada.")
    return resultado


@router.get(
    "",
    response_model=List[dict],
    summary="Listar dietas orais ativas (US08)",
)
def listar_dietas_orais(
    usuario: CopOuNutriUser,
    ctrl: PrescriptionCtrl,
) -> List[dict]:
    """Lista prescrições ativas com dieta oral.

    Usado pela empresa terceirizada para preparação das refeições (US08).
    **Requer:** copeiro, nutricionista ou administrador.
    """
    return ctrl.listar_dietas_orais_ativas()


def _enriquecer(registro: dict) -> PrescriptionResponse:
    """Adapta registro bruto do JSON para o schema de resposta."""
    return PrescriptionResponse(
        id=registro["id"],
        patient_id=registro["patient_id"],
        paciente=registro.get("paciente", ""),
        setor=registro.get("setor", ""),
        dieta_tipo=registro.get("dieta", {}).get("tipo", ""),
        ativa=registro.get("ativa", False),
        total_alteracoes=len(registro.get("historico", [])),
        criado_em=registro.get("criado_em", ""),
        criado_por=registro.get("usuario_responsavel", ""),
    )
