from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from datetime import datetime
from src.snh_project.database import Base
from src.snh_project.core.base import AuditoriaMixin

class SetorClinico:
    def __init__(self, nome):
        self._nome = nome
        # mapa de leito -> Paciente
        self.lista_pacientes = {}

    def adicionar_paciente(self, paciente, leito):
        if leito in self.lista_pacientes:
            return f"Leito {leito} já ocupado por {self.lista_pacientes[leito].nome}."
        self.lista_pacientes[leito] = paciente
        return True

    @property
    def nome(self) -> str:
        return self._nome
    

class Paciente(Base,AuditoriaMixin):
    __tablename__ = 'Paciente'

    id = Column(Integer, primary_key=True, index=True)
    _nome = Column('nome', String, nullable=False)
    _dataNasc = Column('dataNasc', String, nullable=False)
    _setorClinico = Column('setorClinico', String, nullable=False)
    _leito = Column('leito', Integer, nullable=False)
    _datain = Column('datain', DateTime, nullable=False)
    _risco = Column('risco', Boolean, nullable=False)

    criado_em = Column(DateTime, default=datetime.now)
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, nome, dataNasc, setorClinico, leito, datain, risco):
        # setorClinico deve ser uma instância de SetorClinico
        if not isinstance(setorClinico, SetorClinico):
            raise TypeError("`setorClinico` deve ser uma instância de SetorClinico. Use SetorClinico.adicionar_paciente para registrar.")

        self.nome = nome
        self.dataNasc = dataNasc

        result = setorClinico.adicionar_paciente(self, leito)
        if result is not True:
            raise ValueError(result)

        self.setorClinico = setorClinico.nome
        self.leito = leito
        self.datain = datain
        self.risco = risco
    
    
    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, value: str):
        self._nome = value

    @property
    def setorClinico(self) -> str:
        return self._setorClinico

    @setorClinico.setter
    def setorClinico(self, value: str):
        self._setorClinico = value

    @property
    def datain(self) -> datetime:
        return self._datain

    @datain.setter
    def datain(self, value: datetime):
        self._datain = value
    
    @property
    def risco(self) -> bool:
        if self._setorClinico.lower() == "uti":
            return True
        return self._risco

    @risco.setter
    def risco(self, value: bool):
        self._risco = value