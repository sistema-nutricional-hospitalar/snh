"""Repositório de SetorClinico — persistência em JSON."""

from typing import Dict, List, Optional

from .json_repository import JsonRepository
from .serializers import dict_to_setor, setor_to_dict
from ..core.setorclin import SetorClinico


class SetorRepository(JsonRepository):
    """
    Repositório de SetorClinico com persistência em JSON.

    Além das operações CRUD genéricas, fornece métodos específicos
    para busca por nome e reconstrução de objetos de domínio.
    """

    def __init__(self, filepath: str = "data/setores.json") -> None:
        """
        Args:
            filepath: Caminho do arquivo JSON de setores.
        """
        super().__init__(filepath)
        self._id_map: Dict[str, str] = {}  # nome_setor → id

    def salvar_setor(self, setor: SetorClinico, id_: Optional[str] = None) -> str:
        """Persiste um SetorClinico e retorna o ID gerado/usado.

        Args:
            setor: Objeto SetorClinico a salvar.
            id_: UUID opcional (gerado automaticamente se None).

        Returns:
            UUID string do registro salvo.
        """
        record = setor_to_dict(setor, id_ or self._novo_id())
        self.save(record)
        return record["id"]

    def buscar_setor_por_nome(self, nome: str) -> Optional[Dict]:
        """Busca registro de setor pelo nome (case-insensitive).

        Args:
            nome: Nome do setor clínico.

        Returns:
            Dicionário do registro ou None se não encontrado.
        """
        nome_lower = nome.strip().lower()
        return next(
            (r for r in self.find_all() if r["nome"].strip().lower() == nome_lower),
            None,
        )

    def listar_setores_dominio(self) -> Dict[str, SetorClinico]:
        """Reconstrói todos os setores como objetos de domínio.

        Returns:
            Dicionário {id_setor: SetorClinico}.
        """
        return {
            r["id"]: dict_to_setor(r)
            for r in self.find_all()
        }

    def obter_ou_criar(self, nome: str) -> tuple[str, SetorClinico]:
        """Retorna setor existente pelo nome ou cria um novo.

        Útil para garantir que o setor exista antes de cadastrar um paciente.

        Args:
            nome: Nome do setor.

        Returns:
            Tupla (id_setor, SetorClinico).
        """
        registro = self.buscar_setor_por_nome(nome)
        if registro:
            return registro["id"], dict_to_setor(registro)
        setor = SetorClinico(nome)
        novo_id = self.salvar_setor(setor)
        return novo_id, setor
