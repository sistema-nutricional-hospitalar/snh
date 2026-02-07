from abc import ABC
from datetime import datetime

class AuditoriaMixin:
    """Rastreia criação e atualização de entidades do domínio"""
    
    def __init__(self):
        self.criado_em = datetime.now()
        self.atualizado_em = datetime.now()
    
    def registrar_atualizacao(self):
        self.atualizado_em = datetime.now()

class StatusDietaMixin:
    """Gerencia status de prescrições de dieta"""
    
    def __init__(self):
        self.ativo = True
        self.data_inicio = datetime.now()
        self.data_fim = None
    
    def encerrar_dieta(self):
        self.ativo = False
        self.data_fim = datetime.now()

class Dieta(ABC):
    pass