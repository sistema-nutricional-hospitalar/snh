"""
Módulo core do SNH - Domínio do sistema.

Contém as entidades principais do sistema hospitalar.
"""

# Importa de base
from .base import Dieta, AuditoriaMixin, StatusDietaMixin

# Importa de diets (pasta modular)
from .diets import ItemCardapio, DietaOral, DietaEnteral

# Importa de outros módulos
from .patient import Paciente, SetorClinico
# from .prescription import Prescricao, HistoricoAlteracao

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
]
