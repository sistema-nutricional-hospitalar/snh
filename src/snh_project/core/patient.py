from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from datetime import datetime
from src.snh_project.database import Base
from src.snh_project.core.base import AuditoriaMixin

class SetorClinico:
    def __init__(self, nome):
        self._nome = nome
        # mapa de leito -> Paciente
        self._lista_pacientes = {}  # Alterado agora
        
    @property
    def lista_pacientes(self) -> dict: # Alterado agora
        """Retorna cópia da lista para manter encapsulamento"""
        return self._lista_pacientes.copy()

    def adicionar_paciente(self, paciente: 'Paciente', leito: int) -> bool | str: # Alterado agora
        """Adiciona paciente ao setor em um leito específico.
        Raises: ValueError: Se leito já estiver ocupado."""
        
        if leito in self._lista_pacientes:
            raise ValueError(f"Leito {leito} já ocupado por {self._lista_pacientes[leito].nome}")
        else:
            self._lista_pacientes[leito] = paciente

    @property
    def nome(self) -> str:
        return self._nome
    

class Paciente(Base,AuditoriaMixin):
    """Classe que representa um paciente, com atributos e métodos para gerenciamento de dados do paciente."""

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
        """Inicializa um paciente e registra no setor clínico."""
        # Inicializa mixins (auditoria)
        AuditoriaMixin.__init__(self)
        # setorClinico deve ser uma instância de SetorClinico
        if not isinstance(setorClinico, SetorClinico):
            raise TypeError("`setorClinico` deve ser uma instância de SetorClinico. Use SetorClinico.adicionar_paciente para registrar.")

        self.nome = nome
        self._data_nasc = dataNasc
        self.leito = leito
        self._data_entrada = data_entrada
        self._risco = risco

        setorClinico.adicionar_paciente(self, leito) # Pode lançar ValueError
        self._setor_clinico = setor_clinico # ✅ Mantém referência ao objeto

    @property
    def setor_clinico(self) -> SetorClinico:
        """Retorna o setor clínico onde o paciente está internado."""
        return self._setor_clinico
    
    
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
    def data_entrada(self) -> datetime:
        return self._data_entrada

    @data_entrada.setter
    def data_entrada(self, value: datetime):
        self._data_entrada = value

    @property
    def risco(self) -> bool:
        return self._risco
    
    @risco.setter
    def risco(self, value: bool):
        # Validação: Se está na UTI, risco é sempre True
        if self._setorClinico.nome.lower() == "uti":
            self._risco = True
        else:
            self._risco = value
        self.registrar_atualizacao()

    @property
    def risco(self) -> bool:
        return self._risco