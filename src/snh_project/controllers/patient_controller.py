"""
Controller de Paciente — coordena domínio, repositório e validações de negócio.

Implementa os casos de uso: US01, US02, US03.
Aplica regras: RN01 (campos obrigatórios), RN04 (confirmação antes de excluir).
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from ..infrastructure.serializers import _parse_datetime
from ..core.patient import Paciente
from ..core.setorclin import SetorClinico
from ..infrastructure.patient_repository import PatientRepository
from ..infrastructure.setor_repository import SetorRepository
from ..infrastructure.serializers import paciente_to_dict

CAMPOS_OBRIGATORIOS = ["nome", "data_nasc", "setor_nome", "leito", "data_internacao"]


class PatientController:
    """
    Coordena operações de paciente entre domínio, repositório e regras de negócio.

    Responsabilidades:
        - Validar campos obrigatórios antes de criar objetos de domínio
        - Delegar persistência ao PatientRepository
        - Gerenciar SetorClinico via SetorRepository
        - Aplicar regras de negócio (RN01, RN04)

    Atributos:
        _patient_repo: Repositório de pacientes
        _setor_repo: Repositório de setores clínicos
    """

    def __init__(
        self,
        patient_repo: Optional[PatientRepository] = None,
        setor_repo: Optional[SetorRepository] = None,
        data_dir: str = "data",
    ) -> None:
        """
        Args:
            patient_repo: Repositório de pacientes (cria padrão se None).
            setor_repo: Repositório de setores (cria padrão se None).
            data_dir: Diretório base dos arquivos JSON.
        """
        self._patient_repo = patient_repo or PatientRepository(f"{data_dir}/patients.json")
        self._setor_repo = setor_repo or SetorRepository(f"{data_dir}/setores.json")

    def cadastrar(self, dados: Dict[str, Any], usuario_responsavel: str = "sistema") -> Dict[str, Any]:
        """Cadastra um novo paciente com validação de campos obrigatórios (RN01).

        Args:
            dados: nome, data_nasc, setor_nome, leito, data_internacao obrigatórios.
            usuario_responsavel: Usuário realizando o cadastro.

        Returns:
            Dicionário com dados do paciente cadastrado + 'id' e 'setor_nome'.

        Raises:
            ValueError: Se campos faltando ou leito ocupado.
        """
        self._validar_campos_obrigatorios(dados, CAMPOS_OBRIGATORIOS)

        setor_id, setor = self._setor_repo.obter_ou_criar(dados["setor_nome"])

        paciente = Paciente(
            nome=dados["nome"],
            dataNasc=dados["data_nasc"],
            setorClinico=setor,
            leito=int(dados["leito"]),
            datain=_parse_datetime(dados["data_internacao"]),
            risco=bool(dados.get("risco", False)),
        )

        patient_id = self._patient_repo.salvar_paciente(paciente, setor_id)

        return {
            **paciente_to_dict(paciente, patient_id, setor_id),
            "setor_nome": setor.nome,
        }

    def listar(self, setor_nome: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista pacientes, opcionalmente filtrados por setor (US02).

        Args:
            setor_nome: Nome do setor para filtrar (None retorna todos).

        Returns:
            Lista de dicionários com dados dos pacientes + 'setor_nome'.
        """
        setores_records = {r["id"]: r["nome"] for r in self._setor_repo.find_all()}

        if setor_nome:
            registro_setor = self._setor_repo.buscar_setor_por_nome(setor_nome)
            if not registro_setor:
                return []
            registros = self._patient_repo.listar_por_setor(registro_setor["id"])
        else:
            registros = self._patient_repo.find_all()

        resultado = []
        for r in registros:
            r_copy = dict(r)
            r_copy["setor_nome"] = setores_records.get(r.get("setor_id", ""), "Desconhecido")
            resultado.append(r_copy)
        return resultado

    def obter_por_id(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Retorna dados de um paciente pelo ID.

        Args:
            patient_id: UUID do paciente.

        Returns:
            Dicionário com dados + 'setor_nome' ou None se não encontrado.
        """
        registro = self._patient_repo.find_by_id(patient_id)
        if not registro:
            return None
        setores_records = {r["id"]: r["nome"] for r in self._setor_repo.find_all()}
        registro["setor_nome"] = setores_records.get(registro.get("setor_id", ""), "Desconhecido")
        return registro

    def editar(self, patient_id: str, dados: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza informações de um paciente existente (US03).

        Args:
            patient_id: UUID do paciente.
            dados: Campos a atualizar (nome, data_nasc, leito, risco, setor_nome).

        Returns:
            Registro atualizado ou None se não encontrado.
        """
        if not self._patient_repo.find_by_id(patient_id):
            return None

        campos = {}
        if "nome" in dados and dados["nome"].strip():
            campos["nome"] = dados["nome"].strip()
        if "data_nasc" in dados:
            campos["data_nasc"] = dados["data_nasc"]
        if "risco" in dados:
            campos["risco"] = bool(dados["risco"])
        if "leito" in dados:
            campos["leito"] = int(dados["leito"])
        if "data_internacao" in dados:
            campos["data_internacao"] = dados["data_internacao"]
        if "setor_nome" in dados:
            setor_id, _ = self._setor_repo.obter_ou_criar(dados["setor_nome"])
            campos["setor_id"] = setor_id

        return self._patient_repo.atualizar_campos(patient_id, campos)

    def excluir(self, patient_id: str, confirmar: bool = False) -> Dict[str, Any]:
        """Remove paciente do sistema com confirmação obrigatória (RN04).

        Args:
            patient_id: UUID do paciente.
            confirmar: Deve ser True para efetivar a exclusão.

        Returns:
            Dict com 'sucesso' e 'motivo' descrevendo o resultado.
        """
        if not confirmar:
            return {
                "sucesso": False,
                "motivo": "confirmacao_necessaria",
                "mensagem": "Passe confirmar=True para efetivar a exclusão.",
            }
        if not self._patient_repo.find_by_id(patient_id):
            return {"sucesso": False, "motivo": "nao_encontrado"}
        self._patient_repo.delete(patient_id)
        return {"sucesso": True, "id": patient_id}

    def buscar_por_nome(self, nome: str) -> List[Dict[str, Any]]:
        """Busca pacientes pelo nome (parcial, case-insensitive)."""
        setores_records = {r["id"]: r["nome"] for r in self._setor_repo.find_all()}
        registros = self._patient_repo.buscar_por_nome(nome)
        for r in registros:
            r["setor_nome"] = setores_records.get(r.get("setor_id", ""), "Desconhecido")
        return registros

    def reconstruir_paciente_e_setor(
        self, patient_id: str
    ) -> Optional[tuple]:
        """Reconstrói objetos de domínio para uso nos controllers de prescrição.

        Args:
            patient_id: UUID do paciente.

        Returns:
            Tupla (Paciente, SetorClinico, setor_id) ou None.
        """
        setores_map = self._setor_repo.listar_setores_dominio()
        result = self._patient_repo.reconstruir_paciente(patient_id, setores_map)
        if not result:
            return None
        paciente, setor_id = result
        setor = setores_map.get(setor_id)
        return paciente, setor, setor_id

    @staticmethod
    def _validar_campos_obrigatorios(dados: Dict, campos: List[str]) -> None:
        """Valida presença e não-vazio de campos obrigatórios (RN01)."""
        faltando = [
            c for c in campos
            if c not in dados or dados[c] is None or str(dados[c]).strip() == ""
        ]
        if faltando:
            raise ValueError(f"Campos obrigatórios não preenchidos: {', '.join(faltando)}")