from typing import List, Tuple
from ..base import Dieta


class DietaMista(Dieta):
    """
    Dieta mista: composição de múltiplas dietas com percentuais
    
    Implementa o Padrão Composite (GoF - Estrutural):
    - Permite tratar dieta simples e composta uniformemente
    - Dieta composta é uma árvore de dietas
    - Cada componente tem um peso/percentual
    
    Casos de uso:
    - Paciente em transição de enteral para oral (50%/50%)
    - Reforço nutricional (70% oral + 30% parenteral)
    - Desmame de nutrição artificial (80% oral + 20% enteral)
    
    Regras:
    - Soma dos percentuais deve ser 100% (±5% tolerância)
    - Mínimo 2 componentes
    - Máximo 4 componentes (evitar complexidade excessiva)
    - Cada componente deve ser Dieta válida
    
    Atributos:
        _componentes: List[Tuple[Dieta, float]] (dieta, percentual)
    """
    
    def __init__(
        self,
        descricao: str = "Dieta Mista",
        usuario_responsavel: str = "sistema"
    ):
        """
        Cria uma nova DietaMista vazia
        
        Componentes devem ser adicionados usando adicionar_componente()
        
        Args:
            descricao: Descrição da dieta mista (opcional)
            usuario_responsavel: Quem prescreveu (padrão: "sistema")
        
        Example:
            >>> dieta_mista.adicionar_componente(dieta_oral, 30.0)
            >>> dieta_mista.adicionar_componente(dieta_enteral, 70.0)
        """
        super().__init__(
            descricao=descricao,
            usuario_responsavel=usuario_responsavel
        )
        
        # Atributo específico: lista de (Dieta, percentual)
        self._componentes: List[Tuple[Dieta, float]] = []
    
    
    # ==================== PROPERTIES ====================
    
    @property
    def componentes(self) -> List[Tuple[Dieta, float]]:
        """
        Retorna:
            List[Tuple[Dieta, float]]: Lista de (dieta, percentual)
        
        Exemplo:
            >>> for dieta, percentual in dieta_mista.componentes:
            ...     print(f"{dieta.__class__.__name__}: {percentual}%")
        """
        return self._componentes.copy()
    
    @property
    def quantidade_componentes(self) -> int:
        return len(self._componentes)
    
    @property
    def percentual_total(self) -> float:
        """
        Calcula a soma dos percentuais dos componentes
        
        Deve ser 100% (±5% tolerância)
        """
        return sum(percentual for _, percentual in self._componentes)
    
    @property
    def esta_valida(self) -> bool:
        return self.validar_compatibilidade()
    
    
    # ==================== MÉTODOS PÚBLICOS ====================
    
    def adicionar_componente(self, dieta: Dieta, percentual: float) -> None:
        """
        Adiciona um componente (dieta) à dieta mista.
        
        Args:
            dieta: Objeto Dieta (DietaOral, DietaEnteral, etc)
            percentual: Percentual desta dieta na composição (0-100)
        
        Raises:
            TypeError: Se dieta não for instância de Dieta
            ValueError: Se percentual inválido ou limite de componentes atingido
        """

        if not isinstance(dieta, Dieta):
            raise TypeError(
                f"Componente deve ser instância de Dieta, "
                f"recebido: {type(dieta).__name__}"
            )
        
        # Evita adicionar DietaMista dentro de DietaMista (evita recursão infinita)
        if isinstance(dieta, DietaMista):
            raise TypeError(
                "Não é permitido adicionar DietaMista como componente "
                "(evita complexidade excessiva e recursão)"
            )
        
        # Validação de percentual
        if percentual <= 0 or percentual > 100:
            raise ValueError(
                f"Percentual deve estar entre 0 e 100, recebido: {percentual}"
            )
        
        # Validação de limite de componentes
        if len(self._componentes) >= 4:
            raise ValueError(
                "Dieta mista já possui 4 componentes (limite máximo). "
                "Remova um componente antes de adicionar outro."
            )
        
        # Validação: não adicionar a mesma dieta duas vezes
        for dieta_existente, _ in self._componentes:
            if dieta_existente is dieta:
                raise ValueError(
                    "Esta dieta já foi adicionada como componente. "
                    "Use atualizar_percentual() para alterar o percentual."
                )
        
        # Adiciona componente
        self._componentes.append((dieta, percentual))
        self.registrar_atualizacao()
    
    
    def remover_componente(self, dieta: Dieta) -> bool:
        """
        Remove um componente da dieta mista.
        
        Args:
            dieta: Dieta a ser removida
        
        Returns:
            bool: True se removeu, False se não encontrou
        
        Example:
            >>> removido = dieta_mista.remover_componente(dieta_oral)
            >>> print(removido)
            True
        """
        for i, (dieta_existente, _) in enumerate(self._componentes):
            if dieta_existente is dieta:
                self._componentes.pop(i)
                self.registrar_atualizacao()
                return True
        return False
    
    
    def atualizar_percentual(self, dieta: Dieta, novo_percentual: float) -> bool:
        """
        Atualiza o percentual de um componente existente.
        
        Args:
            dieta: Dieta cujo percentual será alterado
            novo_percentual: Novo valor do percentual (0-100)
        
        Returns:
            bool: True se atualizou, False se dieta não encontrada
        
        Raises:
            ValueError: Se novo_percentual inválido
        
        Example:
            >>> dieta_mista.atualizar_percentual(dieta_oral, 50.0)
            True
        """
        # Validação de percentual
        if novo_percentual <= 0 or novo_percentual > 100:
            raise ValueError(
                f"Percentual deve estar entre 0 e 100, recebido: {novo_percentual}"
            )
        
        # Busca e atualiza
        for i, (dieta_existente, _) in enumerate(self._componentes):
            if dieta_existente is dieta:
                self._componentes[i] = (dieta_existente, novo_percentual)
                self.registrar_atualizacao()
                return True
        
        return False
    
    
    def limpar_componentes(self) -> int:
        """
        Remove todos os componentes da dieta mista.
        
        Returns:
            int: Quantidade de componentes removidos
        
        Example:
            >>> quantidade = dieta_mista.limpar_componentes()
            >>> print(f"{quantidade} componentes removidos")
        """
        quantidade = len(self._componentes)
        self._componentes.clear()
        self.registrar_atualizacao()
        return quantidade
    
    
    def obter_componente_por_tipo(self, tipo_dieta: type) -> List[Tuple[Dieta, float]]:
        """
        Busca componentes por tipo de dieta.
        
        Args:
            tipo_dieta: Classe da dieta (DietaOral, DietaEnteral, etc)
        
        Returns:
            List[Tuple[Dieta, float]]: Lista de componentes do tipo especificado
        
        Example:
            >>> orais = dieta_mista.obter_componente_por_tipo(DietaOral)
            >>> for dieta, perc in orais:
            ...     print(f"Oral: {perc}%")
        """

        return [
            (dieta, percentual)
            for dieta, percentual in self._componentes
            if isinstance(dieta, tipo_dieta)
        ]
    
    
    def calcular_nutrientes(self) -> dict[str, float | dict | str | list]:
        """
        Calcula metadados agregados da dieta mista (Composite).
        
        Agrega informações de todos os componentes, ponderando pelos
        percentuais quando aplicável.
        
        Returns:
            dict: Estrutura com tipo_dieta, componentes (lista), percentual_total,
                  quantidade_componentes, esta_valida
        
        Example:
            >>> resultado = dieta_mista.calcular_nutrientes()
            >>> print(resultado['tipo_dieta'])
            'Mista (Composite)'
            >>> for comp in resultado['componentes']:
            ...     print(f"{comp['tipo']}: {comp['percentual']}%")
        """

        # Calcula informações de cada componente
        componentes_info = []
        for dieta, percentual in self._componentes:
            info = {
                "tipo": dieta.__class__.__name__,
                "percentual": percentual,
                "descricao": dieta.descricao,
                "ativo": dieta.ativo
            }
            componentes_info.append(info)
        
        return {
            "tipo_dieta": "Mista (Composite)",
            "componentes": componentes_info,
            "quantidade_componentes": self.quantidade_componentes,
            "percentual_total": self.percentual_total,
            "esta_valida": self.esta_valida,
            "quantidade_itens": len(self._itens)  # Geralmente 0 para mista
        }
    
    
    def validar_compatibilidade(self) -> bool:

        try:
            # Valida quantidade de componentes
            if len(self._componentes) < 2:
                return False
            
            if len(self._componentes) > 4:
                return False
            
            # Valida percentual total (±5% tolerância)
            total = self.percentual_total
            if total < 95.0 or total > 105.0:
                return False
            
            # Valida que todos os componentes são dietas válidas
            for dieta, percentual in self._componentes:
                if dieta is None:
                    return False
                if not isinstance(dieta, Dieta):
                    return False
                if percentual <= 0 or percentual > 100:
                    return False
            
            return True
        except (ValueError, AttributeError):
            return False
    
    
    def obter_resumo(self) -> str:
        """
        Retorna resumo legível da composição da dieta mista.
        
        Returns:
            str: Texto descritivo da composição
        
        Example:
            >>> print(dieta_mista.obter_resumo())
            'Dieta Mista: DietaOral (30%) + DietaEnteral (70%)'
        """
        if not self._componentes:
            return "Dieta Mista (vazia)"
        
        partes = [
            f"{dieta.__class__.__name__} ({percentual}%)"
            for dieta, percentual in self._componentes
        ]
        
        return f"Dieta Mista: {' + '.join(partes)}"
    
    
    # ==================== SOBRESCRITA DE MÉTODOS DA BASE ====================
    
    def adicionar_item(self, item) -> None:
        """
        DietaMista geralmente não tem itens próprios.
        
        Os itens pertencem aos componentes individuais.
        Este método está disponível mas não é recomendado usar.
        """
        raise NotImplementedError(
            "DietaMista não deve ter itens próprios. "
            "Adicione itens aos componentes individuais (DietaOral, etc)."
        )
    
    
    def __repr__(self) -> str:
        """Representação em string para debug"""
        return (
            f"DietaMista(componentes={self.quantidade_componentes}, "
            f"percentual_total={self.percentual_total}%, "
            f"valida={self.esta_valida}, "
            f"ativo={self._ativo})"
        )
    
    
    def __str__(self) -> str:
        """Representação amigável para usuário"""
        return self.obter_resumo()
