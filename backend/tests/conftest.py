"""
Fixtures globais do pytest para o SNH.

Disponíveis automaticamente em todos os arquivos de teste.
"""

import pytest
import os


@pytest.fixture(autouse=False)
def data_dir(tmp_path):
    """Diretório temporário isolado para testes de persistência.

    Cria automaticamente os JSONs vazios necessários.
    """
    for nome in ["patients.json", "prescriptions.json", "users.json",
                 "setores.json", "notifications.json"]:
        (tmp_path / nome).write_text("[]")
    return str(tmp_path)
