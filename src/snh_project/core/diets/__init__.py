"""
Módulo de dietas do SNH.

Contém todas as implementações de dietas hospitalares:
- ItemCardapio: Item individual do cardápio
- DietaOral: Dieta via alimentação normal
- DietaEnteral: Dieta via sonda
- DietaParenteral: Dieta intravenosa (pela veia)
- DietaMista: Composição de múltiplas dietas (Padrão Composite)
"""

from .item_cardapio import ItemCardapio
from .dieta_oral import DietaOral
from .dieta_enteral import DietaEnteral
from .dieta_parenteral import DietaParenteral
from .dieta_mista import DietaMista

__all__ = [
    'ItemCardapio',
    'DietaOral',
    'DietaEnteral',
    'DietaParenteral',
    'DietaMista',
]