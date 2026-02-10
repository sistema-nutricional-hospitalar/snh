from typing import Dict, Any
from ..core.diet import DietaOral, DietaEnteral
from ..core.base import Dieta

class DietaFactory:
    """
    Implementação do Padrão Factory Method.
    
    Responsabilidade: Centralizar a criação de objetos da hierarquia 'Dieta'.
    Isso desacopla o código cliente (Prescrição) das classes concretas (Oral/Enteral).
    
    A Factory valida os dados de entrada e garante que as dietas sejam criadas
    com todos os parâmetros obrigatórios, fornecendo mensagens de erro claras
    quando algo está faltando ou inválido.
    """

    @staticmethod
    def criar_dieta(tipo: str, dados: Dict[str, Any]) -> Dieta:
        """
        Fabrica uma instância de Dieta baseada no tipo solicitado.

        Args:
            tipo (str): O tipo de dieta ('oral' ou 'enteral').
            dados (Dict[str, Any]): Dicionário contendo os parâmetros necessários.
        
        Returns:
            Dieta: Uma instância validada de DietaOral ou DietaEnteral.
        
        Raises:
            ValueError: Se o tipo for desconhecido ou dados forem inválidos.
        
        Exemplo:
            dados_oral = {
                'textura': 'normal',
                'numero_refeicoes': 5,
                'tipo_refeicao': 'almoço',
                'descricao': 'Dieta Geral',
                'usuario_responsavel': 'Dr. Silva'
            }
            dieta = DietaFactory.criar_dieta('oral', dados_oral)
        """
        tipo_normalizado = tipo.strip().lower()

        if tipo_normalizado == 'oral':
            return DietaFactory._criar_dieta_oral(dados)
        
        elif tipo_normalizado == 'enteral':
            return DietaFactory._criar_dieta_enteral(dados)
        
        else:
            raise ValueError(
                f"Tipo de dieta desconhecido: '{tipo}'. "
                f"Tipos válidos: 'oral', 'enteral'"
            )

    @staticmethod
    def _criar_dieta_oral(dados: Dict[str, Any]) -> DietaOral:
        """
        Cria uma instância de DietaOral com validação de parâmetros.
        
        Args:
            dados: Dicionário com parâmetros da dieta oral
        
        Returns:
            DietaOral: Instância criada e validada
        
        Raises:
            ValueError: Se parâmetros obrigatórios estiverem faltando ou inválidos
        """
        # Lista de parâmetros obrigatórios
        params_obrigatorios = ['textura', 'numero_refeicoes', 'tipo_refeicao']
        
        # Valida presença de parâmetros obrigatórios
        faltando = [p for p in params_obrigatorios if p not in dados]
        if faltando:
            raise ValueError(
                f"Dieta Oral exige os seguintes parâmetros: {', '.join(faltando)}"
            )
        
        # Validação e conversão de tipo para numero_refeicoes
        try:
            num_refeicoes = int(dados['numero_refeicoes'])
            if num_refeicoes <= 0:
                raise ValueError("numero_refeicoes deve ser maior que 0")
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Parâmetro 'numero_refeicoes' inválido. "
                f"Esperado número inteiro positivo, recebido: {dados.get('numero_refeicoes')}"
            ) from e

        # Cria a dieta com parâmetros validados
        return DietaOral(
            textura=dados['textura'],
            numero_refeicoes=num_refeicoes,
            tipo_refeicao=dados['tipo_refeicao'],
            descricao=dados.get('descricao', ''),
            usuario_responsavel=dados.get('usuario_responsavel', 'sistema')
        )

    @staticmethod
    def _criar_dieta_enteral(dados: Dict[str, Any]) -> DietaEnteral:
        """
        Cria uma instância de DietaEnteral com validação de parâmetros.
        
        Args:
            dados: Dicionário com parâmetros da dieta enteral
        
        Returns:
            DietaEnteral: Instância criada e validada
        
        Raises:
            ValueError: Se parâmetros obrigatórios estiverem faltando ou inválidos
        """
        # Lista de parâmetros obrigatórios
        params_obrigatorios = [
            'setor_clinico',
            'via_infusao',
            'velocidade_ml_h',
            'quantidade_gramas_por_porção'
        ]
        
        # Valida presença de parâmetros obrigatórios
        faltando = [p for p in params_obrigatorios if p not in dados]
        if faltando:
            raise ValueError(
                f"Dieta Enteral exige os seguintes parâmetros: {', '.join(faltando)}"
            )
        
        # Validação e conversão de tipos numéricos
        try:
            velocidade = float(dados['velocidade_ml_h'])
            if velocidade <= 0:
                raise ValueError("velocidade_ml_h deve ser maior que 0")
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Parâmetro 'velocidade_ml_h' inválido. "
                f"Esperado número positivo, recebido: {dados.get('velocidade_ml_h')}"
            ) from e
        
        try:
            gramas = float(dados['quantidade_gramas_por_porção'])
            if gramas <= 0:
                raise ValueError("quantidade_gramas_por_porção deve ser maior que 0")
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Parâmetro 'quantidade_gramas_por_porção' inválido. "
                f"Esperado número positivo, recebido: {dados.get('quantidade_gramas_por_porção')}"
            ) from e
        
        try:
            porcoes = int(dados.get('porcoes_diarias', 1))
            if porcoes < 1:
                raise ValueError("porcoes_diarias deve ser >= 1")
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Parâmetro 'porcoes_diarias' inválido. "
                f"Esperado número inteiro >= 1, recebido: {dados.get('porcoes_diarias')}"
            ) from e

        # Cria a dieta com parâmetros validados
        return DietaEnteral(
            setor_clinico=dados['setor_clinico'],
            via_infusao=dados['via_infusao'],
            velocidade_ml_h=velocidade,
            quantidade_gramas_por_porção=gramas,
            porcoes_diarias=porcoes,
            tipo_equipo=dados.get('tipo_equipo', 'bomba'),
            usuario_responsavel=dados.get('usuario_responsavel', 'sistema')
        )