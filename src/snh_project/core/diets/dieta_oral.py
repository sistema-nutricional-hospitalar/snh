from typing import List
from ..base import Dieta
from .item_cardapio import ItemCardapio


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
        except (ValueError, AttributeError):
            return False

    def __repr__(self) -> str:
        return (
            f"DietaOral(textura={self._textura}, "
            f"refeicoes={self._numero_refeicoes}, "
            f"tipo={self._tipo_refeicao}, "
            f"itens={len(self._itens)}, "
            f"ativo={self._ativo})"
        )
