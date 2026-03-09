"""Camada de Controllers do SNH."""
from .patient_controller import PatientController
from .prescription_controller import PrescriptionController
from .user_controller import UserController
from .report_controller import RelatorioController
from .notification_controller import NotificationController

# Alias para compatibilidade
PrescricaoController = PrescriptionController

__all__ = [
    "PatientController",
    "PrescriptionController",
    "PrescricaoController",
    "UserController",
    "RelatorioController",
    "NotificationController",
]
