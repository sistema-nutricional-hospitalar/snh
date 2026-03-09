"""
Controller de Paciente — coordena domínio, repositório e validações de negócio.

Implementa os casos de uso: US01, US02, US03.
Aplica regras: RN01 (campos obrigatórios), RN04 (confirmação antes de excluir).
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from ..infrastructure.serializers import _parse_datetime
from ..core.patient import Paciente
from ..infrastructure.patient_repository import PatientRepository
from ..infrastructure.setor_repository import SetorRepository
from ..infrastructure.serializers import paciente_to_dict


class PatientController:
    """Coordena operações de paciente entre domínio, repositório e regras de negócio."""

    def __init__(
        self,
        patient_repo: Optional[PatientRepository] = None,
        setor_repo: Optional[SetorRepository] = None,
        data_dir: str = "data",
    ) -> None:
        self._patient_repo = patient_repo or PatientRepository(f"{data_dir}/patients.json")
        self._setor_repo   = setor_repo   or SetorRepository(f"{data_dir}/setores.json")

    def cadastrar(self, dados: Dict[str, Any], usuario_responsavel: str = "sistema") -> Dict[str, Any]:
        """Cadastra um novo paciente (RN01).

        Aceita tanto o payload legado (setor_nome + leito int) quanto o payload
        do frontend React (setor_id + quarto + leito string).
        """
        if not dados.get("nome", "").strip():
            raise ValueError("Campo obrigatório não preenchido: nome")

        # ── Resolve setor ──────────────────────────────────────────────────────
        setor_nome = dados.get("setor_nome") or dados.get("setor_id") or "Geral"
        setor_id, setor = self._setor_repo.obter_ou_criar(setor_nome)

        # ── Resolve datas ──────────────────────────────────────────────────────
        data_nasc = (
            dados.get("data_nasc")
            or dados.get("data_nascimento")
            or "1900-01-01"
        )
        data_internacao = dados.get("data_internacao") or date.today().isoformat()

        # ── Resolve leito (int) ────────────────────────────────────────────────
        leito_raw = dados.get("leito", 1)
        try:
            leito_int = int(leito_raw)
        except (ValueError, TypeError):
            leito_int = 1

        paciente = Paciente(
            nome=dados["nome"].strip(),
            dataNasc=data_nasc,
            setorClinico=setor,
            leito=leito_int,
            datain=_parse_datetime(data_internacao),
            risco=bool(dados.get("risco", False)),
        )

        patient_id = self._patient_repo.salvar_paciente(paciente, setor_id)

        # ── Persiste campos extras do frontend (não no domínio, mas no JSON) ──
        extras: Dict[str, Any] = {}
        for campo in ("quarto", "sexo", "peso_atual", "altura", "diagnostico",
                      "observacoes", "alergias", "restricoes_alimentares"):
            if campo in dados and dados[campo] is not None:
                extras[campo] = dados[campo]
        if extras:
            self._patient_repo.atualizar_campos(patient_id, extras)

        registro = self._patient_repo.find_by_id(patient_id) or {}
        return {**registro, "setor_nome": setor.nome}

    def listar(self, setor_nome: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista pacientes, opcionalmente filtrados por setor (US02)."""
        setores_map = {r["id"]: r["nome"] for r in self._setor_repo.find_all()}

        if setor_nome:
            registro_setor = self._setor_repo.buscar_setor_por_nome(setor_nome)
            if not registro_setor:
                return []
            registros = self._patient_repo.listar_por_setor(registro_setor["id"])
        else:
            registros = self._patient_repo.find_all()

        return [
            {**r, "setor_nome": setores_map.get(r.get("setor_id", ""), "Desconhecido")}
            for r in registros
        ]

    def obter_por_id(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Retorna dados de um paciente pelo ID."""
        registro = self._patient_repo.find_by_id(patient_id)
        if not registro:
            return None
        setores_map = {r["id"]: r["nome"] for r in self._setor_repo.find_all()}
        return {**registro, "setor_nome": setores_map.get(registro.get("setor_id", ""), "Desconhecido")}

    def editar(self, patient_id: str, dados: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza informações de um paciente existente (US03)."""
        if not self._patient_repo.find_by_id(patient_id):
            return None

        campos: Dict[str, Any] = {}
        for campo_simples in ("nome", "data_nasc", "risco", "data_internacao",
                              "sexo", "peso_atual", "altura", "diagnostico",
                              "observacoes", "alergias", "restricoes_alimentares",
                              "quarto"):
            if campo_simples in dados and dados[campo_simples] is not None:
                v = dados[campo_simples]
                if campo_simples == "nome":
                    v = str(v).strip()
                elif campo_simples == "risco":
                    v = bool(v)
                campos[campo_simples] = v

        if "leito" in dados and dados["leito"] is not None:
            try:
                campos["leito"] = int(dados["leito"])
            except (ValueError, TypeError):
                campos["leito"] = dados["leito"]

        setor_nome = dados.get("setor_nome") or dados.get("setor_id")
        if setor_nome:
            setor_id, _ = self._setor_repo.obter_ou_criar(setor_nome)
            campos["setor_id"] = setor_id

        return self._patient_repo.atualizar_campos(patient_id, campos)

    def excluir(self, patient_id: str, confirmar: bool = False) -> Dict[str, Any]:
        """Remove paciente do sistema com confirmação obrigatória (RN04)."""
        if not confirmar:
            return {"sucesso": False, "motivo": "confirmacao_necessaria"}
        if not self._patient_repo.find_by_id(patient_id):
            return {"sucesso": False, "motivo": "nao_encontrado"}
        self._patient_repo.delete(patient_id)
        return {"sucesso": True, "id": patient_id}

    def buscar_por_nome(self, nome: str) -> List[Dict[str, Any]]:
        """Busca pacientes pelo nome (parcial, case-insensitive)."""
        setores_map = {r["id"]: r["nome"] for r in self._setor_repo.find_all()}
        registros = self._patient_repo.buscar_por_nome(nome)
        return [
            {**r, "setor_nome": setores_map.get(r.get("setor_id", ""), "Desconhecido")}
            for r in registros
        ]

    def reconstruir_paciente_e_setor(self, patient_id: str) -> Optional[tuple]:
        """Reconstrói objetos de domínio para uso nos controllers de prescrição."""
        setores_map = self._setor_repo.listar_setores_dominio()
        result = self._patient_repo.reconstruir_paciente(patient_id, setores_map)
        if not result:
            return None
        paciente, setor_id = result
        setor = setores_map.get(setor_id)
        return paciente, setor, setor_id
