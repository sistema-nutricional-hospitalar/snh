from typing import List, Optional


class ItemCardapio:
    """
    Representa um item individual do cardápio.
    
    Exemplo: Arroz 200g com restrição de sal
    
    Atributos:
        _nome: Nome do item (ex: "Arroz")
        _quantidade_gramas: Peso em gramas
        _restricoes: Lista de restrições alimentares associadas
    """
    
    def __init__(
        self,
        nome: str,
        quantidade_gramas: float,
        restricoes: Optional[List[str]] = None
    ):
        """
        Cria um novo item de cardápio com validações rigorosas.
        
        Args:
            nome: Identificação do alimento
            quantidade_gramas: Peso do item (> 0)
            restricoes: Lista de restrições do item (opcional)
        
        Raises:
            ValueError: Se parâmetros inválidos
        """
        # Validações encapsuladas no construtor
        if not nome or len(nome.strip()) == 0:
            raise ValueError("Nome do item não pode ser vazio")
        
        if quantidade_gramas <= 0:
            raise ValueError("Quantidade deve ser maior que 0 gramas")
        
        # Armazenamento protegido
        self._nome: str = nome.strip()
        self._quantidade_gramas: float = quantidade_gramas
        self._restricoes: List[str] = [r.strip().lower() for r in (restricoes or [])]
    
    
    @property
    def nome(self) -> str:
        """Retorna o nome do item"""
        return self._nome
    
    @property
    def quantidade_gramas(self) -> float:
        """Retorna a quantidade em gramas"""
        return self._quantidade_gramas
    
    @property
    def restricoes(self) -> List[str]:
        """Retorna lista de restrições alimentares associadas ao item"""
        return self._restricoes.copy()

    def __repr__(self) -> str:
        """Representação em string para debug"""
        return (
            f"ItemCardapio(nome='{self._nome}', qtd={self._quantidade_gramas}g, "
            f"restricoes={self._restricoes})"
        )
    
    def __eq__(self, other: object) -> bool:
        """Compara dois itens pelo nome (identificador único)"""
        if not isinstance(other, ItemCardapio):
            return False
        return self._nome == other._nome
