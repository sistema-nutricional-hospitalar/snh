from typing import Optional, List
from .base import Dieta


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


class DietaOral(Dieta):
    """
    Dieta via alimentação normal (por boca).
    
    Para pacientes que conseguem se alimentar normalmente.
    
    Características:
    - Textura de preparação (normal, mole, pastosa, líquida)
    - Número de refeições por dia
    - Tipo de refeição (desjejum, almoço, lanche, janta, etc)
    - Restrições alimentares proibidas
    
    Atributos:
        _textura: Forma de preparação (normal, mole, pastosa, liquida)
        _numero_refeicoes: Quantidade de refeições por dia
        _tipo_refeicao: Tipo da refeição (desjejum, almoço, lanche da tarde, janta)
        _restricoes_proibidas: Conjunto de restrições alimentares proibidas
    """
    
    # Constante: texturas válidas
    TEXTURAS_VALIDAS = {"normal", "mole", "pastosa", "liquida"}
    
    def __init__(
        self,
        textura: str,
        numero_refeicoes: int,
        tipo_refeicao: str,
        descricao: str = "",
        usuario_responsavel: str = "sistema"
    ):
        """
        Cria uma nova DietaOral com validações rigorosas.
        
        Args:
            textura: Forma de preparação (normal, mole, pastosa, liquida)
            numero_refeicoes: Quantidade de refeições por dia (> 0)
            tipo_refeicao: Tipo de refeição (desjejum, almoço, lanche, janta, etc)
            descricao: Notas adicionais (opcional)
            usuario_responsavel: Quem prescreveu (padrão: "sistema")
        
        Raises:
            ValueError: Se parâmetros inválidos
        """
        if textura.lower() not in self.TEXTURAS_VALIDAS:
            raise ValueError(
                f"Textura inválida. Opções: {', '.join(self.TEXTURAS_VALIDAS)}"
            )
        
        if numero_refeicoes <= 0:
            raise ValueError("Número de refeições deve ser maior que 0")

        tipo_refeicao_norm = tipo_refeicao.strip().lower()
        TIPOS_REFEICAO = {"desjejum", "lanche", "ceia", "janta", "almoço", "almoco", "lanche da tarde"}
        if tipo_refeicao_norm not in TIPOS_REFEICAO:
            raise ValueError(f"Tipo de refeição inválido: {tipo_refeicao}")

        super().__init__(
            descricao=descricao,
            usuario_responsavel=usuario_responsavel
        )

        self._textura: str = textura.lower()
        self._numero_refeicoes: int = numero_refeicoes
        self._tipo_refeicao: str = tipo_refeicao_norm
        self._restricoes_proibidas: set[str] = set()
    
    @property
    def textura(self) -> str:
        """Retorna a textura da dieta"""
        return self._textura
    
    
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
        Retorna metadados essenciais da dieta oral.
        
        Não realiza cálculos complexos — apenas consolida informações de
        textura, número de refeições, tipo de refeição e restrições.
        
        Returns:
            dict com tipo_dieta, textura, prescrito (numero_refeicoes, tipo_refeicao),
            restricoes (proibidas) e quantidade_itens
        """
        return {
            "tipo_dieta": "Oral",
            "textura": self._textura,
            "prescrito": {
                "numero_refeicoes": self._numero_refeicoes,
                "tipo_refeicao": self._tipo_refeicao,
            },
            "restricoes": {
                "proibidas": sorted(self._restricoes_proibidas)
            },
            "quantidade_itens": len(self._itens)
        }
    
    def validar_compatibilidade(self) -> bool:
        """
        Valida se a configuração básica da dieta oral é consistente.
        
        Regras simples:
        - textura deve estar em TEXTURAS_VALIDAS
        - número de refeições > 0
        
        Returns:
            True se ok, False caso contrário
        """
        try:
            if self._textura not in self.TEXTURAS_VALIDAS:
                return False
            if self._numero_refeicoes <= 0:
                return False
            return True
        except Exception:
            return False
    
    def __repr__(self) -> str:
        return (
            f"DietaOral(textura={self._textura}, refeicoes={self._numero_refeicoes}, "
            f"tipo_refeicao={self._tipo_refeicao}, ativo={self._ativo})"
        )


class DietaEnteral(Dieta):
    """
    Dieta enteral: nutrição via sonda (nasogástrica, gastrostomia, etc).
    
    Modelagem simplificada focada em operacionalização:
    - Via de infusão (tipo de sonda)
    - Velocidade de infusão em ml/h
    - Quantidade de gramas por porção
    - Número de porções diárias
    - Tipo de equipo (bomba ou gravitacional)
    
    Regras de equipo:
    - Se tipo_equipo='gravitacional': uma bomba por porção
    - Se tipo_equipo='bomba': uma bomba para todo dia
    
    Atributos:
        _via_infusao: Tipo de sonda (ex: "nasogástrica")
        _velocidade_ml_h: Taxa de infusão em mililitros por hora
        _quantidade_gramas_por_porção: Gramas de fórmula por porção
        _porcoes_diarias: Número de porções prescritas por dia
        _tipo_equipo: "bomba" ou "gravitacional"
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
        quantidade_gramas_por_porção: float,
        porcoes_diarias: int = 1,
        tipo_equipo: str = "bomba",
        usuario_responsavel: str = "sistema"
    ):
        """
        Cria nova dieta enteral com validações rigorosas.
        
        Args:
            setor_clinico: Setor clínico responsável
            via_infusao: Tipo de via (nasogástrica, gastrostomia, etc)
            velocidade_ml_h: Velocidade de infusão em ml/h (> 0)
            quantidade_gramas_por_porção: Gramas de fórmula por porção (> 0)
            porcoes_diarias: Número de porções por dia (>= 1, padrão: 1)
            tipo_equipo: "bomba" ou "gravitacional" (padrão: "bomba")
            usuario_responsavel: Usuário que prescreveu
        
        Raises:
            ValueError: Se parâmetros fora dos intervalos válidos
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

        if quantidade_gramas_por_porção <= 0:
            raise ValueError("quantidade_gramas_por_porção deve ser maior que 0")
        
        # Cria descrição da dieta a partir da via
        descricao = f"Dieta Enteral via {via_infusao}"

        # Inicializa classe base (mixins)
        super().__init__(descricao, usuario_responsavel)

        # Armazena o setor clínico
        self._setor_clinico = setor_clinico

        # Atributos específicos de enteral
        self._via_infusao = via_norm
        self._velocidade_ml_h = velocidade_ml_h

        # Prescrição simplificada: gramas por porção e porções diárias
        self._quantidade_gramas_por_porção = quantidade_gramas_por_porção

        # Equipo e porções
        tipo_eq_norm = tipo_equipo.strip().lower()
        if tipo_eq_norm not in {"bomba", "gravitacional"}:
            raise ValueError("tipo_equipo inválido. Valores aceitos: 'bomba', 'gravitacional'")

        if not isinstance(porcoes_diarias, int) or porcoes_diarias < 1:
            raise ValueError("porcoes_diarias deve ser inteiro maior ou igual a 1")

        self._tipo_equipo = tipo_eq_norm
        self._porcoes_diarias = porcoes_diarias
    
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
    def tipo_equipo(self) -> str:
        """Retorna o tipo de equipo ('bomba' ou 'gravitacional')."""
        return self._tipo_equipo

    @tipo_equipo.setter
    def tipo_equipo(self, valor: str):
        v = valor.strip().lower()
        if v not in {"bomba", "gravitacional"}:
            raise ValueError("tipo_equipo inválido. Valores aceitos: 'bomba', 'gravitacional'")
        self._tipo_equipo = v
        self.registrar_atualizacao()

    @property
    def porcoes_diarias(self) -> int:
        """Retorna o número de porções diárias."""
        return self._porcoes_diarias

    @porcoes_diarias.setter
    def porcoes_diarias(self, valor: int):
        if not isinstance(valor, int) or valor < 1:
            raise ValueError("porcoes_diarias deve ser inteiro maior ou igual a 1")
        self._porcoes_diarias = valor
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
        # Removido: cálculo baseado em volume total — não aplicável na modelagem atual
        return 0.0
    
    
    def calcular_nutrientes(self) -> dict[str, float | dict]:
        """
        Retorna metadados operacionais da dieta enteral.
        
        Cálculo realizado:
        - total_gramas_diarias = quantidade_gramas_por_porção * porcoes_diarias
        
        Returns:
            dict com tipo_dieta, via_infusao, tipo_equipo, porcoes_diarias,
            quantidade_gramas_por_porção, total_gramas_diarias, velocidade_ml_h,
            e flags equipo_por_porção/equipo_unico_por_dia
        """
        # Modelagem simplificada: apenas gramas por porção, porções diárias e vazão
        total_gramas_diarias = self._quantidade_gramas_por_porção * self._porcoes_diarias

        return {
            "tipo_dieta": "Enteral",
            "via_infusao": self._via_infusao,
            "tipo_equipo": self._tipo_equipo,
            "porcoes_diarias": self._porcoes_diarias,
            "quantidade_gramas_por_porção": self._quantidade_gramas_por_porção,
            "total_gramas_diarias": total_gramas_diarias,
            "velocidade_ml_h": self._velocidade_ml_h,
            # Se gravitacional -> equipo por porção; se bomba -> equipo único por dia
            "equipo_por_porção": (self._tipo_equipo == "gravitacional"),
            "equipo_unico_por_dia": (self._tipo_equipo == "bomba"),
        }
    
    def validar_compatibilidade(self) -> bool:
        """
        Valida se a configuração de dieta enteral é consistente.
        
        Regras:
        - Via de infusão deve estar em VIAS_VALIDAS
        - Velocidade de infusão > 0
        - Quantidade de gramas por porção > 0
        - Número de porções >= 1
        - Tipo de equipo válido ("bomba" ou "gravitacional")
        
        Returns:
            True se todas as validações passam, False caso contrário
        """
        try:
            if self._via_infusao not in self.VIAS_VALIDAS:
                return False
            
            if self._velocidade_ml_h <= 0:
                return False
            
            if self._quantidade_gramas_por_porção <= 0:
                return False
            
            if self._porcoes_diarias < 1:
                return False
            
            if self._tipo_equipo not in {"bomba", "gravitacional"}:
                return False
            
            return True
        except (ValueError, AttributeError):
            return False
    
    def __repr__(self) -> str:
        return (
            f"DietaEnteral(via={self._via_infusao}, "
            f"vel={self._velocidade_ml_h}ml/h, "
            f"vol={self._volume_total_ml}ml, "
            f"cal={self._calorias_dieta}, ativo={self._ativo})"
        )