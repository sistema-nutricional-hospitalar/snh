from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from datetime import datetime
from src.snh_project.database import Base
from src.snh_project.core.base import AuditoriaMixin

class SetorClinico:
    pass

class Paciente(Base,AuditoriaMixin):
    __tablename__ = 'Paciente'

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    dataNasc = Column(String, nullable=False)
    setorClinico = Column(String, nullable=False)
    leito = Column(Integer, nullable=False)
    datain = Column(Integer, nullable=False)
    risco = Column(Boolean, nullable=False)

    criado_em = Column(DateTime, default=datetime.now)
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, nome, dataNasc, setorClinico, leito, datain, risco):
        self.nome = nome
        self.dataNasc = dataNasc
        self.setorClinico = setorClinico
        self.leito = leito
        self.datain = datain
        self.risco = risco
