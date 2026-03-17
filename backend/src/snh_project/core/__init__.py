"""
Módulo core do SNH - Domínio do sistema.

Contém as entidades principais do sistema hospitalar.
"""

# Importa de base
from .base import Dieta, AuditoriaMixin, StatusDietaMixin

# Importa de diets (pasta modular)
from .diets import ItemCardapio, DietaOral, DietaEnteral

# Importa a classe de domínio Paciente
from .patient import Paciente

# Importa o SetorClinico do arquivo correto
from .setorclin import SetorClinico

# Importa hierarquia de usuários
from .user import (
    TipoUsuario,
    StatusUsuario,
    Usuario,
    Nutricionista,
    Medico,
    Enfermeiro,
    Copeiro,
    Administrador,
    GerenciadorUsuarios,
)

# Exporta tudo
__all__ = [
    # Base
    'Dieta',
    'AuditoriaMixin',
    'StatusDietaMixin',

    # Dietas
    'ItemCardapio',
    'DietaOral',
    'DietaEnteral',

    # Pacientes
    'Paciente',
    'SetorClinico',

    # Usuários
    'TipoUsuario',
    'StatusUsuario',
    'Usuario',
    'Nutricionista',
    'Medico',
    'Enfermeiro',
    'Copeiro',
    'Administrador',
    'GerenciadorUsuarios',
]
