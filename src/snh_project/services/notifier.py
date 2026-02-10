from typing import List, Dict
from .strategies import EstrategiaNotificacao


class NotificadorService:
    """Padrão Observer: gerencia canais de notificação e dispara eventos."""
    
    def __init__(self):
        """Inicializa o serviço sem observadores."""
        self._observadores: Dict[str, EstrategiaNotificacao] = {}
        self._destinatarios: Dict[str, List[str]] = {}
    
    def registrar_observador(
        self, 
        canal: str, 
        estrategia: EstrategiaNotificacao, 
        destinatarios: List[str]
    ) -> None:
        """
        Registra um novo canal de notificação.
        
        Args:
            canal: Nome do canal
            estrategia: Implementação concreta (Email, Push, etc)
            destinatarios: Lista de endereços/IDs
        
        Raises:
            TypeError: Se estrategia não implementa EstrategiaNotificacao
            ValueError: Se canal ou destinatarios forem vazios
        """
        # Validação de tipo da estratégia
        if not isinstance(estrategia, EstrategiaNotificacao):
            raise TypeError(
                f"Estratégia deve implementar EstrategiaNotificacao, "
                f"recebido {type(estrategia).__name__}"
            )
        
        # Validação do nome do canal
        if not canal or len(canal.strip()) == 0:
            raise ValueError("Nome do canal não pode ser vazio")
        
        # Validação da lista de destinatários
        if not destinatarios or len(destinatarios) == 0:
            raise ValueError(f"Canal '{canal}' precisa de ao menos um destinatário")
        
        # Validação de que todos os destinatários são strings não vazias
        for dest in destinatarios:
            if not isinstance(dest, str) or len(dest.strip()) == 0:
                raise ValueError(f"Destinatário inválido no canal '{canal}': {dest}")
        
        # Armazena a estratégia e destinatários
        canal_normalizado = canal.strip().lower()
        self._observadores[canal_normalizado] = estrategia
        self._destinatarios[canal_normalizado] = [d.strip() for d in destinatarios]
    
    def remover_observador(self, canal: str) -> bool:
        """
        Remove um canal de notificação.
        
        Args:
            canal: Nome do canal
        
        Returns:
            True se removido, False se não encontrado
        """
        canal_normalizado = canal.strip().lower()
        
        # Verifica se o canal existe
        if canal_normalizado not in self._observadores:
            return False
        
        # Remove das duas estruturas de dados
        del self._observadores[canal_normalizado]
        del self._destinatarios[canal_normalizado]
        
        return True
    
    def notificar_mudanca(
        self,
        prescricao_id: int,
        tipo_mudanca: str,
        detalhes: str = ""
    ) -> Dict[str, int]:
        """
        Dispara notificações em todos os canais registrados.
        
        Args:
            prescricao_id: ID da prescrição alterada
            tipo_mudanca: Tipo de evento (ex: 'Alteração de dieta')
            detalhes: Informações adicionais (opcional)
        
        Returns:
            Dict com 'total_enviados', 'sucessos', 'falhas'
        """
        # Contadores de estatísticas
        total_enviados = 0
        sucessos = 0
        falhas = 0
        
        # Monta a mensagem completa
        mensagem_base = f"[SNH] Prescrição #{prescricao_id} - {tipo_mudanca}"
        if detalhes:
            mensagem_completa = f"{mensagem_base}\nDetalhes: {detalhes}"
        else:
            mensagem_completa = mensagem_base
        
        # Itera sobre todos os canais registrados
        for canal, estrategia in self._observadores.items():
            destinatarios = self._destinatarios[canal]
            
            # Envia para cada destinatário do canal
            for destinatario in destinatarios:
                total_enviados += 1
                
                try:
                    # Usa a estratégia específica do canal para enviar
                    sucesso = estrategia.enviar(mensagem_completa, destinatario)
                    
                    if sucesso:
                        sucessos += 1
                    else:
                        falhas += 1
                        
                except Exception as e:
                    # Captura qualquer exceção durante o envio
                    falhas += 1
                    print(f"[ERRO] Falha ao notificar {destinatario} no canal {canal}: {e}")
        
        # Retorna estatísticas
        return {
            'total_enviados': total_enviados,
            'sucessos': sucessos,
            'falhas': falhas
        }
    
    def listar_canais_ativos(self) -> List[str]:
        """Retorna lista de canais registrados."""
        return list(self._observadores.keys())
    
    @property
    def total_observadores(self) -> int:
        """Retorna a quantidade de canais registrados."""
        return len(self._observadores)
    
    def obter_destinatarios(self, canal: str) -> List[str]:
        """
        Retorna cópia da lista de destinatários de um canal.
        
        Args:
            canal: Nome do canal
        
        Returns:
            Lista vazia se canal não existir
        """
        canal_normalizado = canal.strip().lower()
        
        if canal_normalizado not in self._destinatarios:
            return []
        
        return self._destinatarios[canal_normalizado].copy()
    
    def __repr__(self) -> str:
        """Representação do objeto para debug."""
        return (
            f"NotificadorService(canais={len(self._observadores)}, "
            f"total_destinatarios={sum(len(d) for d in self._destinatarios.values())})"
        )