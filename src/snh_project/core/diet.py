from .base import Dieta


class ItemCardapio:
    """
    Representa um item individual do cardápio.
    
    Exemplo: Arroz 200g com 150 kcal, 3g proteína, 30g carboidrato, 2g gordura
    
    Atributos:
        _nome: Nome do item (ex: "Arroz")
        _quantidade_gramas: Peso em gramas
        _calorias: Calorias totais (kcal)
        _proteinas: Gramas de proteína
        _carboidratos: Gramas de carboidrato
        _gorduras: Gramas de gordura
    """
    
    def __init__(
        self,
        nome: str,
        quantidade_gramas: float,
        calorias: float,
        proteinas: float = 0.0,
        carboidratos: float = 0.0,
        gorduras: float = 0.0
    ):
        """
        Cria um novo item de cardápio com validações rigorosas.
        
        Args:
            nome: Identificação do alimento
            quantidade_gramas: Peso do item
            calorias: Energia disponível
            proteinas: Macronutriente protéico (opcional)
            carboidratos: Macronutriente carboidrato (opcional)
            gorduras: Macronutriente lipídico (opcional)
        
        Raises:
            ValueError: Se algum parâmetro numérico for inválido
        """
        # Validações encapsuladas no construtor
        if not nome or len(nome.strip()) == 0:
            raise ValueError("Nome do item não pode ser vazio")
        
        if quantidade_gramas <= 0:
            raise ValueError("Quantidade deve ser maior que 0 gramas")
        
        if calorias < 0:
            raise ValueError("Calorias não podem ser negativas")
        
        if any(val < 0 for val in [proteinas, carboidratos, gorduras]):
            raise ValueError("Macronutrientes não podem ser negativos")
        
        # Armazenamento protegido
        self._nome: str = nome.strip()
        self._quantidade_gramas: float = quantidade_gramas
        self._calorias: float = calorias
        self._proteinas: float = proteinas
        self._carboidratos: float = carboidratos
        self._gorduras: float = gorduras
    
    
    @property
    def nome(self) -> str:
        """Retorna o nome do item"""
        return self._nome
    
    @property
    def quantidade_gramas(self) -> float:
        """Retorna a quantidade em gramas"""
        return self._quantidade_gramas
    
    @property
    def calorias(self) -> float:
        """Retorna o total de calorias"""
        return self._calorias
    
    @property
    def proteinas(self) -> float:
        """Retorna o total de proteínas em gramas"""
        return self._proteinas
    
    @property
    def carboidratos(self) -> float:
        """Retorna o total de carboidratos em gramas"""
        return self._carboidratos
    
    @property
    def gorduras(self) -> float:
        """Retorna o total de gorduras em gramas"""
        return self._gorduras
    
    def __repr__(self) -> str:
        """Representação em string para debug"""
        return (
            f"ItemCardapio(nome='{self._nome}', qtd={self._quantidade_gramas}g, "
            f"cal={self._calorias}, prot={self._proteinas}g, "
            f"carb={self._carboidratos}g, gord={self._gorduras}g)"
        )
    
    def __eq__(self, other: object) -> bool:
        """Compara dois itens pelo nome (identificador único)"""
        if not isinstance(other, ItemCardapio):
            return False
        return self._nome == other._nome


class DietaOral(Dieta):
    pass


class DietaEnteral(Dieta):
    pass