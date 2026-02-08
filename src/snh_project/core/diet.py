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
    """
    Dieta via alimentação normal (por boca).
    
    Para pacientes que conseguem se alimentar normalmente.
    Características:
    - Variedade de alimentos e texturas
    - Suporta restrições de mastigação (textura)
    - Controle de fibra importante
    
    Atributos:
        _textura: Forma de preparação (normal, mole, pastosa, líquida)
        _fibra_g: Quantidade de fibra em gramas (0-50)
        _permite_acucar: Pode consumir açúcar?
        _permite_sal: Pode consumir sal?
    """
    
    # Constante: texturas válidas
    TEXTURAS_VALIDAS = {"normal", "mole", "pastosa", "liquida"}
    
    def __init__(
        self,
        textura: str,
        calorias: float,
        proteina_g: float,
        carboidrato_g: float,
        lipidio_g: float,
        fibra_g: float = 25.0,
        permite_acucar: bool = True,
        permite_sal: bool = True,
        descricao: str = "",
        usuario_responsavel: str = "sistema"
    ):
        """
        Cria uma nova DietaOral com validações rigorosas.
        
        Args:
            textura: "normal", "mole", "pastosa" ou "liquida"
            calorias: Energia total (kcal)
            proteina_g: Proteína em gramas
            carboidrato_g: Carboidrato em gramas
            lipidio_g: Gordura em gramas
            fibra_g: Fibra em gramas (padrão: 25g - ideal)
            permite_acucar: Permitir açúcar? (padrão: sim)
            permite_sal: Permitir sal? (padrão: sim)
            descricao: Notas adicionais
            usuario_responsavel: Quem prescreveu
        
        Raises:
            ValueError: Se parâmetros inválidos
        """
        if textura.lower() not in self.TEXTURAS_VALIDAS:
            raise ValueError(
                f"Textura inválida. Opções: {', '.join(self.TEXTURAS_VALIDAS)}"
            )
        
        if fibra_g < 0 or fibra_g > 50:
            raise ValueError("Fibra deve estar entre 0 e 50 gramas")
        
        if calorias <= 0:
            raise ValueError("Calorias devem ser maiores que zero")
        
        super().__init__(
            descricao=descricao,
            usuario_responsavel=usuario_responsavel
        )
        
        self._textura: str = textura.lower()
        self._calorias_dieta: float = calorias
        self._proteina_dieta: float = proteina_g
        self._carboidrato_dieta: float = carboidrato_g
        self._lipidio_dieta: float = lipidio_g
        self._fibra_g: float = fibra_g
        self._permite_acucar: bool = permite_acucar
        self._permite_sal: bool = permite_sal
    
    @property
    def textura(self) -> str:
        """Retorna a textura da dieta"""
        return self._textura
    
    @property
    def fibra_g(self) -> float:
        """Retorna quantidade de fibra em gramas"""
        return self._fibra_g
    
    @property
    def permite_acucar(self) -> bool:
        """Retorna se pode consumir açúcar"""
        return self._permite_acucar
    
    @property
    def permite_sal(self) -> bool:
        """Retorna se pode consumir sal"""
        return self._permite_sal
    
    @fibra_g.setter
    def fibra_g(self, valor: float) -> None:
        """
        Define fibra com validação.
        
        Args:
            valor: Fibra em gramas (0-50)
        
        Raises:
            ValueError: Se fora do intervalo válido
        """
        if valor < 0 or valor > 50:
            raise ValueError("Fibra deve estar entre 0 e 50 gramas")
        self._fibra_g = valor
        self.registrar_atualizacao()
    
    @permite_acucar.setter
    def permite_acucar(self, valor: bool) -> None:
        """Define se permite açúcar"""
        self._permite_acucar = valor
        self.registrar_atualizacao()
    
    @permite_sal.setter
    def permite_sal(self, valor: bool) -> None:
        """Define se permite sal"""
        self._permite_sal = valor
        self.registrar_atualizacao()
    
    def calcular_nutrientes(self) -> dict[str, float]:
        """
        Implementação do método abstrato.
        Calcula nutrientes totais de DietaOral.
        
        Returns:
            dict com macronutrientes calculados
        """
        return {
            "tipo_dieta": "Oral",
            "textura": self._textura,
            "calorias_total": self._calorias_dieta,
            "proteina_total_g": self._proteina_dieta,
            "carboidrato_total_g": self._carboidrato_dieta,
            "lipidio_total_g": self._lipidio_dieta,
            "fibra_total_g": self._fibra_g,
            "itens_cardapio": len(self._itens),
            "permite_acucar": self._permite_acucar,
            "permite_sal": self._permite_sal
        }
    
    def __repr__(self) -> str:
        return (
            f"DietaOral(textura={self._textura}, "
            f"cal={self._calorias_dieta}, "
            f"fibra={self._fibra_g}g, ativo={self._ativo})"
        )


class DietaEnteral(Dieta):
    pass