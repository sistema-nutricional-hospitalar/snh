"""
Controller de Relatórios.

Gera relatórios de auditoria e evolução nutricional (US13, US14).
Aplica filtros de data, setor e tipo de dieta (RN09).
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..infrastructure.patient_repository import PatientRepository
from ..infrastructure.prescription_repository import PrescriptionRepository
from ..infrastructure.setor_repository import SetorRepository


class RelatorioController:
    """Gera relatórios de auditoria e evolução nutricional do sistema SNH."""

    def __init__(
        self,
        prescricao_repo: Optional[PrescriptionRepository] = None,
        patient_repo: Optional[PatientRepository] = None,
        setor_repo: Optional[SetorRepository] = None,
        data_dir: str = "data",
    ) -> None:
        self._prescricao_repo = prescricao_repo or PrescriptionRepository(f"{data_dir}/prescriptions.json")
        self._patient_repo    = patient_repo    or PatientRepository(f"{data_dir}/patients.json")
        self._setor_repo      = setor_repo      or SetorRepository(f"{data_dir}/setores.json")

    # ── Bug 2 fix: aceita setor_nome (nome do router) + apenas_ativas ────────
    def gerar_relatorio_dietas(
        self,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        setor_nome: Optional[str] = None,   # antes era 'setor'
        tipo_dieta: Optional[str] = None,
        apenas_ativas: bool = False,        # antes faltava este param
    ) -> Dict[str, Any]:
        """Gera relatório de prescrições com filtros (US13, RN09)."""

        setor_id = None
        if setor_nome:
            registro = self._setor_repo.buscar_setor_por_nome(setor_nome)
            if registro:
                setor_id = registro["id"]
            else:
                return self._empty_report(data_inicio, data_fim, setor_nome, tipo_dieta)

        prescricoes = self._prescricao_repo.filtrar(
            data_inicio=data_inicio,
            data_fim=data_fim,
            setor_id=setor_id,
            tipo_dieta=tipo_dieta,
            apenas_ativas=apenas_ativas,
        )

        resultado = []
        for p in prescricoes:
            pr = self._patient_repo.find_by_id(p.get("patient_id", ""))
            resultado.append({
                "prescricao_id":       p["id"],
                "paciente_nome":       pr["nome"] if pr else "Desconhecido",
                "setor_nome":          setor_nome or "",
                "tipo_dieta":          p.get("dieta", {}).get("tipo", ""),
                "ativa":               p.get("ativa"),
                "criado_em":           p.get("criado_em"),
                "total_alteracoes":    len(p.get("historico", [])),
                "usuario_responsavel": p.get("usuario_responsavel"),
            })

        if not resultado:
            return self._empty_report(data_inicio, data_fim, setor_nome, tipo_dieta)

        # Bug 2 fix: campo 'filtros' (não 'filtros_aplicados') — alinha com ReportResponse
        return {
            "filtros":          {"data_inicio": data_inicio, "data_fim": data_fim,
                                 "setor_nome": setor_nome, "tipo_dieta": tipo_dieta},
            "total":            len(resultado),
            "resumo_por_tipo":  self._resumo_por_tipo(resultado),
            "prescricoes":      resultado,
            "gerado_em":        datetime.now().isoformat(),
        }

    def _empty_report(self, data_inicio, data_fim, setor_nome, tipo_dieta) -> Dict[str, Any]:
        return {
            "filtros":         {"data_inicio": data_inicio, "data_fim": data_fim,
                                "setor_nome": setor_nome, "tipo_dieta": tipo_dieta},
            "total":           0,
            "resumo_por_tipo": {},
            "prescricoes":     [],
            "gerado_em":       datetime.now().isoformat(),
        }

    def _resumo_por_tipo(self, prescricoes: List[Dict]) -> Dict[str, int]:
        resumo: Dict[str, int] = {}
        for p in prescricoes:
            t = p.get("tipo_dieta", "desconhecido") or "desconhecido"
            resumo[t] = resumo.get(t, 0) + 1
        return resumo

    # ── Bug 3 fix: relatório global de alterações (sem paciente_id) ───────────
    def gerar_relatorio_alteracoes(
        self,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        setor_nome: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Gera relatório global de todas as alterações de dieta (US13, RNF06)."""

        prescricoes = self._prescricao_repo.find_all()

        alteracoes: List[Dict] = []
        for p in prescricoes:
            # filtro por setor
            if setor_nome:
                setor_reg = self._setor_repo.buscar_setor_por_nome(setor_nome)
                if setor_reg and p.get("setor_id") != setor_reg["id"]:
                    continue

            pr = self._patient_repo.find_by_id(p.get("patient_id", ""))
            nome_paciente = pr["nome"] if pr else "Desconhecido"

            for h in p.get("historico", []):
                data_hora = h.get("data_hora", "")

                # filtro por data
                if data_inicio and data_hora < data_inicio:
                    continue
                if data_fim and data_hora[:10] > data_fim:
                    continue

                alteracoes.append({
                    "prescricao_id":    p["id"],
                    "paciente_nome":    nome_paciente,
                    "data":             data_hora,
                    "tipo_alteracao":   h.get("tipo_alteracao", ""),
                    "dieta_anterior":   h.get("descricao", ""),
                    "dieta_nova":       p.get("dieta", {}).get("tipo", ""),
                    "motivo":           h.get("descricao", ""),
                    "usuario":          h.get("usuario", ""),
                })

        alteracoes.sort(key=lambda x: x.get("data", ""), reverse=True)

        return {
            "total_alteracoes": len(alteracoes),
            "urgentes":   0,  # sem campo de prioridade no historico atual
            "notificadas": len(alteracoes),
            "alteracoes": alteracoes,
            "gerado_em":  datetime.now().isoformat(),
        }

    def gerar_relatorio_evolucao_paciente(self, paciente_id: str) -> Dict[str, Any]:
        """Gera relatório de evolução nutricional de um paciente (US14)."""
        pr = self._patient_repo.find_by_id(paciente_id)
        if pr is None:
            return {"sucesso": False, "motivo": "paciente_nao_encontrado", "paciente_id": paciente_id}

        prescricoes = self._prescricao_repo.listar_por_paciente(paciente_id)

        historico: List[Dict] = []
        for p in prescricoes:
            for h in p.get("historico", []):
                historico.append({
                    **h,
                    "prescricao_id": p["id"],
                    "tipo_dieta":    p.get("dieta", {}).get("tipo", ""),
                })

        historico.sort(key=lambda h: h.get("data_hora", ""))

        return {
            "sucesso":           True,
            "paciente":          {"nome": pr["nome"], "id": paciente_id},
            "paciente_id":       paciente_id,
            "total_prescricoes": len(prescricoes),
            "total_alteracoes":  len(historico),
            "historico":         historico,
            "gerado_em":         datetime.now().isoformat(),
        }

    def exportar_json(self, relatorio: Dict[str, Any]) -> str:
        """Exporta relatório como string JSON formatada (US14)."""
        return json.dumps(relatorio, ensure_ascii=False, indent=2, default=str)