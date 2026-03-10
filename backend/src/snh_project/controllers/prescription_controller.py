"""
Controller de Prescrição — orquestra domínio, persistência e notificações.

Implementa os casos de uso: US04, US05, US06, US07, US08.
Aplica regras: RN02 (data/hora em alterações), RN03 (notificação automática).
"""

from typing import Any, Dict, List, Optional

from ..core.prescription import Prescricao
from ..infrastructure.patient_repository import PatientRepository
from ..infrastructure.prescription_repository import PrescriptionRepository
from ..infrastructure.setor_repository import SetorRepository
from ..infrastructure.serializers import dict_to_dieta
from ..services.factory import DietaFactory
from ..services.notifier import NotificadorService
from ..services.strategies import NotificacaoInApp


class PrescriptionController:
    """
    Orquestra criação, alteração e consulta de prescrições dietéticas.

    Responsabilidades:
        - Reconstruir objetos de domínio (Paciente, SetorClinico)
        - Criar Prescricao via domínio (que valida, registra histórico e notifica)
        - Persistir via PrescriptionRepository
        - Injetar NotificadorService configurado

    Atributos:
        _prescription_repo: Repositório de prescrições
        _patient_repo: Repositório de pacientes
        _setor_repo: Repositório de setores
        _notificador: Serviço de notificações compartilhado
    """

    def __init__(
        self,
        prescription_repo: Optional[PrescriptionRepository] = None,
        patient_repo: Optional[PatientRepository] = None,
        setor_repo: Optional[SetorRepository] = None,
        notificador: Optional[NotificadorService] = None,
        data_dir: str = "data",
    ) -> None:
        """
        Args:
            prescription_repo: Repositório de prescrições.
            patient_repo: Repositório de pacientes.
            setor_repo: Repositório de setores.
            notificador: Serviço de notificações (cria padrão se None).
            data_dir: Diretório base dos arquivos JSON.
        """
        self._prescription_repo = prescription_repo or PrescriptionRepository(
            f"{data_dir}/prescriptions.json"
        )
        self._patient_repo = patient_repo or PatientRepository(f"{data_dir}/patients.json")
        self._setor_repo = setor_repo or SetorRepository(f"{data_dir}/setores.json")

        if notificador is None:
            self._notificador = NotificadorService()
            self._notificador.registrar_observador(
                "copeiros", NotificacaoInApp(), ["copeiro@hospital.com"]
            )
        else:
            self._notificador = notificador

    def prescrever(
        self,
        patient_id: str,
        tipo_dieta: str,
        dados_dieta: Dict[str, Any],
        usuario_responsavel: str = "sistema",
    ) -> Dict[str, Any]:
        """Cria nova prescrição dietética para um paciente (US04).

        Args:
            patient_id: UUID do paciente.
            tipo_dieta: 'oral', 'enteral', 'parenteral' ou 'mista'.
            dados_dieta: Parâmetros do tipo de dieta para a DietaFactory.
            usuario_responsavel: Nutricionista prescrevendo.

        Returns:
            Resumo da prescrição criada.

        Raises:
            ValueError: Se paciente não encontrado ou dados inválidos.
        """
        paciente, setor, setor_id = self._reconstruir_paciente_e_setor(patient_id)

        if tipo_dieta.lower() == "enteral" and "setor_clinico" not in dados_dieta:
            dados_dieta = {**dados_dieta, "setor_clinico": setor}
        dados_dieta["usuario_responsavel"] = usuario_responsavel

        dieta = DietaFactory.criar_dieta(tipo_dieta, dados_dieta)
        prescricao = Prescricao(
            paciente=paciente,
            dieta=dieta,
            notificador=self._notificador,
            usuario_responsavel=usuario_responsavel,
        )

        prescription_id = self._prescription_repo.salvar_prescricao(
            prescricao, patient_id, setor_id
        )
        return self._resumo(prescricao, prescription_id, patient_id)

    def alterar_dieta(
        self,
        prescription_id: str,
        tipo_dieta: str,
        dados_dieta: Dict[str, Any],
        usuario_responsavel: str = "sistema",
    ) -> Dict[str, Any]:
        """Altera dieta de uma prescrição existente (US05, RN02, RN03).

        Toda alteração: registra data/hora (RN02) + envia notificação (RN03).

        Args:
            prescription_id: UUID da prescrição.
            tipo_dieta: Novo tipo de dieta.
            dados_dieta: Novos parâmetros.
            usuario_responsavel: Quem está alterando.

        Returns:
            Resumo atualizado da prescrição.
        """
        registro = self._prescription_repo.find_by_id(prescription_id)
        if not registro:
            raise ValueError(f"Prescrição '{prescription_id}' não encontrada.")
        if not registro.get("ativa", False):
            raise ValueError("Não é possível alterar uma prescrição encerrada.")

        patient_id = registro["patient_id"]
        setor_id = registro["setor_id"]
        paciente, setor, _ = self._reconstruir_paciente_e_setor(patient_id)
        dieta_atual = dict_to_dieta(registro["dieta"], setor=setor)

        prescricao = Prescricao(
            paciente=paciente,
            dieta=dieta_atual,
            notificador=self._notificador,
            usuario_responsavel=registro["usuario_responsavel"],
        )
        prescricao._id = prescription_id

        # Restaura historico anterior do JSON (evita perda de entradas anteriores)
        historico_anterior = registro.get("historico", [])
        if len(historico_anterior) > 1:
            from ..core.prescription import HistoricoAlteracao
            from datetime import datetime
            prescricao._historico = []
            for h in historico_anterior:
                entrada = HistoricoAlteracao(
                    tipo_alteracao=h["tipo_alteracao"],
                    descricao=h["descricao"],
                    usuario=h["usuario"],
                )
                entrada._data_hora = datetime.fromisoformat(h["data_hora"])
                prescricao._historico.append(entrada)

        if tipo_dieta.lower() == "enteral" and "setor_clinico" not in dados_dieta:
            dados_dieta = {**dados_dieta, "setor_clinico": setor}
        dados_dieta["usuario_responsavel"] = usuario_responsavel
        nova_dieta = DietaFactory.criar_dieta(tipo_dieta, dados_dieta)

        prescricao.alterar_dieta(nova_dieta, usuario=usuario_responsavel)

        self._prescription_repo.atualizar_prescricao(
            prescription_id, prescricao, patient_id, setor_id
        )
        return self._resumo(prescricao, prescription_id, patient_id)

    def obter_historico(self, prescription_id: str) -> List[Dict[str, Any]]:
        """Retorna histórico cronológico de alterações (US06, RN02).

        Returns:
            Lista de registros de histórico ou [] se não encontrado.
        """
        return self._prescription_repo.obter_historico(prescription_id)

    def listar_por_paciente(self, patient_id: str) -> List[Dict[str, Any]]:
        """Lista todas as prescrições de um paciente."""
        return self._prescription_repo.listar_por_paciente(patient_id)

    def listar_dietas_orais_ativas(self) -> List[Dict[str, Any]]:
        """Lista prescrições ativas com dieta oral (US08 — empresa terceirizada)."""
        return [
            r for r in self._prescription_repo.listar_ativas()
            if r.get("dieta", {}).get("tipo") == "oral"
        ]

    def obter_por_id(self, prescription_id: str) -> Optional[Dict[str, Any]]:
        """Retorna dados de uma prescrição pelo ID."""
        return self._prescription_repo.find_by_id(prescription_id)

    def encerrar(self, prescription_id: str, usuario_responsavel: str = "sistema") -> Dict[str, Any]:
        """Encerra uma prescrição ativa."""
        registro = self._prescription_repo.find_by_id(prescription_id)
        if not registro:
            return {"sucesso": False, "motivo": "nao_encontrado"}
        if not registro.get("ativa", False):
            return {"sucesso": False, "motivo": "ja_encerrada"}

        patient_id = registro["patient_id"]
        setor_id = registro["setor_id"]
        paciente, setor, _ = self._reconstruir_paciente_e_setor(patient_id)
        dieta_atual = dict_to_dieta(registro["dieta"], setor=setor)

        prescricao = Prescricao(
            paciente=paciente,
            dieta=dieta_atual,
            notificador=self._notificador,
            usuario_responsavel=registro["usuario_responsavel"],
        )
        prescricao._id = prescription_id
        prescricao.encerrar(usuario=usuario_responsavel)

        self._prescription_repo.atualizar_prescricao(
            prescription_id, prescricao, patient_id, setor_id
        )
        return {"sucesso": True, "id": prescription_id}

    def _reconstruir_paciente_e_setor(self, patient_id: str) -> tuple:
        """Reconstrói Paciente, SetorClinico e setor_id a partir dos repositórios."""
        setores_map = self._setor_repo.listar_setores_dominio()
        result = self._patient_repo.reconstruir_paciente(patient_id, setores_map)
        if not result:
            raise ValueError(f"Paciente '{patient_id}' não encontrado.")
        paciente, setor_id = result
        setor = setores_map.get(setor_id)
        return paciente, setor, setor_id

    @staticmethod
    def _resumo(prescricao: Prescricao, prescription_id: str, patient_id: str) -> Dict[str, Any]:
        """Gera dicionário resumido de retorno para a API."""
        r = prescricao.obter_resumo()
        return {
            "id": prescription_id,
            "patient_id": patient_id,
            "paciente": r["paciente"],
            "setor": r["setor"],
            "dieta_tipo": r["dieta_tipo"],
            "ativa": r["ativa"],
            "total_alteracoes": r["total_alteracoes"],
            "criado_em": r["criado_em"].isoformat()
            if hasattr(r["criado_em"], "isoformat") else str(r["criado_em"]),
            "criado_por": r["criado_por"],
        }
