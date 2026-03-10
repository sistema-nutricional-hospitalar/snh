"""
Módulo core do SNH - Domínio do sistema.

Contém as entidades principais do sistema hospitalar.
"""

# Importa de base
from .base import Dieta, AuditoriaMixin, StatusDietaMixin

# Importa de diets (pasta modular)
from .diets import ItemCardapio, DietaOral, DietaEnteral

# Importa as classes do arquivo de pacientes (usando os nomes reais)
from .patient import PatientResponse, PatientCreate, PatientUpdate

# Importa o SetorClinico do arquivo correto
from .setorclin import SetorClinico

# Cria o "apelido" Paciente para não quebrar o resto do sistema
Paciente = PatientResponse

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

    # Prescrições (quando implementadas)
    'Prescricao',
    'HistoricoAlteracao',

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