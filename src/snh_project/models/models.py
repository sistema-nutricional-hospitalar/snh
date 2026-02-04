from sqlalchemy import Column, Integer, String, Text, Boolean

from src.snh_project.database import Base


class Paciente(Base):
    __tablename__ = 'Paciente'

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    dataNasc = Column(String, nullable=False)
    setorClinico = Column(String, nullable=False)
    leito = Column(Integer, nullable=False)
    datain = Column(Integer, nullable=False)
    risco = Column(Boolean, nullable=False)