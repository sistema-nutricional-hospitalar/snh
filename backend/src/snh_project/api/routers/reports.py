"""Router de Relatórios — geração e exportação (US13, US14)."""

from typing import Optional

from fastapi import APIRouter, Query, Response, status

from ..dependencies import CurrentUser, ReportCtrl
from ..schemas.report import ReportResponse

router = APIRouter(prefix="/reports", tags=["Relatórios"])


@router.get(
    "/dietas",
    response_model=ReportResponse,
    summary="Relatório de prescrições (US13, RN09)",
)
def relatorio_dietas(
    usuario: CurrentUser,
    ctrl: ReportCtrl,
    data_inicio: Optional[str] = Query(None, description="Data inicial YYYY-MM-DD"),
    data_fim: Optional[str] = Query(None, description="Data final YYYY-MM-DD"),
    setor_nome: Optional[str] = Query(None, description="Filtrar por setor"),
    tipo_dieta: Optional[str] = Query(None, description="oral | enteral | parenteral | mista"),
    apenas_ativas: bool = Query(False, description="Somente prescrições ativas"),
) -> ReportResponse:
    """Gera relatório de prescrições com filtros flexíveis.

    **RN09:** suporta filtros por data, setor e tipo de dieta.
    **Requer:** qualquer usuário autenticado.
    """
    resultado = ctrl.gerar_relatorio_dietas(
        data_inicio=data_inicio,
        data_fim=data_fim,
        setor_nome=setor_nome,
        tipo_dieta=tipo_dieta,
        apenas_ativas=apenas_ativas,
    )
    return ReportResponse(**resultado)


@router.get(
    "/dietas/export",
    summary="Exportar relatório de dietas como JSON (US14)",
)
def exportar_relatorio_dietas(
    usuario: CurrentUser,
    ctrl: ReportCtrl,
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    setor_nome: Optional[str] = Query(None),
    tipo_dieta: Optional[str] = Query(None),
    apenas_ativas: bool = Query(False),
) -> Response:
    """Exporta o relatório de prescrições como arquivo JSON para download.

    **US14:** exportação do relatório diário.
    """
    relatorio = ctrl.gerar_relatorio_dietas(
        data_inicio=data_inicio,
        data_fim=data_fim,
        setor_nome=setor_nome,
        tipo_dieta=tipo_dieta,
        apenas_ativas=apenas_ativas,
    )
    json_str = ctrl.exportar_json(relatorio)
    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=relatorio_dietas.json"},
    )


@router.get(
    "/evolucao/{patient_id}",
    summary="Evolução nutricional do paciente (US14)",
)
def evolucao_paciente(
    patient_id: str,
    usuario: CurrentUser,
    ctrl: ReportCtrl,
) -> dict:
    """Gera relatório de evolução nutricional de um paciente específico.

    Inclui histórico completo de todas as prescrições e alterações.
    **US14:** rastreabilidade nutricional por paciente.
    """
    return ctrl.gerar_relatorio_evolucao_paciente(patient_id)


@router.get(
    "/alteracoes",
    summary="Relatório de alterações de dieta (US13, RNF06)",
)
def relatorio_alteracoes(
    usuario: CurrentUser,
    ctrl: ReportCtrl,
    data_inicio: Optional[str] = Query(None, description="Data inicial YYYY-MM-DD"),
    data_fim: Optional[str] = Query(None, description="Data final YYYY-MM-DD"),
    setor_nome: Optional[str] = Query(None, description="Filtrar por setor"),
) -> dict:
    """Gera relatório de todas as alterações de dieta realizadas.

    **US13:** auditoria de alterações.
    **RNF06:** rastreabilidade com responsável e timestamp.
    """
    return ctrl.gerar_relatorio_alteracoes(
        data_inicio=data_inicio,
        data_fim=data_fim,
        setor_nome=setor_nome,
    )
