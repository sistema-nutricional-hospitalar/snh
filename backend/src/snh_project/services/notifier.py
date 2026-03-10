from .strategies import EstrategiaNotificacao

class NotificadorService:
    def __init__(self):
        self._observadores = {}

    def registrar_observador(self, nome_canal: str, estrategia: EstrategiaNotificacao, destinatarios: list[str]):
        if not nome_canal:
            raise ValueError("Nome do canal não pode ser vazio")
        
        if not isinstance(estrategia, EstrategiaNotificacao):
            raise TypeError("Estratégia deve implementar EstrategiaNotificacao")
        
        if not destinatarios:
            raise ValueError("precisa de ao menos um destinatário")
        
        for d in destinatarios:
            if not isinstance(d, str):
                raise ValueError("Destinatário inválido no canal")
        
        self._observadores[nome_canal] = {
            "estrategia": estrategia,
            "destinatarios": destinatarios
        }

    def remover_observador(self, nome_canal: str) -> bool:
        if nome_canal in self._observadores:
            del self._observadores[nome_canal]
            return True
        return False

    def listar_canais_ativos(self) -> list[str]:
        return list(self._observadores.keys())

    def obter_destinatarios(self, nome_canal: str) -> list[str]:
        if nome_canal in self._observadores:
            return self._observadores[nome_canal]["destinatarios"]
        return []

    @property
    def total_observadores(self) -> int:
        return len(self._observadores)

    def notificar_mudanca(self, id_paciente: int, mensagem: str) -> dict:
        total_enviados = 0
        sucessos = 0
        falhas = 0
        
        for canal, info in self._observadores.items():
            estrategia = info["estrategia"]
            for destinatario in info["destinatarios"]:
                total_enviados += 1
                try:
                    resultado = estrategia.enviar(mensagem, destinatario)
                    if resultado:
                        sucessos += 1
                    else:
                        falhas += 1
                except Exception:
                    falhas += 1
        
        return {
            "total_enviados": total_enviados,
            "sucessos": sucessos,
            "falhas": falhas
        }

    def __repr__(self) -> str:
        return f"NotificadorService(canais={self.listar_canais_ativos()})"
