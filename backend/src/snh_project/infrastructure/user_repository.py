"""Repositório de Usuario — persistência em JSON."""

from typing import Any, Dict, List, Optional

from .json_repository import JsonRepository
from .serializers import dict_to_usuario, hash_senha, usuario_to_dict, verificar_senha
from ..core.user import TipoUsuario, Usuario


class UserRepository(JsonRepository):
    """
    Repositório de Usuario com persistência em JSON.

    Gerencia autenticação, cadastro e busca de usuários.
    Senhas são armazenadas como hash SHA-256 (nunca em texto puro).
    """

    def __init__(self, filepath: str = "data/users.json") -> None:
        """
        Args:
            filepath: Caminho do arquivo JSON de usuários.
        """
        super().__init__(filepath)

    def salvar_usuario(
        self,
        usuario: Usuario,
        senha: str,
        id_: Optional[str] = None,
    ) -> str:
        """Persiste um Usuario com senha hasheada.

        Args:
            usuario: Objeto Usuario a salvar.
            senha: Senha em texto puro (será hasheada antes de salvar).
            id_: UUID opcional (gerado automaticamente se None).

        Returns:
            UUID string do registro salvo.

        Raises:
            ValueError: Se CPF ou e-mail já existirem no repositório.
        """
        # Unicidade de CPF e e-mail
        if self.buscar_por_cpf(usuario.cpf):
            raise ValueError(f"CPF '{usuario.cpf}' já cadastrado.")
        if self.buscar_por_email(usuario.email):
            raise ValueError(f"E-mail '{usuario.email}' já cadastrado.")

        novo_id = id_ or self._novo_id()
        record = usuario_to_dict(usuario, novo_id, hash_senha(senha))
        self.save(record)
        return novo_id

    def buscar_por_cpf(self, cpf: str) -> Optional[Dict[str, Any]]:
        """Busca registro de usuário pelo CPF.

        Args:
            cpf: CPF com ou sem formatação (só dígitos na comparação).

        Returns:
            Dicionário do registro ou None se não encontrado.
        """
        cpf_limpo = "".join(c for c in cpf if c.isdigit())
        return next(
            (r for r in self.find_all() if r.get("cpf") == cpf_limpo),
            None,
        )

    def buscar_por_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Busca registro de usuário pelo e-mail.

        Args:
            email: E-mail do usuário.

        Returns:
            Dicionário do registro ou None se não encontrado.
        """
        email_lower = email.strip().lower()
        return next(
            (r for r in self.find_all() if r.get("email", "").lower() == email_lower),
            None,
        )

    def autenticar(self, email: str, senha: str) -> Optional[Dict[str, Any]]:
        """Verifica credenciais e retorna o registro do usuário se válidas.

        Implementa RN08: autenticação obrigatória.

        Args:
            email: E-mail do usuário.
            senha: Senha em texto puro.

        Returns:
            Dicionário do registro se autenticado, None se credenciais inválidas.
        """
        registro = self.buscar_por_email(email)
        if not registro:
            return None
        if registro.get("status") == "bloqueado":
            return None
        if not verificar_senha(senha, registro.get("senha_hash", "")):
            return None
        return registro

    def listar_por_tipo(self, tipo: str) -> List[Dict[str, Any]]:
        """Lista usuários de um tipo específico.

        Args:
            tipo: Tipo de usuário (ex: 'nutricionista', 'copeiro').

        Returns:
            Lista de registros do tipo especificado.
        """
        return self.find_all_by_field("tipo", tipo)

    def reconstruir_usuario(self, id_: str) -> Optional[Usuario]:
        """Reconstrói um objeto Usuario a partir do JSON.

        Args:
            id_: UUID do usuário.

        Returns:
            Instância de Usuario ou None se não encontrado.
        """
        registro = self.find_by_id(id_)
        if not registro:
            return None
        return dict_to_usuario(registro)

    def alterar_status(self, id_: str, novo_status: str) -> bool:
        """Altera o status de um usuário diretamente no JSON.

        Args:
            id_: UUID do usuário.
            novo_status: 'ativo', 'inativo' ou 'bloqueado'.

        Returns:
            True se alterado, False se não encontrado.
        """
        registro = self.find_by_id(id_)
        if not registro:
            return False
        registro["status"] = novo_status
        self.save(registro)
        return True
