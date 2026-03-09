"""
Configuração global do pytest.

Adiciona o diretório src ao sys.path para que todos os testes
possam importar os módulos sem prefixo 'src.'.
"""
import sys
import os

# Garante que src/ está no path — sem isso, pytest não encontra snh_project
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
