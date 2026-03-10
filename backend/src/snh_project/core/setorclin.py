from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .patient import Paciente

class SetorClinico:
    """
    Representa um setor clínico do hospital (UTI, Enfermaria, etc).
    
    Gerencia a alocação de pacientes em leitos específicos.
    Garante que um leito não seja ocupado por dois pacientes simultaneamente.
    
    Atributos:
        _nome: Nome do setor (ex: "UTI", "Clínica Geral")
        _lista_pacientes: Mapeamento leito → Paciente
    """
    
    def __init__(self, nome: str):
        """
        Cria um novo setor clínico.
        
        Args:
            nome: Nome do setor (não pode ser vazio)
        
        Raises:
            ValueError: Se nome for vazio
        
        Example:
            >>> uti = SetorClinico("UTI")
            >>> enfermaria = SetorClinico("Enfermaria Geral")
        """
        if not nome or len(nome.strip()) == 0:
            raise ValueError("Nome do setor não pode ser vazio")
        
        self._nome = nome.strip()
        self._lista_pacientes: Dict[int, 'Paciente'] = {}  # leito → Paciente
    
    
    @property
    def nome(self) -> str:
        """Retorna o nome do setor"""
        return self._nome
    
    @property
    def lista_pacientes(self) -> Dict[int, 'Paciente']:
        """
        Retorna CÓPIA do dicionário de pacientes.
        
        Protege encapsulamento: modificações no dicionário retornado
        não afetam o estado interno do setor.
        
        Returns:
            Dict[int, Paciente]: Mapeamento leito → Paciente
        
        Example:
            >>> setor = SetorClinico("UTI")
            >>> pacientes = setor.lista_pacientes
            >>> len(pacientes)
            0
        """
        return self._lista_pacientes.copy()
    
    @property
    def quantidade_pacientes(self) -> int:
        """
        Retorna o número de pacientes no setor.
        
        Returns:
            int: Quantidade de leitos ocupados
        
        Example:
            >>> setor = SetorClinico("UTI")
            >>> setor.quantidade_pacientes
            0
        """
        return len(self._lista_pacientes)
    
    @property
    def leitos_ocupados(self) -> List[int]:
        """
        Retorna lista de números dos leitos ocupados.
        
        Returns:
            List[int]: Lista ordenada de leitos ocupados
        
        Example:
            >>> setor = SetorClinico("UTI")
            >>> setor.leitos_ocupados
            [1, 3, 5, 10]
        """
        return sorted(self._lista_pacientes.keys())
    
    @property
    def esta_vazio(self) -> bool:
        """
        Verifica se o setor está vazio (sem pacientes).
        
        Returns:
            bool: True se não há pacientes, False caso contrário
        """
        return len(self._lista_pacientes) == 0
    
    # ==================== MÉTODOS PÚBLICOS ====================
    
    def adicionar_paciente(self, paciente: 'Paciente', leito: int):
        """
        Adiciona um paciente ao setor em um leito específico.
        
        Valida que o leito está disponível antes de adicionar.
        
        Args:
            paciente: Objeto Paciente a ser adicionado
            leito: Número do leito (deve estar vago)
        
        Returns:
            True se adicionou com sucesso
            str com mensagem de erro se leito ocupado
        
        Example:
            >>> setor = SetorClinico("UTI")
            >>> paciente = Paciente(...)
            >>> result = setor.adicionar_paciente(paciente, 10)
            >>> result
            True
        """
        # Validação de tipo
        if not hasattr(paciente, 'nome'):
            raise TypeError("paciente deve ser instância de Paciente")
        
        if not isinstance(leito, int) or leito <= 0:
            raise ValueError(f"Leito deve ser inteiro positivo, recebido: {leito}")
        
        # Verifica se leito está disponível
        if leito in self._lista_pacientes:
            paciente_atual = self._lista_pacientes[leito]
            return f"Leito {leito} já ocupado por {paciente_atual.nome}"
        
        # Adiciona paciente
        self._lista_pacientes[leito] = paciente
        return True
    
    def remover_paciente(self, leito: int) -> bool:
        """
        Remove um paciente do setor (libera o leito).
        
        Args:
            leito: Número do leito a ser liberado
        
        Returns:
            bool: True se removeu, False se leito já estava vazio
        
        Example:
            >>> setor.remover_paciente(10)
            True
            >>> setor.remover_paciente(10)  # Já removido
            False
        """
        if leito in self._lista_pacientes:
            del self._lista_pacientes[leito]
            return True
        return False
    
    def obter_paciente(self, leito: int) -> Optional['Paciente']:
        """
        Busca paciente por número do leito.
        
        Args:
            leito: Número do leito
        
        Returns:
            Paciente se encontrado, None se leito vazio
        
        Example:
            >>> paciente = setor.obter_paciente(10)
            >>> if paciente:
            ...     print(paciente.nome)
        """
        return self._lista_pacientes.get(leito)
    
    def leito_esta_ocupado(self, leito: int) -> bool:
        """
        Verifica se um leito específico está ocupado.
        
        Args:
            leito: Número do leito a verificar
        
        Returns:
            bool: True se ocupado, False se vago
        
        Example:
            >>> if setor.leito_esta_ocupado(10):
            ...     print("Leito ocupado")
        """
        return leito in self._lista_pacientes
    
    def buscar_paciente_por_nome(self, nome: str) -> Optional['Paciente']:
        """
        Busca paciente pelo nome no setor.
        
        Args:
            nome: Nome (ou parte do nome) do paciente
        
        Returns:
            Paciente se encontrado, None caso contrário
        
        Example:
            >>> paciente = setor.buscar_paciente_por_nome("João")
        """
        nome_busca = nome.strip().lower()
        for paciente in self._lista_pacientes.values():
            if nome_busca in paciente.nome.lower():
                return paciente
        return None
    
    def listar_pacientes(self) -> List['Paciente']:
        """
        Retorna lista de todos os pacientes do setor.
        
        Returns:
            List[Paciente]: Lista de pacientes (ordenada por leito)
        
        Example:
            >>> for paciente in setor.listar_pacientes():
            ...     print(f"{paciente.nome} - Leito {paciente.leito}")
        """
        leitos_ordenados = sorted(self._lista_pacientes.keys())
        return [self._lista_pacientes[leito] for leito in leitos_ordenados]
    
    def limpar_setor(self) -> int:
        """
        Remove todos os pacientes do setor (libera todos os leitos).
        
        Útil para testes ou reorganizações do setor.
        
        Returns:
            int: Quantidade de pacientes removidos
        
        Warning:
            Este método não atualiza os objetos Paciente.
            Use com cuidado!
        
        Example:
            >>> quantidade = setor.limpar_setor()
            >>> print(f"{quantidade} pacientes removidos")
        """
        quantidade = len(self._lista_pacientes)
        self._lista_pacientes.clear()
        return quantidade
    
    def obter_relatorio(self) -> Dict:
        """
        Gera relatório resumido do setor.
        
        Returns:
            dict: Estatísticas do setor
        
        Example:
            >>> relatorio = setor.obter_relatorio()
            >>> print(relatorio)
            {
                'nome': 'UTI',
                'total_pacientes': 5,
                'leitos_ocupados': [1, 2, 3, 5, 10],
                'taxa_ocupacao': '50%'  # se capacidade for 10
            }
        """
        return {
            'nome': self._nome,
            'total_pacientes': self.quantidade_pacientes,
            'leitos_ocupados': self.leitos_ocupados,
            'esta_vazio': self.esta_vazio
        }
    
    
    def __repr__(self) -> str:
        """Representação em string para debug"""
        return (
            f"SetorClinico(nome='{self._nome}', "
            f"pacientes={self.quantidade_pacientes})"
        )
    
    def __str__(self) -> str:
        """Representação amigável para usuário"""
        return f"{self._nome} ({self.quantidade_pacientes} pacientes)"
    
    def __len__(self) -> int:
        """Permite usar len(setor) para contar pacientes"""
        return self.quantidade_pacientes
    
    def __contains__(self, leito: int) -> bool:
        """
        Permite usar 'leito in setor' para verificar ocupação.
        
        Example:
            >>> if 10 in setor:
            ...     print("Leito 10 ocupado")
        """
        return leito in self._lista_pacientes
    
    def __iter__(self):
        """
        Permite iterar sobre os pacientes do setor.
        
        Example:
            >>> for paciente in setor:
            ...     print(paciente.nome)
        """
        return iter(self.listar_pacientes())