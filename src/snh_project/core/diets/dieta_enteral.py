from ..base import Dieta


class DietaEnteral(Dieta):
    """
    Dieta Enteral - via sonda (tubo).
    
    Para pacientes que não conseguem se alimentar normalmente via boca.
    Nutrição administrada através de sonda diretamente no trato gastrointestinal.
    
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
        "cateter central",
        "sng"
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
            raise ValueError("Velocidade de infusão deve ser maior que 0")

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
            raise ValueError("Velocidade deve ser maior que 0")
        self._velocidade_ml_h = valor
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
            f"gramas_porção={self._quantidade_gramas_por_porção}g, "
            f"porcoes={self._porcoes_diarias}, "
            f"equipo={self._tipo_equipo}, "
            f"ativo={self._ativo})"
        )
