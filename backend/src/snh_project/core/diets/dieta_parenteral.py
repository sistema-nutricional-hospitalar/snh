from typing import Optional
from ..base import Dieta


class DietaParenteral(Dieta):
    """
    Dieta parenteral: nutrição intravenosa (pela veia).
    
    Para pacientes que não podem usar o trato digestivo devido a:
    - Cirurgias gastrointestinais
    - Obstruções intestinais
    - Síndrome do intestino curto
    - Pancreatite grave
    
    Características:
    - Via de acesso (periférico ou central)
    - Volume total em ml
    - Composição (glicose + aminoácidos + lipídios)
    - Velocidade de infusão
    
    Atributos:
        _tipo_acesso: str (periférico, central)
        _volume_ml_dia: float (volume total prescrito por dia)
        _composicao: str (descrição da fórmula)
        _velocidade_ml_h: float (taxa de infusão)
    """
    
    # Constantes: tipos de acesso válidos
    TIPOS_ACESSO_VALIDOS = {"periférico", "central", "cateter central", "picc"}
    
    def __init__(
        self,
        tipo_acesso: str,
        volume_ml_dia: float,
        composicao: str,
        velocidade_ml_h: float,
        descricao: str = "",
        usuario_responsavel: str = "sistema"
    ):
        """
        Cria uma nova DietaParenteral com validações rigorosas.
        
        Args:
            tipo_acesso: Tipo de acesso venoso (periférico, central)
            volume_ml_dia: Volume total prescrito por dia em ml (> 0)
            composicao: Descrição da composição (ex: "Glicose 50% + Aminoácidos 10% + Lipídios 20%")
            velocidade_ml_h: Velocidade de infusão em ml/h (> 0)
            descricao: Notas adicionais (opcional)
            usuario_responsavel: Quem prescreveu (padrão: "sistema")
        
        Raises:
            ValueError: Se parâmetros inválidos
        
        Examples:
            >>> dieta = DietaParenteral(
            ...     tipo_acesso="central",
            ...     volume_ml_dia=2000.0,
            ...     composicao="Glicose 50% + Aminoácidos 10% + Lipídios 20%",
            ...     velocidade_ml_h=83.3
            ... )
        """
        # Validação do tipo de acesso
        tipo_acesso_norm = tipo_acesso.strip().lower()
        if tipo_acesso_norm not in self.TIPOS_ACESSO_VALIDOS:
            raise ValueError(
                f"Tipo de acesso inválido: '{tipo_acesso}'. "
                f"Opções válidas: {', '.join(sorted(self.TIPOS_ACESSO_VALIDOS))}"
            )
        
        # Validações numéricas
        if volume_ml_dia <= 0:
            raise ValueError("Volume por dia deve ser maior que 0 ml")
        
        if velocidade_ml_h <= 0:
            raise ValueError("Velocidade de infusão deve ser maior que 0 ml/h")
        
        # Validação da composição
        if not composicao or len(composicao.strip()) == 0:
            raise ValueError("Composição não pode ser vazia")
        
        # Validação de consistência: velocidade deve permitir infundir o volume em 24h
        volume_teorico_24h = velocidade_ml_h * 24
        if volume_teorico_24h < volume_ml_dia * 0.8 or volume_teorico_24h > volume_ml_dia * 1.2:
            # Permite 20% de tolerância
            raise ValueError(
                f"Velocidade {velocidade_ml_h} ml/h infundiria {volume_teorico_24h:.1f} ml em 24h, "
                f"mas volume prescrito é {volume_ml_dia} ml. Ajuste a velocidade ou o volume."
            )
        
        # Inicializa classe base
        if not descricao:
            descricao = f"Dieta Parenteral via {tipo_acesso}"
        
        super().__init__(
            descricao=descricao,
            usuario_responsavel=usuario_responsavel
        )
        
        # Atributos específicos de parenteral
        self._tipo_acesso = tipo_acesso_norm
        self._volume_ml_dia = volume_ml_dia
        self._composicao = composicao.strip()
        self._velocidade_ml_h = velocidade_ml_h
    
    
    @property
    def tipo_acesso(self) -> str:
        """Retorna o tipo de acesso venoso"""
        return self._tipo_acesso
    
    @tipo_acesso.setter
    def tipo_acesso(self, valor: str):
        """Altera o tipo de acesso com validação"""
        valor_norm = valor.strip().lower()
        if valor_norm not in self.TIPOS_ACESSO_VALIDOS:
            raise ValueError(
                f"Tipo de acesso inválido: '{valor}'. "
                f"Opções válidas: {', '.join(sorted(self.TIPOS_ACESSO_VALIDOS))}"
            )
        self._tipo_acesso = valor_norm
        self.registrar_atualizacao()
    
    @property
    def volume_ml_dia(self) -> float:
        """Retorna o volume total prescrito por dia"""
        return self._volume_ml_dia
    
    @volume_ml_dia.setter
    def volume_ml_dia(self, valor: float):
        """Altera o volume total com validação"""
        if valor <= 0:
            raise ValueError("Volume por dia deve ser maior que 0 ml")
        self._volume_ml_dia = valor
        self.registrar_atualizacao()
    
    @property
    def composicao(self) -> str:
        """Retorna a composição da dieta parenteral"""
        return self._composicao
    
    @composicao.setter
    def composicao(self, valor: str):
        """Altera a composição com validação"""
        if not valor or len(valor.strip()) == 0:
            raise ValueError("Composição não pode ser vazia")
        self._composicao = valor.strip()
        self.registrar_atualizacao()
    
    @property
    def velocidade_ml_h(self) -> float:
        """Retorna a velocidade de infusão em ml/h"""
        return self._velocidade_ml_h
    
    @velocidade_ml_h.setter
    def velocidade_ml_h(self, valor: float):
        """Altera a velocidade de infusão com validação"""
        if valor <= 0:
            raise ValueError("Velocidade de infusão deve ser maior que 0 ml/h")
        self._velocidade_ml_h = valor
        self.registrar_atualizacao()
    
    @property
    def volume_infundido_24h(self) -> float:
        """
        Calcula quantos ml serão infundidos em 24 horas.
        
        Fórmula: velocidade_ml_h * 24
        
        Returns:
            float: Volume em ml que será infundido em 24h
        """
        return self._velocidade_ml_h * 24
    
    @property
    def percentual_volume_atingido(self) -> float:
        """
        Calcula percentual do volume prescrito que será atingido em 24h.
        
        Fórmula: (volume_infundido_24h / volume_ml_dia) * 100
        
        Returns:
            float: Percentual (0-100+)
        """
        return (self.volume_infundido_24h / self._volume_ml_dia) * 100
    
    @property
    def tempo_para_infundir_horas(self) -> float:
        """
        Calcula quanto tempo levará para infundir todo o volume.
        
        Fórmula: volume_ml_dia / velocidade_ml_h
        
        Returns:
            float: Tempo em horas
        """
        return self._volume_ml_dia / self._velocidade_ml_h
    
    
    def calcular_nutrientes(self) -> dict[str, float | dict | str]:
        """
        Retorna metadados operacionais da dieta parenteral.
        
        Não realiza cálculos nutricionais complexos - apenas consolida
        informações de tipo de acesso, volume, composição e velocidade.
        
        Returns:
            dict: Estrutura com tipo_dieta, tipo_acesso, volume_ml_dia,
                  composicao, velocidade_ml_h, volume_infundido_24h,
                  percentual_volume_atingido, tempo_para_infundir_horas
        
        Example:
            >>> resultado = dieta.calcular_nutrientes()
            >>> print(resultado['tipo_dieta'])
            'Parenteral'
            >>> print(resultado['percentual_volume_atingido'])
            100.0
        """
        return {
            "tipo_dieta": "Parenteral",
            "tipo_acesso": self._tipo_acesso,
            "volume_ml_dia": self._volume_ml_dia,
            "composicao": self._composicao,
            "velocidade_ml_h": self._velocidade_ml_h,
            "volume_infundido_24h": self.volume_infundido_24h,
            "percentual_volume_atingido": self.percentual_volume_atingido,
            "tempo_para_infundir_horas": self.tempo_para_infundir_horas,
            "quantidade_itens": len(self._itens) 
        }
    
    def validar_compatibilidade(self) -> bool:
        """
        Valida se a configuração da dieta parenteral é consistente.
        
        Regras:
        - Tipo de acesso deve estar em TIPOS_ACESSO_VALIDOS
        - Volume por dia > 0
        - Velocidade > 0
        - Composição não vazia
        - Velocidade deve permitir infundir o volume em 24h (±20%)
        
        Returns:
            bool: True se todas as validações passam, False caso contrário
        """
        try:
            if self._tipo_acesso not in self.TIPOS_ACESSO_VALIDOS:
                return False
            
            if self._volume_ml_dia <= 0:
                return False
            
            if self._velocidade_ml_h <= 0:
                return False
            
            if not self._composicao or len(self._composicao.strip()) == 0:
                return False
            
            # Valida consistência volume vs velocidade (±20% tolerância)
            volume_teorico = self._velocidade_ml_h * 24
            if volume_teorico < self._volume_ml_dia * 0.8:
                return False
            if volume_teorico > self._volume_ml_dia * 1.2:
                return False
            
            return True
        except (ValueError, AttributeError):
            return False
    
    
    def __repr__(self) -> str:
        """Representação em string para debug"""
        return (
            f"DietaParenteral(acesso={self._tipo_acesso}, "
            f"volume={self._volume_ml_dia}ml, "
            f"vel={self._velocidade_ml_h}ml/h, "
            f"ativo={self._ativo})"
        )