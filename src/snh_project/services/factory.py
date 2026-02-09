from typing import Dict, Any
from .diet import DietaOral, DietaEnteral, Dieta

class DietaFactory:
    """
    Factory responsável por instanciar os objetos de dieta corretos,
    garantindo que os dados recebidos (ex: de um formulário ou API)
    sejam mapeados para os argumentos exigidos pelas classes atualizadas.
    """

    @staticmethod
    def criar_dieta(tipo: str, dados: Dict[str, Any]) -> Dieta:
        """
        Cria uma instância de Dieta baseada no tipo.

        Args:
            tipo: 'oral' ou 'enteral'
            dados: Dicionário contendo os parâmetros necessários.
        
        Raises:
            ValueError: Se o tipo for desconhecido ou dados forem inválidos.
        """
        tipo_normalizado = tipo.strip().lower()

        if tipo_normalizado == 'oral':
            return DietaFactory._criar_dieta_oral(dados)
        
        elif tipo_normalizado == 'enteral':
            return DietaFactory._criar_dieta_enteral(dados)
        
        else:
            raise ValueError(f"Tipo de dieta desconhecido: {tipo}")

    @staticmethod
    def _criar_dieta_oral(dados: Dict[str, Any]) -> DietaOral:
        # Extração de dados com tratamento de tipos básicos
        try:
            # Tenta converter numero_refeicoes para int se vier como string
            num_refeicoes = int(dados.get('numero_refeicoes', 0))
        except (ValueError, TypeError):
            num_refeicoes = 0

        return DietaOral(
            textura=dados.get('textura', 'normal'),
            numero_refeicoes=num_refeicoes,
            tipo_refeicao=dados.get('tipo_refeicao', ''),
            descricao=dados.get('descricao', ''),
            usuario_responsavel=dados.get('usuario_responsavel', 'sistema')
        )

    @staticmethod
    def _criar_dieta_enteral(dados: Dict[str, Any]) -> DietaEnteral:
        # Conversões de tipos para garantir que o diet.py não reclame
        try:
            velocidade = float(dados.get('velocidade_ml_h', 0))
            gramas = float(dados.get('quantidade_gramas_por_porção', 0))
            porcoes = int(dados.get('porcoes_diarias', 1))
        except (ValueError, TypeError):
            # Se a conversão falhar, passamos 0 ou 1 e deixamos o diet.py 
            # levantar o ValueError com a mensagem correta
            velocidade = 0.0
            gramas = 0.0
            porcoes = 1

        return DietaEnteral(
            # OBRIGATÓRIO: Novo campo exigido pelo diet.py do seu amigo
            setor_clinico=dados.get('setor_clinico', 'Não Informado'),
            
            via_infusao=dados.get('via_infusao', ''),
            velocidade_ml_h=velocidade,
            
            # ATENÇÃO: Nome do argumento com acentuação conforme definido na classe
            quantidade_gramas_por_porção=gramas,
            
            porcoes_diarias=porcoes,
            tipo_equipo=dados.get('tipo_equipo', 'bomba'),
            usuario_responsavel=dados.get('usuario_responsavel', 'sistema')
        )