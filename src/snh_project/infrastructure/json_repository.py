"""
Repositório genérico de persistência em JSON.

Implementa o padrão Repository, isolando o domínio do mecanismo de armazenamento.
Usa arquivos .json como banco de dados simples (key-value por id).
"""

import json
import uuid
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")


class JsonRepository(Generic[T]):
    """
    Repositório base genérico para persistência em arquivo JSON.

    Padrão: Repository — isola o domínio do meio de armazenamento.
    Princípio SOLID: OCP — extensível via subclasses sem modificar esta base.

    Cada registro é um dicionário com campo obrigatório 'id' (UUID string).
    Os dados são carregados e salvos a cada operação (sem cache em memória),
    garantindo consistência entre chamadas.

    Atributos:
        _path: Caminho absoluto do arquivo JSON
    """

    def __init__(self, filepath: str) -> None:
        """
        Inicializa o repositório garantindo que o arquivo exista.

        Args:
            filepath: Caminho do arquivo JSON (cria diretórios se necessário)
        """
        self._path = Path(filepath)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.write_text("[]", encoding="utf-8")

    def _load(self) -> List[Dict[str, Any]]:
        """Carrega todos os registros do arquivo JSON."""
        raw = self._path.read_text(encoding="utf-8-sig").strip()
        if not raw:
            return []
        return json.loads(raw)

    def _save(self, data: List[Dict[str, Any]]) -> None:
        """Salva a lista de registros no arquivo JSON."""
        self._path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

    @staticmethod
    def _novo_id() -> str:
        """Gera um novo UUID único como string."""
        return str(uuid.uuid4())

    def find_all(self) -> List[Dict[str, Any]]:
        """Retorna todos os registros persistidos."""
        return self._load()

    def find_by_id(self, id_: str) -> Optional[Dict[str, Any]]:
        """Busca um registro pelo seu ID."""
        return next((r for r in self._load() if r.get("id") == id_), None)

    def find_by_field(self, campo: str, valor: Any) -> Optional[Dict[str, Any]]:
        """Retorna o PRIMEIRO registro onde campo == valor, ou None."""
        return next((r for r in self._load() if r.get(campo) == valor), None)

    def find_all_by_field(self, campo: str, valor: Any) -> List[Dict[str, Any]]:
        """Retorna TODOS os registros onde campo == valor."""
        return [r for r in self._load() if r.get(campo) == valor]

    def save(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Persiste um registro (insert ou update por ID).

        Se não tiver 'id', gera UUID automaticamente.
        Se já existir registro com mesmo 'id', substitui (update).
        """
        if "id" not in record or not record["id"]:
            record["id"] = self._novo_id()

        data = self._load()
        idx = next(
            (i for i, r in enumerate(data) if r.get("id") == record["id"]),
            None,
        )
        if idx is not None:
            data[idx] = record
        else:
            data.append(record)

        self._save(data)
        return record

    def delete(self, id_: str) -> bool:
        """Remove um registro pelo ID. Retorna True se removido."""
        data = self._load()
        nova_lista = [r for r in data if r.get("id") != id_]
        if len(nova_lista) == len(data):
            return False
        self._save(nova_lista)
        return True

    def count(self) -> int:
        """Retorna total de registros."""
        return len(self._load())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path='{self._path}', total={self.count()})"