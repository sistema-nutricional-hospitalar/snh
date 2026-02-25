"""
Módulo de dietas do SNH.

Contém todas as implementações de dietas hospitalares:
- ItemCardapio: Item individual do cardápio
- DietaOral: Dieta via alimentação normal
- DietaEnteral: Dieta via sonda
"""

from .item_cardapio import ItemCardapio
from .dieta_oral import DietaOral
from .dieta_enteral import DietaEnteral

__all__ = [
    'ItemCardapio',
    'DietaOral',
    'DietaEnteral',
]
