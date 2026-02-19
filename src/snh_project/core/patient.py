from datetime import datetime
from src.snh_project.core.base import AuditoriaMixin
from src.snh_project.core.setorclin import SetorClinico


class Paciente(AuditoriaMixin):
    '''
    Classe que cria um paciente e o associa a um setor clínico. 
    O paciente é registrado no setor através do método `adicionar_paciente` do `SetorClinico`.
    '''
   

    def __init__(self, nome, dataNasc, setorClinico, leito, datain, risco):
        # Inicializa timestamps do AuditoriaMixin (OOP puro, sem ORM)
        super().__init__()
        # setorClinico deve ser uma instância de SetorClinico
        if not isinstance(setorClinico, SetorClinico):
            raise TypeError("`setorClinico` deve ser uma instância de SetorClinico. Use SetorClinico.adicionar_paciente para registrar.")

        self._nome = nome
        self._dataNasc = dataNasc

        result = setorClinico.adicionar_paciente(self, leito)
        if result is not True:
            raise ValueError(result)

        self._setorClinico = setorClinico.nome
        self._leito = leito
        self._datain = datain
        # inicializa com o valor passado, depois aplica regra de negócio explícita
        self._risco = risco
        # Recalcula risco automaticamente conforme regra de domínio (ex.: UTI sempre True)
        self._risco = self.calcular_risco_por_regra()

    
    
    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, value: str):
        self._nome = value
        self.registrar_atualizacao()

    @property
    def setorClinico(self) -> str:
        return getattr(self, "_setorClinico", "")

    @setorClinico.setter
    def setorClinico(self, value: str):
        self._setorClinico = value
        self.registrar_atualizacao()

    @property
    def datain(self) -> datetime:
        return self._datain

    @datain.setter
    def datain(self, value):
        # Aceita `datetime` ou ISO-8601 string
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        elif not isinstance(value, datetime):
            raise TypeError("`datain` deve ser `datetime` ou ISO string")

        self._datain = value
        self.registrar_atualizacao()
    
    @property
    def risco(self) -> bool:
        return bool(getattr(self, "_risco", False))

    @risco.setter
    def risco(self, value: bool):
        self._risco = bool(value)
        self.registrar_atualizacao()
    
    def calcular_risco_por_regra(self) -> bool:
        setor = getattr(self, "_setorClinico", "")
        if isinstance(setor, str) and setor.lower() == "uti":
            return True
        return bool(getattr(self, "_risco", False))

    def transferir_para_setor(self, setor_obj, leito):
        # validações e interações com SetorClinico
        if not isinstance(setor_obj, SetorClinico):
            raise TypeError("`setor_obj` deve ser SetorClinico")
        result = setor_obj.adicionar_paciente(self, leito)
        if result is not True:
            raise ValueError(result)
        # Atualiza estado do paciente explicitamente e registra auditoria
        self._setorClinico = setor_obj.nome
        self._leito = leito
        # Recalcula risco por regra explícita
        self._risco = self.calcular_risco_por_regra()
        self.registrar_atualizacao()
        return True