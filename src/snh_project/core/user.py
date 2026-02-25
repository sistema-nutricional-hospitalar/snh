from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from .base import AuditoriaMixin


# ===========================================================================
# ENUMS
# ===========================================================================

class TipoUsuario(Enum):
    """Define os tipos de usuário do sistema SNH."""
    ADMINISTRADOR  = "administrador"
    MEDICO         = "medico"
    NUTRICIONISTA  = "nutricionista"
    ENFERMEIRO     = "enfermeiro"
    COPEIRO        = "copeiro"


class StatusUsuario(Enum):
    """Define os possíveis status de um usuário."""
    ATIVO    = "ativo"
    INATIVO  = "inativo"
    BLOQUEADO = "bloqueado"