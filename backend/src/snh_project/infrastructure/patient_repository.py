"""Repositório de Paciente — persistência em JSON."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .json_repository import JsonRepository
from .serializers import dict_to_paciente, paciente_to_dict
from ..core.patient import Paciente
from ..core.setorclin import SetorClinico


class PatientRepository(JsonRepository):
    """
    Repositório de Paciente com persistência em JSON.

    Gerencia a persistência dos dados de pacientes, independente dos
    objetos SetorClinico (que são carregados pelo SetorRepository).

    Os registros são dicionários planos — objetos de domínio são
    reconstruídos sob demanda pelo controller.
    """

    def __init__(self, filepath: str = "data/patients.json") -> None:
        """
        Args:
            filepath: Caminho do arquivo JSON de pacientes.
        """
        super().__init__(filepath)

    def salvar_paciente(
        self,
        paciente: Paciente,
        setor_id: str,
        id_: Optional[str] = None,
    ) -> str:
        """Persiste um Paciente e retorna o ID gerado/usado.

        Args:
            paciente: Objeto Paciente a salvar.
            setor_id: UUID do SetorClinico associado.
            id_: UUID opcional (gerado automaticamente se None).

        Returns:
            UUID string do registro salvo.
        """
        novo_id = id_ or self._novo_id()
        record = paciente_to_dict(paciente, novo_id, setor_id)
        self.save(record)
        return novo_id

    def buscar_por_nome(self, nome: str) -> List[Dict[str, Any]]:
        """Busca registros de pacientes pelo nome (busca parcial, case-insensitive).

        Args:
            nome: Nome ou parte do nome do paciente.

        Returns:
            Lista de registros que correspondem à busca.
        """
        nome_lower = nome.strip().lower()
        return [r for r in self.find_all() if nome_lower in r["nome"].lower()]

    def listar_por_setor(self, setor_id: str) -> List[Dict[str, Any]]:
        """Retorna todos os pacientes de um setor específico.

        Args:
            setor_id: UUID do SetorClinico.

        Returns:
            Lista de registros de pacientes no setor.
        """
        return self.find_all_by_field("setor_id", setor_id)

    def reconstruir_paciente(
        self,
        id_: str,
        setores_map: Dict[str, SetorClinico],
    ) -> Optional[tuple[Paciente, str]]:
        """Reconstrói um objeto Paciente a partir do JSON.

        Args:
            id_: UUID do paciente.
            setores_map: Dicionário {setor_id: SetorClinico} já instanciado.

        Returns:
            Tupla (Paciente, setor_id) ou None se não encontrado.
        """
        registro = self.find_by_id(id_)
        if not registro:
            return None
        setor_id = registro["setor_id"]
        setor = setores_map.get(setor_id)
        if setor is None:
            raise ValueError(f"Setor '{setor_id}' não encontrado no mapa de setores.")
        return dict_to_paciente(registro, setor), setor_id

    def atualizar_campos(self, id_: str, campos: Dict[str, Any]) -> Optional[Dict]:
        """Atualiza campos específicos de um registro de paciente.

        Args:
            id_: UUID do paciente.
            campos: Dicionário com os campos a atualizar.

        Returns:
            Registro atualizado ou None se não encontrado.
        """
        registro = self.find_by_id(id_)
        if not registro:
            return None
        registro.update(campos)
        registro["atualizado_em"] = datetime.now().isoformat()
        self.save(registro)
        return registro
