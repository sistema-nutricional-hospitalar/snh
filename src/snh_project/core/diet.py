from typing import Optional, List
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
        gorduras: float = 0.0,
        restricoes: Optional[List[str]] = None
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
    
    @property
    def restricoes(self) -> List[str]:
        """Retorna lista de restrições alimentares associadas ao item"""
        return self._restricoes.copy()

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
        self._restricoes_proibidas: set[str] = set()
    
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
    
    def adicionar_item(self, item: ItemCardapio) -> None:
        """Sobrescreve adicionar_item para validar restrições antes de adicionar."""
        if not isinstance(item, ItemCardapio):
            raise TypeError(f"Esperado ItemCardapio, recebido {type(item).__name__}")

        # verifica conflito entre restrições do item e restrições proibidas da dieta
        item_restricoes = {r.lower() for r in item.restricoes}
        proibidas = {r.lower() for r in self._restricoes_proibidas}
        if item_restricoes & proibidas:
            conflitantes = ", ".join(sorted(item_restricoes & proibidas))
            raise ValueError(f"Item '{item.nome}' conflita com restrições da dieta: {conflitantes}")

        super().adicionar_item(item)

    def adicionar_restricao_proibida(self, restricao: str) -> None:
        """Adiciona uma restrição proibida (ex: 'gluten', 'lactose')."""
        if not restricao or not restricao.strip():
            raise ValueError("Restrição inválida")
        self._restricoes_proibidas.add(restricao.strip().lower())
        self.registrar_atualizacao()

    def remover_restricao_proibida(self, restricao: str) -> bool:
        """Remove uma restrição proibida; retorna True se removida"""
        chave = restricao.strip().lower()
        if chave in self._restricoes_proibidas:
            self._restricoes_proibidas.remove(chave)
            self.registrar_atualizacao()
            return True
        return False

    def listar_restricoes_proibidas(self) -> List[str]:
        """Retorna lista ordenada de restrições proibidas"""
        return sorted(self._restricoes_proibidas)

    def tem_restricao_proibida(self, restricao: str) -> bool:
        return restricao.strip().lower() in self._restricoes_proibidas

    def calcular_nutrientes(self) -> dict[str, float | dict]:
        """
        Calcula nutrientes de forma inteligente e estratégica.
        
        Compara nutrientes prescritos vs alcançados pelos itens do cardápio.
        Fornece análise de viabilidade da dieta.
        
        Returns:
            dict com:
            - prescribed: nutrientes prescritos
            - achieved_from_items: nutrientes dos itens adicionados
            - analysis: percentual de cobertura e viabilidade
            - restrictions: contraindicações
        """
        # Soma dos nutrientes fornecidos pelos itens do cardápio
        calorias_itens = sum(item.calorias for item in self._itens) if self._itens else 0.0
        proteina_itens = sum(item.proteinas for item in self._itens) if self._itens else 0.0
        carboidrato_itens = sum(item.carboidratos for item in self._itens) if self._itens else 0.0
        lipidio_itens = sum(item.gorduras for item in self._itens) if self._itens else 0.0

        diferenca_calorias = self._calorias_dieta - calorias_itens

        percentual_cobertura = (
            (calorias_itens / self._calorias_dieta * 100) if self._calorias_dieta > 0 else 0.0
        )

        viavel = percentual_cobertura >= 80.0 or len(self._itens) == 0

        return {
            "tipo_dieta": "Oral",
            "textura": self._textura,

            "prescrito": {
                "calorias": self._calorias_dieta,
                "proteina_g": self._proteina_dieta,
                "carboidrato_g": self._carboidrato_dieta,
                "lipidio_g": self._lipidio_dieta,
                "fibra_g": self._fibra_g,
            },

            "alcancado_por_itens": {
                "calorias": calorias_itens,
                "proteina_g": proteina_itens,
                "carboidrato_g": carboidrato_itens,
                "lipidio_g": lipidio_itens,
                "quantidade_itens": len(self._itens),
            },

            "analise": {
                "diferenca_calorias": diferenca_calorias,
                "percentual_cobertura": round(percentual_cobertura, 2),
                "viavel": viavel,
                "mensagem": (
                    "Dieta completa" if percentual_cobertura >= 100 else
                    "Dieta viável" if viavel else
                    "AVISO: Dieta incompleta (< 80% cobertura)"
                )
            },

            "restricoes": {
                "permite_acucar": self._permite_acucar,
                "permite_sal": self._permite_sal,
                "proibidas": sorted(self._restricoes_proibidas)
            }
        }
    
    def validar_compatibilidade(self) -> bool:
        """
        Valida se dieta oral é viável.
        
        Regras:
        - Deve ter calorias prescritas > 0
        - Se tem itens, deve cobrir pelo menos 80% das calorias
        
        Returns:
            True se dieta é válida, False caso contrário
        """
        if self._calorias_dieta <= 0:
            return False
        
        if len(self._itens) == 0:
            return True
        
        nutrientes = self.calcular_nutrientes()
        return nutrientes["analise"]["viavel"]
    
    def __repr__(self) -> str:
        return (
            f"DietaOral(textura={self._textura}, "
            f"cal={self._calorias_dieta}, "
            f"fibra={self._fibra_g}g, ativo={self._ativo})"
        )


class DietaEnteral(Dieta):
    """
    Dieta enteral: nutrição via sonda (nasogástrica, gastrostomia, etc).
    
    Características:
    - Via de infusão (sonda nasogástrica, gastrostomia, etc)
    - Velocidade de infusão em ml/h
    - Volume total da prescrição
    - Cálculo de nutrientes baseado em volume infundido em 24h
    
    Atributos:
        _via_infusao: Tipo de sonda (ex: "nasogástrica")
        _velocidade_ml_h: Taxa de infusão em mililitros por hora
        _volume_total_ml: Volume total da prescrição em mililitros
        _calorias_dieta: Calorias totais prescritas
        _proteina_dieta: Proteína total prescrita (g)
        _carboidrato_dieta: Carboidrato total prescrito (g)
        _lipidio_dieta: Lipídio total prescrito (g)
    """
    
    VIAS_VALIDAS = {
        "nasogástrica",
        "gastrostomia",
        "jejunostomia",
        "nasoentérica",
        "cateter central"
    }
    
    def __init__(
        self,
        setor_clinico,
        via_infusao: str,
        velocidade_ml_h: float,
        volume_total_ml: float,
        calorias_dieta: float,
        proteina_dieta: float = 0.0,
        carboidrato_dieta: float = 0.0,
        lipidio_dieta: float = 0.0,
        usuario_responsavel: str = "sistema"
    ):
        """
        Cria nova dieta enteral com validações rigorosas.
        
        Args:
            setor_clinico: Setor responsável pela prescrição
            via_infusao: Tipo de via (deve estar em VIAS_VALIDAS)
            velocidade_ml_h: Velocidade de infusão > 0
            volume_total_ml: Volume total > 0
            calorias_dieta: Total de calorias prescritas > 0
            proteina_dieta: Proteína em gramas >= 0
            carboidrato_dieta: Carboidrato em gramas >= 0
            lipidio_dieta: Lipídio em gramas >= 0
            usuario_responsavel: Usuário que prescreveu
        
        Raises:
            ValueError: Se algum parâmetro for inválido
        """
        via_norm = via_infusao.strip().lower()
        if via_norm not in self.VIAS_VALIDAS:
            raise ValueError(
                f"Via '{via_infusao}' inválida. "
                f"Vias válidas: {', '.join(sorted(self.VIAS_VALIDAS))}"
            )
        
        # Validações numéricas
        if velocidade_ml_h <= 0:
            raise ValueError("Velocidade de infusão deve ser maior que 0 ml/h")
        
        if volume_total_ml <= 0:
            raise ValueError("Volume total deve ser maior que 0 ml")
        
        if calorias_dieta <= 0:
            raise ValueError("Calorias prescritas devem ser maiores que 0")
        
        # Validações de nutrientes
        for nome, valor in [
            ("proteína", proteina_dieta),
            ("carboidrato", carboidrato_dieta),
            ("lipídio", lipidio_dieta)
        ]:
            if valor < 0:
                raise ValueError(f"{nome} não pode ser negativo")
        
        # Cria descrição da dieta a partir da via
        descricao = f"Dieta Enteral via {via_infusao}"
        
        # Inicializa classe base (mixins)
        super().__init__(descricao, usuario_responsavel)
        
        # Armazena o setor clínico
        self._setor_clinico = setor_clinico
        
        # Atributos específicos de enteral 
        self._via_infusao = via_norm
        self._velocidade_ml_h = velocidade_ml_h
        self._volume_total_ml = volume_total_ml
        
        # Prescrição nutricional
        self._calorias_dieta = calorias_dieta
        self._proteina_dieta = proteina_dieta
        self._carboidrato_dieta = carboidrato_dieta
        self._lipidio_dieta = lipidio_dieta
    
    @property
    def via_infusao(self) -> str:
        """Retorna a via de infusão atual."""
        return self._via_infusao
    
    @via_infusao.setter
    def via_infusao(self, valor: str):
        """Altera a via de infusão com validação."""
        valor_norm = valor.strip().lower()
        if valor_norm not in self.VIAS_VALIDAS:
            raise ValueError(
                f"Via '{valor}' inválida. "
                f"Vias válidas: {', '.join(sorted(self.VIAS_VALIDAS))}"
            )
        self._via_infusao = valor_norm
        self.registrar_atualizacao()
    
    @property
    def velocidade_ml_h(self) -> float:
        """Retorna a velocidade de infusão em ml/h."""
        return self._velocidade_ml_h
    
    @velocidade_ml_h.setter
    def velocidade_ml_h(self, valor: float):
        """Altera a velocidade de infusão com validação."""
        if valor <= 0:
            raise ValueError("Velocidade deve ser maior que 0 ml/h")
        self._velocidade_ml_h = valor
        self.registrar_atualizacao()
    
    @property
    def volume_total_ml(self) -> float:
        """Retorna o volume total da prescrição em ml."""
        return self._volume_total_ml
    
    @volume_total_ml.setter
    def volume_total_ml(self, valor: float):
        """Altera o volume total com validação."""
        if valor <= 0:
            raise ValueError("Volume deve ser maior que 0 ml")
        self._volume_total_ml = valor
        self.registrar_atualizacao()
    
    @property
    def volume_infundido_24h(self) -> float:
        """
        Calcula quantos ml serão infundidos em 24 horas.
        
        Fórmula: velocidade_ml_h * 24
        """
        return self._velocidade_ml_h * 24
    
    @property
    def percentual_volume_24h(self) -> float:
        """
        Retorna percentual do volume total que será atingido em 24h.
        
        Fórmula: (volume_infundido_24h / volume_total_ml) * 100
        """
        if self._volume_total_ml <= 0:
            return 0.0
        return (self.volume_infundido_24h / self._volume_total_ml) * 100
    
    
    def calcular_nutrientes(self) -> dict[str, float | dict]:
        """
        Calcula nutrientes fornecidos pela dieta enteral.
        
        Para enteral, o cálculo leva em conta o volume infundido em 24h.
        Se o volume infundido em 24h < volume total, assume-se entrega parcial.
        
        Se há itens no cardápio (composição da fórmula enteral),
        soma-se os nutrientes dos itens; caso contrário, usa prescrição.
        
        Returns:
            dict com: tipo_dieta, via_infusao, prescrito, alcancado, analise
        """
        calorias_itens = sum(item.calorias for item in self._itens) if self._itens else 0.0
        proteina_itens = sum(item.proteinas for item in self._itens) if self._itens else 0.0
        carboidrato_itens = sum(item.carboidratos for item in self._itens) if self._itens else 0.0
        lipidio_itens = sum(item.gorduras for item in self._itens) if self._itens else 0.0
        
        # Calcula nutrientes alcançados considerando volume infundido
        # Se volume infundido em 24h < volume total, há deficit
        percentual_volume = self.percentual_volume_24h / 100.0 if self.percentual_volume_24h > 0 else 0.0
        
        calorias_alcancadas = (
            (calorias_itens if calorias_itens > 0 else self._calorias_dieta) * percentual_volume
        )
        proteina_alcancada = (
            (proteina_itens if proteina_itens > 0 else self._proteina_dieta) * percentual_volume
        )
        carboidrato_alcancado = (
            (carboidrato_itens if carboidrato_itens > 0 else self._carboidrato_dieta) * percentual_volume
        )
        lipidio_alcancado = (
            (lipidio_itens if lipidio_itens > 0 else self._lipidio_dieta) * percentual_volume
        )
        
        # Calorias prescritas (considera o volume total, não o infundido)
        calorias_prescritas = calorias_itens if calorias_itens > 0 else self._calorias_dieta
        
        diferenca_calorias = calorias_prescritas - calorias_alcancadas
        
        percentual_cobertura = (
            (calorias_alcancadas / calorias_prescritas * 100) 
            if calorias_prescritas > 0 else 0.0
        )
        
        # Viável: volume 24h >= volume total OU cobertura nutricional >= 80% (consistente com DietaOral)
        volume_completo = self.percentual_volume_24h >= 100.0
        viavel = volume_completo or percentual_cobertura >= 80.0
        
        return {
            "tipo_dieta": "Enteral",
            "via_infusao": self._via_infusao,
            "velocidade_ml_h": self._velocidade_ml_h,
            "volume_infundido_24h": round(self.volume_infundido_24h, 2),
            "volume_total_ml": self._volume_total_ml,
            "percentual_volume_24h": round(self.percentual_volume_24h, 2),
            
            "prescrito": {
                "calorias": calorias_prescritas,
                "proteina_g": (proteina_itens if proteina_itens > 0 else self._proteina_dieta),
                "carboidrato_g": (carboidrato_itens if carboidrato_itens > 0 else self._carboidrato_dieta),
                "lipidio_g": (lipidio_itens if lipidio_itens > 0 else self._lipidio_dieta),
            },
            
            "alcancado_em_24h": {
                "calorias": round(calorias_alcancadas, 2),
                "proteina_g": round(proteina_alcancada, 2),
                "carboidrato_g": round(carboidrato_alcancado, 2),
                "lipidio_g": round(lipidio_alcancado, 2),
                "quantidade_itens": len(self._itens),
            },
            
            "analise": {
                "diferenca_calorias": round(diferenca_calorias, 2),
                "percentual_cobertura_24h": round(percentual_cobertura, 2),
                "volume_completo": volume_completo,
                "viavel": viavel,
                "mensagem": (
                    "Dieta enteral completa em 24h" if volume_completo else
                    "Dieta enteral em andamento (incompleta)" if viavel else
                    "AVISO: Dieta enteral inadequada"
                )
            }
        }
    
    def validar_compatibilidade(self) -> bool:
        """
        Valida se dieta enteral é viável.
        
        Regras:
        - Via de infusão deve ser válida
        - Velocidade > 0
        - Volume total > 0
        - Calorias prescritas > 0
        - Se tem itens, compatibilidade nutricional é verificada
        
        Returns:
            True se dieta é válida, False caso contrário
        """
        try:
            if self._via_infusao not in self.VIAS_VALIDAS:
                return False
            
            if self._velocidade_ml_h <= 0 or self._volume_total_ml <= 0:
                return False
            
            calorias_prescritas = (
                sum(item.calorias for item in self._itens) 
                if self._itens else self._calorias_dieta
            )
            
            if calorias_prescritas <= 0:
                return False
            
            # Se há itens, verifica compatibilidade
            if len(self._itens) > 0:
                nutrientes = self.calcular_nutrientes()
                return nutrientes["analise"]["viavel"]
            
            return True
        except (ValueError, KeyError, AttributeError):
            return False
    
    def __repr__(self) -> str:
        return (
            f"DietaEnteral(via={self._via_infusao}, "
            f"vel={self._velocidade_ml_h}ml/h, "
            f"vol={self._volume_total_ml}ml, "
            f"cal={self._calorias_dieta}, ativo={self._ativo})"
        )