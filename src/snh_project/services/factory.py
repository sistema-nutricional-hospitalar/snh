from typing import Any
try:
    from diet import DietaOral, DietaEnteral
    from base import Dieta
except ImportError:
    from .diet import DietaOral, DietaEnteral
    from .base import Dieta

class DietaFactory:
    """
    Implementação do Padrão Factory Method.
    
    Responsabilidade: Centralizar a criação de objetos da hierarquia 'Dieta'.
    Isso desacopla o código cliente (Prescrição) das classes concretas (Oral/Enteral).
    """

    @staticmethod
    def criar_dieta(tipo: str, usuario_responsavel: str, **kwargs: Any) -> Dieta:
        """
        Fabrica uma instância de Dieta baseada no tipo solicitado.

        Args:
            tipo (str): O tipo de dieta ('oral' ou 'enteral').
            usuario_responsavel (str): Nome do responsável (para a auditoria).
            **kwargs: Argumentos dinâmicos dependendo do tipo:
                      - Oral: exige 'protocolo'.
                      - Enteral: exige 'protocolo', 'volume' e 'densidade'.

        Returns:
            Dieta: Uma instância validada de DietaOral ou DietaEnteral.

        Raises:
            ValueError: Se o tipo for desconhecido ou faltarem parâmetros.
        """
        # Normaliza a string para evitar erros de digitação (ex: "Oral ", "ORAL")
        tipo_normalizado = tipo.lower().strip()

        if tipo_normalizado == 'oral':
            # Validação: Dieta Oral precisa de um protocolo definido
            if 'protocolo' not in kwargs:
                raise ValueError("Erro: Criação de Dieta Oral exige o parâmetro 'protocolo'.")
            
            # Instancia usando a classe do David
            return DietaOral(
                nome_protocolo=kwargs['protocolo'],
                usuario_responsavel=usuario_responsavel
            )

        elif tipo_normalizado == 'enteral':
            # Validação: Dieta Enteral precisa de dados matemáticos para o cálculo
            parametros_obrigatorios = ['protocolo', 'volume', 'densidade']
            
            # Verifica se todos os parâmetros estão presentes
            if not all(param in kwargs for param in parametros_obrigatorios):
                raise ValueError(f"Erro: Dieta Enteral exige {parametros_obrigatorios}")

            # Instancia a classe do David
            # Note que mapeamos 'densidade' para 'kcal_por_ml' conforme a definição dele
            return DietaEnteral(
                nome_protocolo=kwargs['protocolo'],
                volume_ml=float(kwargs['volume']),
                kcal_por_ml=float(kwargs['densidade']),
                usuario_responsavel=usuario_responsavel
            )

        else:
            # Proteção contra tipos inexistentes
            raise ValueError(f"Tipo de dieta não suportado pela Factory: '{tipo}'")