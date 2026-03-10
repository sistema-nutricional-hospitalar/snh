"""Repositório de Prescricao — persistência em JSON."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .json_repository import JsonRepository
from .serializers import prescricao_to_dict, dict_to_dieta, historico_to_dict
from ..core.prescription import Prescricao
from ..core.setorclin import SetorClinico


class PrescriptionRepository(JsonRepository):
    """
    Repositório de Prescricao com persistência em JSON.

    Persiste prescrições com histórico completo de alterações.
    Implementa RN02: data/hora registrada em toda alteração.
    """

    def __init__(self, filepath: str = "data/prescriptions.json") -> None:
        """
        Args:
            filepath: Caminho do arquivo JSON de prescrições.
        """
        super().__init__(filepath)

    def salvar_prescricao(
        self,
        prescricao: Prescricao,
        patient_id: str,
        setor_id: str,
        id_: Optional[str] = None,
    ) -> str:
        """Persiste uma Prescricao e retorna o ID gerado/usado.

        Args:
            prescricao: Objeto Prescricao a salvar.
            patient_id: UUID do Paciente associado.
            setor_id: UUID do SetorClinico (para DietaEnteral).
            id_: UUID opcional (gerado automaticamente se None).

        Returns:
            UUID string do registro salvo.
        """
        novo_id = id_ or self._novo_id()
        record = prescricao_to_dict(prescricao, novo_id, patient_id, setor_id)
        self.save(record)
        return novo_id

    def atualizar_prescricao(
        self,
        id_: str,
        prescricao: Prescricao,
        patient_id: str,
        setor_id: str,
    ) -> bool:
        """Atualiza prescrição existente (dieta + histórico).

        Args:
            id_: UUID da prescrição a atualizar.
            prescricao: Objeto Prescricao com o estado atual.
            patient_id: UUID do Paciente.
            setor_id: UUID do Setor.

        Returns:
            True se atualizado, False se não encontrado.
        """
        if not self.find_by_id(id_):
            return False
        record = prescricao_to_dict(prescricao, id_, patient_id, setor_id)
        self.save(record)
        return True

    def listar_por_paciente(self, patient_id: str) -> List[Dict[str, Any]]:
        """Lista todas as prescrições de um paciente.

        Args:
            patient_id: UUID do Paciente.

        Returns:
            Lista de registros de prescrições (ordenados por criado_em).
        """
        registros = self.find_all_by_field("patient_id", patient_id)
        return sorted(registros, key=lambda r: r.get("criado_em", ""))

    def listar_ativas(self) -> List[Dict[str, Any]]:
        """Retorna todas as prescrições ativas no sistema.

        Returns:
            Lista de prescrições com 'ativa' == True.
        """
        return [r for r in self.find_all() if r.get("ativa", False)]

    def listar_ativas_por_setor(self, setor_id: str) -> List[Dict[str, Any]]:
        """Retorna prescrições ativas de um setor específico.

        Args:
            setor_id: UUID do SetorClinico.

        Returns:
            Lista de prescrições ativas do setor.
        """
        return [
            r for r in self.find_all()
            if r.get("ativa", False) and r.get("setor_id") == setor_id
        ]

    def filtrar(
        self,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        setor_id: Optional[str] = None,
        tipo_dieta: Optional[str] = None,
        apenas_ativas: bool = False,
    ) -> List[Dict[str, Any]]:
        """Filtra prescrições por múltiplos critérios. Implementa RN09.

        Args:
            data_inicio: ISO date string (ex: '2024-01-01').
            data_fim: ISO date string (ex: '2024-12-31').
            setor_id: UUID do setor para filtrar.
            tipo_dieta: Tipo de dieta ('oral', 'enteral', etc).
            apenas_ativas: Se True, retorna apenas prescrições ativas.

        Returns:
            Lista de registros filtrados.
        """
        resultado = self.find_all()

        if apenas_ativas:
            resultado = [r for r in resultado if r.get("ativa", False)]

        if setor_id:
            resultado = [r for r in resultado if r.get("setor_id") == setor_id]

        if tipo_dieta:
            resultado = [
                r for r in resultado
                if r.get("dieta", {}).get("tipo", "").lower() == tipo_dieta.lower()
            ]

        if data_inicio:
            resultado = [
                r for r in resultado
                if r.get("criado_em", "") >= data_inicio
            ]

        if data_fim:
            resultado = [
                r for r in resultado
                if r.get("criado_em", "") <= data_fim + "T23:59:59"
            ]

        return sorted(resultado, key=lambda r: r.get("criado_em", ""))

    def obter_historico(self, id_: str) -> List[Dict[str, Any]]:
        """Retorna o histórico de alterações de uma prescrição.

        Args:
            id_: UUID da prescrição.

        Returns:
            Lista de registros de histórico ordenados cronologicamente (US06).
        """
        registro = self.find_by_id(id_)
        if not registro:
            return []
        historico = registro.get("historico", [])
        return sorted(historico, key=lambda h: h.get("data_hora", ""))
