from abc import ABC, abstractmethod
from typing import Dict, Any

class EstrategiaRelatorio(ABC):
    """
    Interface para estratégias de geração de relatório ou processamento.
    Define o contrato que todas as estratégias devem seguir.
    """
    
    @abstractmethod
    def processar_dados(self, dados: Dict[str, Any]) -> str:
        """
        Processa os dados brutos extraídos do método .calcular_nutrientes()
        da classe de Dieta e retorna uma string formatada.
        """
        pass

class RelatorioDietaOralStrategy(EstrategiaRelatorio):
    """
    Estratégia especializada para relatórios de Dieta Oral.
    Adaptada para a nova estrutura de dicionário aninhado do diet.py.
    """
    def processar_dados(self, dados: Dict[str, Any]) -> str:
        # Validação de segurança para garantir que é o tipo certo
        if dados.get("tipo_dieta") != "Oral":
            return "Erro: Dados fornecidos não correspondem a uma Dieta Oral."

        # Acesso seguro aos dicionários aninhados criados no novo diet.py
        prescricao = dados.get("prescrito", {})
        restricoes = dados.get("restricoes", {}).get("proibidas", [])
        
        qtd_itens = dados.get("quantidade_itens", 0)
        
        # Formatação do relatório
        relatorio = [
            "=== RELATÓRIO DE DIETA ORAL ===",
            f"Textura: {dados.get('textura', 'Não informada').upper()}",
            f"Refeição Principal: {prescricao.get('tipo_refeicao', 'N/A').title()}",
            f"Frequência: {prescricao.get('numero_refeicoes', 0)} vezes ao dia",
            f"Restrições Alimentares: {', '.join(restricoes) if restricoes else 'Nenhuma'}",
            f"Itens no Cardápio: {qtd_itens}",
            "==============================="
        ]
        
        return "\n".join(relatorio)


class RelatorioDietaEnteralStrategy(EstrategiaRelatorio):
    """
    Estratégia especializada para relatórios de Dieta Enteral.
    Adaptada para usar gramagem e vazão em vez de calorias/volume total.
    """
    def processar_dados(self, dados: Dict[str, Any]) -> str:
        if dados.get("tipo_dieta") != "Enteral":
            return "Erro: Dados fornecidos não correspondem a uma Dieta Enteral."

        # Lógica para determinar o tipo de uso do equipo baseada nas flags booleanas
        # retornadas pelo novo diet.py
        uso_equipo = "Troca a cada frasco"
        if dados.get("equipo_unico_por_dia"):
            uso_equipo = "Troca a cada 24h (Único)"

        # Cálculos de projeção (já que diet.py removeu percentuais)
        velocidade = dados.get("velocidade_ml_h", 0)
        volume_estimado_24h = velocidade * 24

        relatorio = [
            "=== RELATÓRIO DE DIETA ENTERAL ===",
            f"Via de Infusão: {dados.get('via_infusao', 'N/A').upper()}",
            f"Velocidade de Fluxo: {velocidade} ml/h",
            f"Volume Estimado (24h): {volume_estimado_24h:.1f} ml",
            "--- Prescrição Nutricional ---",
            f"Porções Diárias: {dados.get('porcoes_diarias', 0)}",
            f"Gramas por Porção: {dados.get('quantidade_gramas_por_porção', 0)}g",
            f"Total de Fórmula (pó): {dados.get('total_gramas_diarias', 0)}g / dia",
            "--- Equipamentos ---",
            f"Tipo de Equipo: {dados.get('tipo_equipo', 'N/A').upper()}",
            f"Regime de Troca: {uso_equipo}",
            "=================================="
        ]

        return "\n".join(relatorio)

class ContextoRelatorio:
    """
    Contexto que utiliza uma estratégia para gerar o relatório.
    """
    def __init__(self, estrategia: EstrategiaRelatorio):
        self._estrategia = estrategia

    @property
    def estrategia(self) -> EstrategiaRelatorio:
        return self._estrategia

    @estrategia.setter
    def estrategia(self, estrategia: EstrategiaRelatorio):
        self._estrategia = estrategia

    def gerar(self, dados_dieta: Dict[str, Any]) -> str:
        return self._estrategia.processar_dados(dados_dieta)