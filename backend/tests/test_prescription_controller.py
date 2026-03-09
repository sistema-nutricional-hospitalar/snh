"""
Testes para PrescriptionController.

Cobertura: prescrição, alteração com acúmulo de histórico (RN02),
           notificação automática (RN03) com mock, encerramento,
           listagem e histórico cronológico.

Inclui 2 testes com MagicMock para o NotificadorService (requisito 8.1).
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from src.snh_project.controllers.patient_controller import PatientController
from src.snh_project.controllers.prescription_controller import PrescriptionController
from src.snh_project.services.notifier import NotificadorService


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def ctrl_pair(tmp_path):
    """Par de controllers isolados usando diretório temporário."""
    data_dir = str(tmp_path)
    patient_ctrl = PatientController(data_dir=data_dir)
    presc_ctrl = PrescriptionController(data_dir=data_dir)
    return patient_ctrl, presc_ctrl


@pytest.fixture
def paciente_id(ctrl_pair):
    """Paciente criado para uso nos testes de prescrição."""
    patient_ctrl, _ = ctrl_pair
    p = patient_ctrl.cadastrar({
        "nome": "Carlos Teste",
        "data_nasc": "1970-08-20",
        "setor_nome": "Clínica Geral",
        "leito": 7,
        "data_internacao": "2024-05-10T10:00:00",
    })
    return p["id"]


@pytest.fixture
def dados_oral():
    return {
        "textura": "normal",
        "numero_refeicoes": 3,
        "tipo_refeicao": "almoco",
        "descricao": "Dieta padrão",
    }


@pytest.fixture
def prescricao_criada(ctrl_pair, paciente_id, dados_oral):
    """Prescrição já criada para testes que precisam de um ID existente."""
    _, presc_ctrl = ctrl_pair
    return presc_ctrl.prescrever(paciente_id, "oral", dados_oral, "Dra. Ana")


# =============================================================================
# PRESCRIÇÃO — US04
# =============================================================================

class TestPrescrever:

    def test_prescrever_oral_retorna_resumo(self, ctrl_pair, paciente_id, dados_oral):
        """Prescrição oral válida deve retornar dicionário com campos esperados."""
        _, presc_ctrl = ctrl_pair
        resultado = presc_ctrl.prescrever(paciente_id, "oral", dados_oral, "Dra. Ana")
        assert "id" in resultado
        assert resultado["dieta_tipo"] == "DietaOral"
        assert resultado["ativa"] is True
        assert resultado["patient_id"] == paciente_id

    def test_prescrever_cria_historico_inicial(self, ctrl_pair, paciente_id, dados_oral):
        """Prescrição nova deve ter 1 entrada no histórico (criação)."""
        _, presc_ctrl = ctrl_pair
        presc = presc_ctrl.prescrever(paciente_id, "oral", dados_oral, "Dra. Ana")
        historico = presc_ctrl.obter_historico(presc["id"])
        assert len(historico) == 1
        assert historico[0]["tipo_alteracao"] == "Criação de prescrição"

    def test_prescrever_paciente_inexistente_levanta_erro(self, ctrl_pair):
        """Prescrever para paciente inexistente deve levantar ValueError."""
        _, presc_ctrl = ctrl_pair
        with pytest.raises(ValueError, match="não encontrado"):
            presc_ctrl.prescrever("id-fantasma", "oral", {
                "textura": "normal", "numero_refeicoes": 3, "tipo_refeicao": "almoco"
            })

    def test_prescrever_tipo_dieta_invalido_levanta_erro(self, ctrl_pair, paciente_id):
        """Tipo de dieta inválido deve levantar erro da DietaFactory."""
        _, presc_ctrl = ctrl_pair
        with pytest.raises(ValueError):
            presc_ctrl.prescrever(paciente_id, "tipo_invalido", {})


# =============================================================================
# ALTERAÇÃO — US05 / RN02
# =============================================================================

class TestAlterar:

    def test_alterar_dieta_retorna_resumo_atualizado(
        self, ctrl_pair, prescricao_criada
    ):
        """alterar_dieta deve retornar o resumo com tipo de dieta atualizado."""
        _, presc_ctrl = ctrl_pair
        resultado = presc_ctrl.alterar_dieta(
            prescricao_criada["id"], "oral",
            {"textura": "pastosa", "numero_refeicoes": 5, "tipo_refeicao": "desjejum"},
            "Dra. Ana",
        )
        assert resultado["ativa"] is True

    def test_alterar_acumula_historico_rn02(self, ctrl_pair, prescricao_criada):
        """RN02: cada alteração deve acrescentar entrada no histórico (não sobrescrever)."""
        _, presc_ctrl = ctrl_pair
        pid = prescricao_criada["id"]

        presc_ctrl.alterar_dieta(pid, "oral",
            {"textura": "mole", "numero_refeicoes": 4, "tipo_refeicao": "almoco"}, "Dra. Ana")
        presc_ctrl.alterar_dieta(pid, "oral",
            {"textura": "pastosa", "numero_refeicoes": 5, "tipo_refeicao": "desjejum"}, "Dra. Ana")

        historico = presc_ctrl.obter_historico(pid)
        # criação (1) + alteração (1) + alteração (1) = 3
        assert len(historico) == 3

    def test_historico_ordenado_cronologicamente(self, ctrl_pair, prescricao_criada):
        """RN02: histórico deve vir ordenado do mais antigo para o mais recente."""
        _, presc_ctrl = ctrl_pair
        pid = prescricao_criada["id"]

        presc_ctrl.alterar_dieta(pid, "oral",
            {"textura": "mole", "numero_refeicoes": 4, "tipo_refeicao": "almoco"}, "Dra. Ana")

        historico = presc_ctrl.obter_historico(pid)
        datas = [h["data_hora"] for h in historico]
        assert datas == sorted(datas)

    def test_alterar_prescricao_inexistente_levanta_erro(self, ctrl_pair):
        """alterar_dieta em prescrição que não existe deve levantar ValueError."""
        _, presc_ctrl = ctrl_pair
        with pytest.raises(ValueError, match="não encontrada"):
            presc_ctrl.alterar_dieta("id-fantasma", "oral",
                {"textura": "normal", "numero_refeicoes": 3, "tipo_refeicao": "almoco"})

    def test_alterar_prescricao_encerrada_levanta_erro(
        self, ctrl_pair, prescricao_criada
    ):
        """Não deve ser possível alterar dieta de prescrição encerrada."""
        _, presc_ctrl = ctrl_pair
        pid = prescricao_criada["id"]
        presc_ctrl.encerrar(pid, "Dra. Ana")
        with pytest.raises(ValueError, match="encerrada"):
            presc_ctrl.alterar_dieta(pid, "oral",
                {"textura": "normal", "numero_refeicoes": 3, "tipo_refeicao": "almoco"})


# =============================================================================
# MOCK — RN03: notificação automática ao alterar dieta
# =============================================================================

class TestNotificacaoComMock:

    def test_notificador_chamado_ao_alterar_dieta(self, tmp_path):
        """
        RN03: alterar_dieta deve disparar notificação automaticamente.
        Usa MagicMock para verificar que notificar_mudanca foi chamado
        sem depender de arquivos ou estratégias reais.
        """
        data_dir = str(tmp_path)
        patient_ctrl = PatientController(data_dir=data_dir)
        p = patient_ctrl.cadastrar({
            "nome": "Paciente Mock", "data_nasc": "1990-01-01",
            "setor_nome": "UTI", "leito": 1,
            "data_internacao": "2024-01-01T00:00:00",
        })

        # Cria mock do NotificadorService
        mock_notificador = MagicMock(spec=NotificadorService)
        mock_notificador.notificar_mudanca.return_value = {
            "total_enviados": 1, "sucessos": 1, "falhas": 0
        }

        presc_ctrl = PrescriptionController(
            data_dir=data_dir, notificador=mock_notificador
        )
        presc = presc_ctrl.prescrever(
            p["id"], "oral",
            {"textura": "normal", "numero_refeicoes": 3, "tipo_refeicao": "almoco"},
            "Dra. Ana",
        )

        # Altera a dieta — deve disparar notificação
        presc_ctrl.alterar_dieta(
            presc["id"], "oral",
            {"textura": "pastosa", "numero_refeicoes": 5, "tipo_refeicao": "desjejum"},
            "Dra. Ana",
        )

        # Verifica que notificar_mudanca foi chamado pelo menos 1 vez
        mock_notificador.notificar_mudanca.assert_called()

    def test_notificador_chamado_ao_encerrar_prescricao(self, tmp_path):
        """
        RN03: encerrar() também deve disparar notificação.
        Verifica o call count do mock após encerramento.
        """
        data_dir = str(tmp_path)
        patient_ctrl = PatientController(data_dir=data_dir)
        p = patient_ctrl.cadastrar({
            "nome": "Paciente Encerrar", "data_nasc": "1988-07-10",
            "setor_nome": "Enfermaria", "leito": 2,
            "data_internacao": "2024-02-01T00:00:00",
        })

        mock_notificador = MagicMock(spec=NotificadorService)
        mock_notificador.notificar_mudanca.return_value = {
            "total_enviados": 1, "sucessos": 1, "falhas": 0
        }

        presc_ctrl = PrescriptionController(
            data_dir=data_dir, notificador=mock_notificador
        )
        presc = presc_ctrl.prescrever(
            p["id"], "oral",
            {"textura": "normal", "numero_refeicoes": 3, "tipo_refeicao": "almoco"},
            "Dra. Ana",
        )

        calls_antes = mock_notificador.notificar_mudanca.call_count

        presc_ctrl.encerrar(presc["id"], "Dra. Ana")

        # Deve ter sido chamado mais vezes após encerrar
        assert mock_notificador.notificar_mudanca.call_count > calls_antes


# =============================================================================
# ENCERRAMENTO
# =============================================================================

class TestEncerrar:

    def test_encerrar_prescricao_ativa(self, ctrl_pair, prescricao_criada):
        """encerrar() deve retornar sucesso e desativar a prescrição."""
        _, presc_ctrl = ctrl_pair
        resultado = presc_ctrl.encerrar(prescricao_criada["id"], "Dra. Ana")
        assert resultado["sucesso"] is True
        registro = presc_ctrl.obter_por_id(prescricao_criada["id"])
        assert registro["ativa"] is False

    def test_encerrar_prescricao_inexistente(self, ctrl_pair):
        """encerrar() com ID inválido deve retornar motivo nao_encontrado."""
        _, presc_ctrl = ctrl_pair
        resultado = presc_ctrl.encerrar("id-fantasma")
        assert resultado["sucesso"] is False
        assert resultado["motivo"] == "nao_encontrado"

    def test_encerrar_prescricao_ja_encerrada(self, ctrl_pair, prescricao_criada):
        """encerrar() uma prescrição já encerrada deve retornar motivo ja_encerrada."""
        _, presc_ctrl = ctrl_pair
        pid = prescricao_criada["id"]
        presc_ctrl.encerrar(pid)
        resultado = presc_ctrl.encerrar(pid)
        assert resultado["motivo"] == "ja_encerrada"


# =============================================================================
# LISTAGEM
# =============================================================================

class TestListagem:

    def test_listar_por_paciente_retorna_prescricoes(
        self, ctrl_pair, paciente_id, dados_oral
    ):
        """listar_por_paciente deve retornar todas as prescrições do paciente."""
        _, presc_ctrl = ctrl_pair
        presc_ctrl.prescrever(paciente_id, "oral", dados_oral, "Dra. Ana")
        presc_ctrl.prescrever(paciente_id, "oral",
            {**dados_oral, "textura": "mole"}, "Dra. Ana")
        lista = presc_ctrl.listar_por_paciente(paciente_id)
        assert len(lista) == 2

    def test_listar_dietas_orais_ativas_filtra_tipo(
        self, ctrl_pair, paciente_id, dados_oral
    ):
        """listar_dietas_orais_ativas deve retornar apenas prescrições orais ativas."""
        _, presc_ctrl = ctrl_pair
        presc = presc_ctrl.prescrever(paciente_id, "oral", dados_oral, "Dra. Ana")
        orais = presc_ctrl.listar_dietas_orais_ativas()
        assert any(r["id"] == presc["id"] for r in orais)
