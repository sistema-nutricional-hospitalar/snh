from typing import Any, Dict, List

from ..core.base import Dieta
from ..core.diets import DietaEnteral, DietaMista, DietaOral, DietaParenteral


class DietaFactory:
    """
    Implementação do Padrão Factory Method.

    Responsabilidade: Centralizar a criação de objetos da hierarquia 'Dieta'.
    Isso desacopla o código cliente (Prescrição) das classes concretas.

    A Factory valida os dados de entrada e garante que as dietas sejam criadas
    com todos os parâmetros obrigatórios, fornecendo mensagens de erro claras
    quando algo está faltando ou inválido.

    Tipos suportados:
        - 'oral'       → DietaOral
        - 'enteral'    → DietaEnteral
        - 'parenteral' → DietaParenteral
        - 'mista'      → DietaMista (Composite)
    """

    TIPOS_VALIDOS = ('oral', 'enteral', 'parenteral', 'mista')

    @staticmethod
    def criar_dieta(tipo: str, dados: Dict[str, Any]) -> Dieta:
        """
        Fabrica uma instância de Dieta baseada no tipo solicitado.

        Args:
            tipo  : Tipo da dieta ('oral', 'enteral', 'parenteral' ou 'mista').
                    Case-insensitive e ignora espaços extras.
            dados : Dicionário com os parâmetros necessários para cada tipo.

        Returns:
            Dieta: Instância validada do tipo solicitado.

        Raises:
            ValueError: Se o tipo for desconhecido ou dados forem inválidos.
        """
        tipo_normalizado = tipo.strip().lower()

        if tipo_normalizado == 'oral':
            return DietaFactory._criar_dieta_oral(dados)

        elif tipo_normalizado == 'enteral':
            return DietaFactory._criar_dieta_enteral(dados)

        elif tipo_normalizado == 'parenteral':
            return DietaFactory._criar_dieta_parenteral(dados)

        elif tipo_normalizado == 'mista':
            return DietaFactory._criar_dieta_mista(dados)

        else:
            raise ValueError(
                f"Tipo de dieta desconhecido: '{tipo}'. "
                f"Tipos válidos: {', '.join(repr(t) for t in DietaFactory.TIPOS_VALIDOS)}"
            )

    # =========================================================================
    # MÉTODOS PRIVADOS
    # =========================================================================

    @staticmethod
    def _criar_dieta_oral(dados: Dict[str, Any]) -> DietaOral:
        """
        Cria DietaOral.

        Obrigatórios: textura, numero_refeicoes (int > 0), tipo_refeicao.
        Opcionais: descricao, usuario_responsavel.
        """
        params_obrigatorios = ['textura', 'numero_refeicoes', 'tipo_refeicao']

        faltando = [p for p in params_obrigatorios if p not in dados]
        if faltando:
            raise ValueError(
                f"Dieta Oral exige os seguintes parâmetros: {', '.join(faltando)}"
            )

        try:
            num_refeicoes = int(dados['numero_refeicoes'])
            if num_refeicoes <= 0:
                raise ValueError("numero_refeicoes deve ser maior que 0")
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Parâmetro 'numero_refeicoes' inválido. "
                f"Esperado número inteiro positivo, recebido: {dados.get('numero_refeicoes')}"
            ) from e

        return DietaOral(
            textura=dados['textura'],
            numero_refeicoes=num_refeicoes,
            tipo_refeicao=dados['tipo_refeicao'],
            descricao=dados.get('descricao', ''),
            usuario_responsavel=dados.get('usuario_responsavel', 'sistema'),
        )

    @staticmethod
    def _criar_dieta_enteral(dados: Dict[str, Any]) -> DietaEnteral:
        """
        Cria DietaEnteral.

        Obrigatórios: setor_clinico, via_infusao, velocidade_ml_h (float > 0),
                      quantidade_gramas_por_porção (float > 0).
        Opcionais: porcoes_diarias (default 1), tipo_equipo (default 'bomba'),
                   usuario_responsavel.
        """
        params_obrigatorios = [
            'setor_clinico',
            'via_infusao',
            'velocidade_ml_h',
            'quantidade_gramas_por_porção',
        ]

        faltando = [p for p in params_obrigatorios if p not in dados]
        if faltando:
            raise ValueError(
                f"Dieta Enteral exige os seguintes parâmetros: {', '.join(faltando)}"
            )

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

        return DietaEnteral(
            setor_clinico=dados['setor_clinico'],
            via_infusao=dados['via_infusao'],
            velocidade_ml_h=velocidade,
            quantidade_gramas_por_porção=gramas,
            porcoes_diarias=porcoes,
            tipo_equipo=dados.get('tipo_equipo', 'bomba'),
            usuario_responsavel=dados.get('usuario_responsavel', 'sistema'),
        )

    @staticmethod
    def _criar_dieta_parenteral(dados: Dict[str, Any]) -> DietaParenteral:
        """
        Cria DietaParenteral.

        Obrigatórios: tipo_acesso (str), volume_ml_dia (float > 0),
                      composicao (str), velocidade_ml_h (float > 0).
        Opcionais: descricao, usuario_responsavel.

        Tipos de acesso válidos: 'periférico', 'central', 'cateter central', 'picc'.
        Velocidade deve permitir infundir o volume em 24h (±20% de tolerância).
        """
        params_obrigatorios = [
            'tipo_acesso',
            'volume_ml_dia',
            'composicao',
            'velocidade_ml_h',
        ]

        faltando = [p for p in params_obrigatorios if p not in dados]
        if faltando:
            raise ValueError(
                f"Dieta Parenteral exige os seguintes parâmetros: {', '.join(faltando)}"
            )

        try:
            volume = float(dados['volume_ml_dia'])
            if volume <= 0:
                raise ValueError("volume_ml_dia deve ser maior que 0")
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Parâmetro 'volume_ml_dia' inválido. "
                f"Esperado número positivo, recebido: {dados.get('volume_ml_dia')}"
            ) from e

        try:
            velocidade = float(dados['velocidade_ml_h'])
            if velocidade <= 0:
                raise ValueError("velocidade_ml_h deve ser maior que 0")
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Parâmetro 'velocidade_ml_h' inválido. "
                f"Esperado número positivo, recebido: {dados.get('velocidade_ml_h')}"
            ) from e

        return DietaParenteral(
            tipo_acesso=dados['tipo_acesso'],
            volume_ml_dia=volume,
            composicao=dados['composicao'],
            velocidade_ml_h=velocidade,
            descricao=dados.get('descricao', ''),
            usuario_responsavel=dados.get('usuario_responsavel', 'sistema'),
        )

    @staticmethod
    def _criar_dieta_mista(dados: Dict[str, Any]) -> DietaMista:
        """
        Cria DietaMista (Composite).

        Obrigatórios:
            componentes (List[Dict]): lista de dicionários com:
                - 'dieta'      (Dieta)  : instância já criada de qualquer subclasse
                - 'percentual' (float)  : percentual na composição (0–100)

        Opcionais: descricao (default 'Dieta Mista'), usuario_responsavel.

        Regras (impostas por DietaMista):
            - Mínimo 2 componentes, máximo 4
            - Soma dos percentuais: 100% (±5% de tolerância)
            - Nenhum componente pode ser DietaMista (evita recursão)

        Exemplo::

            dados = {
                'componentes': [
                    {'dieta': dieta_oral,    'percentual': 70.0},
                    {'dieta': dieta_enteral, 'percentual': 30.0},
                ],
                'descricao': 'Desmame enteral',
            }
        """
        if 'componentes' not in dados:
            raise ValueError(
                "Dieta Mista exige o parâmetro 'componentes': "
                "lista de {'dieta': Dieta, 'percentual': float}."
            )

        componentes: List[Dict] = dados['componentes']

        if not isinstance(componentes, list) or len(componentes) == 0:
            raise ValueError(
                "Parâmetro 'componentes' deve ser uma lista não vazia."
            )

        # Valida estrutura de cada item antes de criar o objeto
        for i, item in enumerate(componentes):
            if not isinstance(item, dict):
                raise ValueError(
                    f"Cada componente deve ser um dicionário com 'dieta' e "
                    f"'percentual'. Índice {i} inválido."
                )
            if 'dieta' not in item or 'percentual' not in item:
                raise ValueError(
                    f"Componente no índice {i} deve ter as chaves 'dieta' e 'percentual'."
                )
            if not isinstance(item['dieta'], Dieta):
                raise TypeError(
                    f"Componente no índice {i}: 'dieta' deve ser instância de Dieta, "
                    f"recebido: {type(item['dieta']).__name__}."
                )
            try:
                percentual = float(item['percentual'])
                if percentual <= 0 or percentual > 100:
                    raise ValueError(
                        f"Componente no índice {i}: 'percentual' deve estar entre "
                        f"0 e 100, recebido: {item['percentual']}."
                    )
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Componente no índice {i}: 'percentual' inválido, "
                    f"recebido: {item.get('percentual')}."
                ) from e

        dieta_mista = DietaMista(
            descricao=dados.get('descricao', 'Dieta Mista'),
            usuario_responsavel=dados.get('usuario_responsavel', 'sistema'),
        )

        for item in componentes:
            dieta_mista.adicionar_componente(
                dieta=item['dieta'],
                percentual=float(item['percentual']),
            )

        return dieta_mista