from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .diet import ItemCardapio


class AuditoriaMixin:
    """Rastreia criação e atualização de entidades do domínio"""
    
    def __init__(self, usuario_responsavel: str = "sistema"):
        self._criado_em: datetime = datetime.now()
        self._atualizado_em: datetime = datetime.now()
        self._usuario_responsavel: str = usuario_responsavel
    
    @property
    def criado_em(self) -> datetime:
        return self._criado_em
    
    @property
    def atualizado_em(self) -> datetime:
        return self._atualizado_em
    
    @property
    def usuario_responsavel(self) -> str:
        return self._usuario_responsavel
    
    def registrar_atualizacao(self) -> None:
        self._atualizado_em = datetime.now()

class StatusDietaMixin:
    """Gerencia status de prescrições de dieta"""
    
    def __init__(self):
        self._ativo: bool = True
        self._data_inicio: datetime = datetime.now()
        self._data_fim: Optional[datetime] = None
    
    @property
    def ativo(self) -> bool:
        return self._ativo
    
    @property
    def data_inicio(self) -> datetime:
        return self._data_inicio
    
    @property
    def data_fim(self) -> Optional[datetime]:
        return self._data_fim
    
    def encerrar_dieta(self) -> None:
        if not self._ativo:
            raise ValueError("Dieta já foi encerrada")
        self._ativo = False
        self._data_fim = datetime.now()


class Dieta(ABC, AuditoriaMixin, StatusDietaMixin):
    """
    Classe abstrata que define o contrato para qualquer dieta hospitalar.
    
    Herança Múltipla (Mixins):
        - AuditoriaMixin: fornece criado_em, atualizado_em, usuario_responsavel
        - StatusDietaMixin: fornece ativo, data_inicio, data_fim, encerrar_dieta()
    
    Método Abstrato:
        - calcular_nutrientes(): cada subclasse (DietaOral, DietaEnteral) implementa
          sua própria lógica de cálculo
    
    Atributos:
        _descricao: Descrição ou observações sobre a dieta
        _itens: Lista de ItemCardapio que compõem a dieta
    """
    
    def __init__(self, descricao: str = "", usuario_responsavel: str = "sistema"):
        """
        Inicializa uma dieta com os mixins necessários.
        
        Args:
            descricao: Notas sobre a dieta (ex: "Dieta Branda")
            usuario_responsavel: Quem prescreveu (ex: "Dra. Silva")
        """
        # Inicializa os Mixins na ordem correta
        AuditoriaMixin.__init__(self, usuario_responsavel)
        StatusDietaMixin.__init__(self)
        
        # Atributos específicos da dieta
        self._descricao: str = descricao.strip()
        self._itens: list["ItemCardapio"] = []
    
    
    @property
    def descricao(self) -> str:
        """Retorna a descrição da dieta"""
        return self._descricao
    
    @property
    def itens(self) -> list["ItemCardapio"]:
        """
        Retorna uma CÓPIA da lista de itens (encapsulamento).
        """
        return self._itens.copy()
    
    @property
    def quantidade_itens(self) -> int:
        """Retorna a quantidade de itens nesta dieta"""
        return len(self._itens)
    
    def adicionar_item(self, item: "ItemCardapio") -> None:
        """
        Adiciona um novo item à dieta.
        
        Args:
            item: ItemCardapio a ser adicionado
        
        Raises:
            TypeError: Se item não for do tipo ItemCardapio
        """
        from .diet import ItemCardapio
        
        if not isinstance(item, ItemCardapio):
            raise TypeError(f"Esperado ItemCardapio, recebido {type(item).__name__}")
        
        self._itens.append(item)
        self.registrar_atualizacao()
    
    def remover_item(self, nome_item: str) -> bool:
        """
        Remove um item pelo nome.
        
        Args:
            nome_item: Nome do item a remover
        
        Returns:
            True se removeu, False se não encontrou
        """
        for idx, item in enumerate(self._itens):
            if item.nome == nome_item:
                self._itens.pop(idx)
                self.registrar_atualizacao()
                return True
        return False
    
    def obter_item(self, nome_item: str) -> Optional["ItemCardapio"]:
        """
        Busca um item pelo nome.
        
        Args:
            nome_item: Nome do item
        
        Returns:
            ItemCardapio se encontrado, None caso contrário
        """
        for item in self._itens:
            if item.nome == nome_item:
                return item
        return None
    
    def limpar_itens(self) -> None:
        """Remove todos os itens da dieta"""
        self._itens.clear()
        self.registrar_atualizacao()
    
    @abstractmethod
    def calcular_nutrientes(self) -> dict[str, float | dict]:
        """
        Calcula o total de nutrientes da dieta.
        
        Cada tipo de dieta implementa sua própria lógica polimórfica.
        
        Returns:
            Dicionário estruturado com nutrientes, análise e metadados.
            - DietaOral: chaves simples (calorias, proteinas, etc) + análise
            - DietaEnteral: idem + volume_infundido_24h, percentual_volume_24h
        
        Exemplo (genérico):
            {
                'tipo_dieta': 'Oral' | 'Enteral',
                'prescrito': {'calorias': 1500.0, ...},
                'alcancado_por_itens': {...} | 'alcancado_em_24h': {...},
                'analise': {'viavel': True, 'mensagem': '...'}
            }
        """
        pass