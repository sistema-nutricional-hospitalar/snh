"""
Controller de Usuário — gerencia autenticação e administração de usuários.

Implementa os casos de uso: US15, US16.
Aplica regras: RN06 (somente admin gerencia permissões), RN08 (autenticação obrigatória).
"""

from typing import Any, Dict, List, Optional

from ..core.user import (
    Administrador, Copeiro, Enfermeiro, Medico, Nutricionista, TipoUsuario
)
from ..infrastructure.user_repository import UserRepository


# Campos obrigatórios para criar usuário
CAMPOS_OBRIGATORIOS_USUARIO = ["nome", "cpf", "email", "tipo", "senha"]


class UserController:
    """
    Gerencia autenticação e cadastro de usuários do sistema.

    Responsabilidades:
        - Autenticar usuários (RN08)
        - Criar e listar usuários (US15, US16)
        - Restringir operações administrativas por perfil (RN06)

    Atributos:
        _user_repo: Repositório de usuários
    """

    def __init__(
        self,
        user_repo: Optional[UserRepository] = None,
        data_dir: str = "data",
    ) -> None:
        """
        Args:
            user_repo: Repositório de usuários (cria padrão se None).
            data_dir: Diretório base dos arquivos JSON.
        """
        self._user_repo = user_repo or UserRepository(f"{data_dir}/users.json")

    # -------------------------------------------------------------------------
    # US16 — Autenticação
    # -------------------------------------------------------------------------

    def autenticar(self, email: str, senha: str) -> Optional[Dict[str, Any]]:
        """Valida credenciais e retorna dados do usuário autenticado.

        Implementa US16 e RN08.

        Args:
            email: E-mail do usuário.
            senha: Senha em texto puro.

        Returns:
            Dicionário com dados do usuário (sem senha_hash) ou None se inválido.
        """
        registro = self._user_repo.autenticar(email, senha)
        if not registro:
            return None

        # Nunca retorna senha_hash
        return {k: v for k, v in registro.items() if k != "senha_hash"}

    # -------------------------------------------------------------------------
    # US15 — Cadastrar usuário (somente admin — RN06)
    # -------------------------------------------------------------------------

    def cadastrar_usuario(
        self,
        dados: Dict[str, Any],
        solicitante_tipo: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Cadastra um novo usuário no sistema.

        Implementa US15 e RN06 (somente administrador pode criar usuários).

        Args:
            dados: Dados do usuário. Obrigatórios: nome, cpf, email, tipo, senha.
                   Opcionais por tipo: crn (nutricionista), crm+especialidade (medico),
                   coren+setor (enfermeiro), turno (copeiro).
            solicitante_tipo: Tipo do usuário fazendo a solicitação.
                              Se fornecido, valida que é 'administrador'.

        Returns:
            Dicionário com dados do usuário criado (sem senha).

        Raises:
            PermissionError: Se solicitante não for administrador.
            ValueError: Se campos obrigatórios faltando ou CPF/e-mail duplicado.
        """
        # RN06: somente admin gerencia permissões
        if solicitante_tipo and solicitante_tipo != "administrador":
            raise PermissionError("Somente administradores podem cadastrar usuários.")

        self._validar_campos_obrigatorios(dados, CAMPOS_OBRIGATORIOS_USUARIO)

        tipo = dados["tipo"].lower()
        extras = dados.get("dados_extras", {})

        mapa_factory = {
            "nutricionista": lambda: Nutricionista(
                nome=dados["nome"],
                cpf=dados["cpf"],
                email=dados["email"],
                crn=extras.get("crn", dados.get("crn", "000")),
            ),
            "medico": lambda: Medico(
                nome=dados["nome"],
                cpf=dados["cpf"],
                email=dados["email"],
                crm=extras.get("crm", dados.get("crm", "000")),
                especialidade=extras.get("especialidade", dados.get("especialidade", "")),
            ),
            "enfermeiro": lambda: Enfermeiro(
                nome=dados["nome"],
                cpf=dados["cpf"],
                email=dados["email"],
                coren=extras.get("coren", dados.get("coren", "000")),
                setor=extras.get("setor", dados.get("setor_trabalho", "")),
            ),
            "copeiro": lambda: Copeiro(
                nome=dados["nome"],
                cpf=dados["cpf"],
                email=dados["email"],
                turno=extras.get("turno", dados.get("turno", "manhã")),
            ),
            "administrador": lambda: Administrador(
                nome=dados["nome"],
                cpf=dados["cpf"],
                email=dados["email"],
            ),
        }

        factory_fn = mapa_factory.get(tipo)
        if not factory_fn:
            raise ValueError(
                f"Tipo de usuário inválido: '{tipo}'. "
                f"Válidos: {', '.join(mapa_factory.keys())}"
            )

        usuario = factory_fn()
        user_id = self._user_repo.salvar_usuario(usuario, dados["senha"])

        registro = self._user_repo.find_by_id(user_id)
        return {k: v for k, v in registro.items() if k != "senha_hash"}

    # -------------------------------------------------------------------------
    # Listagens (US15)
    # -------------------------------------------------------------------------

    def listar_usuarios(
        self,
        tipo: Optional[str] = None,
        solicitante_tipo: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Lista usuários do sistema.

        Implementa US15. Somente administradores podem listar todos os usuários.

        Args:
            tipo: Filtrar por tipo ('nutricionista', 'copeiro', etc). None = todos.
            solicitante_tipo: Tipo do solicitante (valida permissão admin).

        Returns:
            Lista de dicionários de usuários (sem senha_hash).

        Raises:
            PermissionError: Se solicitante não for administrador.
        """
        if solicitante_tipo and solicitante_tipo != "administrador":
            raise PermissionError("Somente administradores podem listar usuários.")

        if tipo:
            registros = self._user_repo.listar_por_tipo(tipo.lower())
        else:
            registros = self._user_repo.find_all()

        return [{k: v for k, v in r.items() if k != "senha_hash"} for r in registros]

    def obter_por_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retorna dados de um usuário pelo ID (sem senha).

        Args:
            user_id: UUID do usuário.

        Returns:
            Dicionário sem 'senha_hash' ou None se não encontrado.
        """
        registro = self._user_repo.find_by_id(user_id)
        if not registro:
            return None
        return {k: v for k, v in registro.items() if k != "senha_hash"}

    def alterar_status(
        self,
        user_id: str,
        novo_status: str,
        solicitante_tipo: Optional[str] = None,
    ) -> bool:
        """Altera o status de um usuário (ativo/inativo/bloqueado).

        Args:
            user_id: UUID do usuário.
            novo_status: 'ativo', 'inativo' ou 'bloqueado'.
            solicitante_tipo: Tipo do solicitante (valida permissão admin).

        Returns:
            True se alterado com sucesso.

        Raises:
            PermissionError: Se solicitante não for administrador.
            ValueError: Se status inválido.
        """
        if solicitante_tipo and solicitante_tipo != "administrador":
            raise PermissionError("Somente administradores podem alterar status de usuários.")

        status_validos = {"ativo", "inativo", "bloqueado"}
        if novo_status not in status_validos:
            raise ValueError(f"Status inválido: '{novo_status}'. Válidos: {status_validos}")

        return self._user_repo.alterar_status(user_id, novo_status)

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------

    @staticmethod
    def _validar_campos_obrigatorios(dados: Dict, campos: List[str]) -> None:
        """Valida campos obrigatórios."""
        faltando = [
            c for c in campos
            if c not in dados or dados[c] is None or str(dados[c]).strip() == ""
        ]
        if faltando:
            raise ValueError(f"Campos obrigatórios não preenchidos: {', '.join(faltando)}")
