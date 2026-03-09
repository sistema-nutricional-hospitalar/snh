"""
Testes para RelatorioController.

Cobertura: relatório de dietas com filtros (RN09), relatório vazio,
           evolução por paciente, relatório de alterações, exportação JSON.
"""

import json
import pytest

from src.snh_project.controllers.patient_controller import PatientController
from src.snh_project.controllers.prescription_controller import PrescriptionController
from src.snh_project.controllers.report_controller import RelatorioController


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def setup(tmp_path):
    """Cria controllers isolados e retorna conjunto de dados para os testes."""
    data_dir = str(tmp_path)
    patient_ctrl = PatientController(data_dir=data_dir)
    presc_ctrl = PrescriptionController(data_dir=data_dir)
    report_ctrl = RelatorioController(data_dir=data_dir)

    # Cria 2 pacientes em setores diferentes
    p1 = patient_ctrl.cadastrar({
        "nome": "Ana Relatorio", "data_nasc": "1980-01-01",
        "setor_nome": "UTI", "leito": 1,
        "data_internacao": "2024-01-10T00:00:00",
    })
    p2 = patient_ctrl.cadastrar({
        "nome": "Bruno Relatorio", "data_nasc": "1990-05-05",
        "setor_nome": "Enfermaria", "leito": 2,
        "data_internacao": "2024-02-01T00:00:00",
    })

    # Cria prescrições
    pr1 = presc_ctrl.prescrever(p1["id"], "oral",
        {"textura": "normal", "numero_refeicoes": 3, "tipo_refeicao": "almoco"}, "Dra. Ana")
    pr2 = presc_ctrl.prescrever(p2["id"], "oral",
        {"textura": "mole", "numero_refeicoes": 4, "tipo_refeicao": "desjejum"}, "Dra. Ana")

    return {
        "report_ctrl": report_ctrl,
        "presc_ctrl": presc_ctrl,
        "p1_id": p1["id"],
        "p2_id": p2["id"],
        "pr1_id": pr1["id"],
        "pr2_id": pr2["id"],
    }


# =============================================================================
# RELATÓRIO DE DIETAS — US13 / RN09
# =============================================================================

class TestRelatorioDietas:

    def test_relatorio_sem_filtros_retorna_todas(self, setup):
        """Relatório sem filtros deve incluir todas as prescrições."""
        ctrl = setup["report_ctrl"]
        resultado = ctrl.gerar_relatorio_dietas()
        assert resultado["total"] == 2

    def test_relatorio_filtro_setor(self, setup):
        """RN09: filtro por setor deve retornar apenas prescrições daquele setor."""
        ctrl = setup["report_ctrl"]
        resultado = ctrl.gerar_relatorio_dietas(setor_nome="UTI")
        assert resultado["total"] == 1
        assert resultado["prescricoes"][0]["setor_nome"] == "UTI"

    def test_relatorio_filtro_tipo_dieta(self, setup):
        """RN09: filtro por tipo_dieta deve retornar apenas o tipo solicitado."""
        ctrl = setup["report_ctrl"]
        resultado = ctrl.gerar_relatorio_dietas(tipo_dieta="oral")
        assert resultado["total"] == 2
        assert all(p["tipo_dieta"] == "oral" for p in resultado["prescricoes"])

    def test_relatorio_apenas_ativas(self, setup):
        """Filtro apenas_ativas deve excluir prescrições encerradas."""
        ctrl = setup["report_ctrl"]
        presc_ctrl = setup["presc_ctrl"]

        # Encerra uma das prescrições
        presc_ctrl.encerrar(setup["pr1_id"], "Dra. Ana")

        resultado = ctrl.gerar_relatorio_dietas(apenas_ativas=True)
        assert resultado["total"] == 1

    def test_relatorio_vazio_retorna_mensagem(self, tmp_path):
        """Relatório sem dados deve retornar total=0 e mensagem explicativa."""
        ctrl = RelatorioController(data_dir=str(tmp_path))
        resultado = ctrl.gerar_relatorio_dietas()
        assert resultado["total"] == 0
        assert "mensagem" in resultado or resultado["prescricoes"] == []

    def test_relatorio_inclui_resumo_por_tipo(self, setup):
        """Relatório deve incluir contagem agrupada por tipo de dieta."""
        ctrl = setup["report_ctrl"]
        resultado = ctrl.gerar_relatorio_dietas()
        assert "resumo_por_tipo" in resultado
        assert isinstance(resultado["resumo_por_tipo"], dict)

    def test_relatorio_inclui_timestamp_geracao(self, setup):
        """Relatório deve incluir campo 'gerado_em' com timestamp."""
        ctrl = setup["report_ctrl"]
        resultado = ctrl.gerar_relatorio_dietas()
        assert "gerado_em" in resultado
        assert len(resultado["gerado_em"]) > 0

    def test_relatorio_registra_filtros_aplicados(self, setup):
        """Relatório deve incluir os filtros usados na geração."""
        ctrl = setup["report_ctrl"]
        resultado = ctrl.gerar_relatorio_dietas(setor_nome="UTI", tipo_dieta="oral")
        assert resultado["filtros"]["setor_nome"] == "UTI"
        assert resultado["filtros"]["tipo_dieta"] == "oral"


# =============================================================================
# EVOLUÇÃO POR PACIENTE — US14
# =============================================================================

class TestEvolucaoPaciente:

    def test_evolucao_retorna_prescricoes_do_paciente(self, setup):
        """Relatório de evolução deve incluir prescrições do paciente."""
        ctrl = setup["report_ctrl"]
        resultado = ctrl.gerar_relatorio_evolucao_paciente(setup["p1_id"])
        assert resultado["sucesso"] is True
        assert resultado["total_prescricoes"] >= 1

    def test_evolucao_inclui_dados_do_paciente(self, setup):
        """Relatório de evolução deve incluir nome e setor do paciente."""
        ctrl = setup["report_ctrl"]
        resultado = ctrl.gerar_relatorio_evolucao_paciente(setup["p1_id"])
        assert "paciente" in resultado
        assert resultado["paciente"]["nome"] == "Ana Relatorio"

    def test_evolucao_paciente_inexistente(self, tmp_path):
        """Evolução de paciente inexistente deve retornar sucesso=False."""
        ctrl = RelatorioController(data_dir=str(tmp_path))
        resultado = ctrl.gerar_relatorio_evolucao_paciente("id-fantasma")
        assert resultado["sucesso"] is False


# =============================================================================
# RELATÓRIO DE ALTERAÇÕES — US13 / RNF06
# =============================================================================

class TestRelatorioAlteracoes:

    def test_alteracoes_registra_mudancas_de_dieta(self, setup):
        """Após alterar dieta, relatório de alterações deve registrar a mudança."""
        presc_ctrl = setup["presc_ctrl"]
        ctrl = setup["report_ctrl"]

        presc_ctrl.alterar_dieta(
            setup["pr1_id"], "oral",
            {"textura": "pastosa", "numero_refeicoes": 5, "tipo_refeicao": "desjejum"},
            "Dra. Ana",
        )

        resultado = ctrl.gerar_relatorio_alteracoes()
        assert resultado["total_alteracoes"] >= 1

    def test_alteracoes_inclui_usuario_responsavel(self, setup):
        """Cada alteração deve registrar o responsável pela mudança (RNF06)."""
        presc_ctrl = setup["presc_ctrl"]
        ctrl = setup["report_ctrl"]

        presc_ctrl.alterar_dieta(
            setup["pr2_id"], "oral",
            {"textura": "liquida", "numero_refeicoes": 6, "tipo_refeicao": "ceia"},
            "Dr. Responsavel",
        )

        resultado = ctrl.gerar_relatorio_alteracoes()
        usuarios = [a["usuario"] for a in resultado["alteracoes"]]
        assert "Dr. Responsavel" in usuarios


# =============================================================================
# EXPORTAÇÃO JSON — US14
# =============================================================================

class TestExportacao:

    def test_exportar_json_retorna_string_valida(self, setup):
        """exportar_json deve retornar string JSON parseável."""
        ctrl = setup["report_ctrl"]
        relatorio = ctrl.gerar_relatorio_dietas()
        json_str = ctrl.exportar_json(relatorio)
        parsed = json.loads(json_str)
        assert parsed["total"] == relatorio["total"]

    def test_exportar_json_usa_indentacao(self, setup):
        """JSON exportado deve ter indentação (legibilidade)."""
        ctrl = setup["report_ctrl"]
        relatorio = ctrl.gerar_relatorio_dietas()
        json_str = ctrl.exportar_json(relatorio)
        assert "\n" in json_str
