



class SetorClinico:
    def __init__(self, nome):
        self._nome = nome
        # mapa de leito -> Paciente
        self._lista_pacientes = {}

    def adicionar_paciente(self, paciente, leito):
        if leito in self._lista_pacientes:
            return f"Leito {leito} já ocupado por {self._lista_pacientes[leito].nome}."
        self._lista_pacientes[leito] = paciente
        return True

    @property
    def nome(self) -> str:
        return self._nome
    