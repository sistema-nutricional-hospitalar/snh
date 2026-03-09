"""
Camada de infraestrutura do SNH.

Contém repositórios JSON e serializadores que isolam o domínio
do mecanismo de persistência. Nenhum módulo desta camada deve
importar camadas superiores (controllers, api).
"""

from .json_repository import JsonRepository
from .patient_repository import PatientRepository
from .prescription_repository import PrescriptionRepository
from .setor_repository import SetorRepository
from .notification_repository import NotificationRepository
from .user_repository import UserRepository

__all__ = [
    "JsonRepository",
    "PatientRepository",
    "PrescriptionRepository",
    "SetorRepository",
    "NotificationRepository",
    "UserRepository",
]
