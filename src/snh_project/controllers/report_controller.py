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
    """
    Gera relatórios de auditoria e evolução nutricional do sistema SNH.

    Implementa filtros de RN09: data, setor e tipo de dieta.

    Atributos:
        _prescricao_repo: Repositório de prescrições
        _patient_repo: Repositório de pacientes
        _setor_repo: Repositório de setores
    """

    def __init__(
        self,
        prescricao_repo: Optional[PrescriptionRepository] = None,
        patient_repo: Optional[PatientRepository] = None,
        setor_repo: Optional[SetorRepository] = None,
        data_dir: str = "data",
    ) -> None:
        """
        Args:
            prescricao_repo: Repositório de prescrições
            patient_repo: Repositório de pacientes
            setor_repo: Repositório de setores
            data_dir: Diretório base dos arquivos JSON
        """
        self._prescricao_repo = prescricao_repo or PrescriptionRepository(f"{data_dir}/prescriptions.json")
        self._patient_repo = patient_repo or PatientRepository(f"{data_dir}/patients.json")
        self._setor_repo = setor_repo or SetorRepository(f"{data_dir}/setores.json")

    def gerar_relatorio_dietas(
        self,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        setor: Optional[str] = None,
        tipo_dieta: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Gera relatório de prescrições com filtros (US13, RN09).

        Args:
            data_inicio: ISO date string inicial
            data_fim: ISO date string final
            setor: Nome do setor para filtrar
            tipo_dieta: Tipo de dieta para filtrar

        Returns:
            Dict com filtros, total, lista de prescrições e timestamp
        """
        setor_id = None
        if setor:
            registro = self._setor_repo.buscar_setor_por_nome(setor)
            if registro:
                setor_id = registro["id"]
            else:
                # Setor não existe → resultado vazio
                return {
                    "filtros_aplicados": {"data_inicio": data_inicio, "data_fim": data_fim, "setor": setor, "tipo_dieta": tipo_dieta},
                    "total": 0,
                    "mensagem": "Nenhum dado disponível para os filtros informados",
                    "prescricoes": [],
                    "gerado_em": datetime.now().isoformat(),
                }

        prescricoes = self._prescricao_repo.filtrar(
            data_inicio=data_inicio,
            data_fim=data_fim,
            setor_id=setor_id,
            tipo_dieta=tipo_dieta,
        )

        resultado = []
        for p in prescricoes:
            pr = self._patient_repo.find_by_id(p.get("patient_id", ""))
            resultado.append({
                "prescricao_id": p["id"],
                "paciente_nome": pr["nome"] if pr else "Desconhecido",
                "setor": setor or "",
                "tipo_dieta": p.get("dieta", {}).get("tipo", ""),
                "ativa": p.get("ativa"),
                "criado_em": p.get("criado_em"),
                "total_alteracoes": len(p.get("historico", [])),
                "usuario_responsavel": p.get("usuario_responsavel"),
            })

        if not resultado:
            return {
                "filtros_aplicados": {"data_inicio": data_inicio, "data_fim": data_fim, "setor": setor, "tipo_dieta": tipo_dieta},
                "total": 0,
                "mensagem": "Nenhum dado disponível para os filtros informados",
                "prescricoes": [],
                "gerado_em": datetime.now().isoformat(),
            }

        return {
            "filtros_aplicados": {"data_inicio": data_inicio, "data_fim": data_fim, "setor": setor, "tipo_dieta": tipo_dieta},
            "total": len(resultado),
            "prescricoes": resultado,
            "gerado_em": datetime.now().isoformat(),
        }

    def gerar_relatorio_alteracoes(self, paciente_id: str) -> Dict[str, Any]:
        """
        Gera relatório do histórico de alterações de um paciente (US06, US13).

        Args:
            paciente_id: UUID do paciente

        Returns:
            Dict com histórico completo ordenado cronologicamente

        Raises:
            ValueError: Se paciente não encontrado
        """
        pr = self._patient_repo.find_by_id(paciente_id)
        if pr is None:
            raise ValueError(f"Paciente '{paciente_id}' não encontrado")

        prescricoes = self._prescricao_repo.listar_por_paciente(paciente_id)

        historico: List[Dict] = []
        for p in prescricoes:
            for h in p.get("historico", []):
                historico.append({
                    **h,
                    "prescricao_id": p["id"],
                    "tipo_dieta": p.get("dieta", {}).get("tipo", ""),
                })

        historico.sort(key=lambda h: h.get("data_hora", ""))

        if not historico:
            return {
                "paciente_nome": pr["nome"],
                "paciente_id": paciente_id,
                "total_alteracoes": 0,
                "mensagem": "Nenhuma alteração registrada",
                "historico": [],
                "gerado_em": datetime.now().isoformat(),
            }

        return {
            "paciente_nome": pr["nome"],
            "paciente_id": paciente_id,
            "total_alteracoes": len(historico),
            "historico": historico,
            "gerado_em": datetime.now().isoformat(),
        }

    def exportar_json(self, relatorio: Dict[str, Any]) -> str:
        """
        Exporta relatório como string JSON formatada (US14).

        Args:
            relatorio: Dict do relatório gerado

        Returns:
            String JSON com indentação
        """
        return json.dumps(relatorio, ensure_ascii=False, indent=2, default=str)
