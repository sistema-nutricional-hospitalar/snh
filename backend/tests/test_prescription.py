"""
Testes para HistoricoAlteracao e Prescricao.
Cobertura: criação, alteração de dieta, encerramento,
           histórico, resumo, validações e casos de erro.
"""

import pytest
from datetime import datetime

from src.snh_project.core.prescription import HistoricoAlteracao, Prescricao
from src.snh_project.core.patient import Paciente
from src.snh_project.core.setorclin import SetorClinico
from src.snh_project.core.diets import DietaOral, DietaEnteral
from src.snh_project.services.notifier import NotificadorService
from src.snh_project.services.strategies import NotificacaoEmail

@pytest.fixture
def setor():
    return SetorClinico("Enfermaria")

@pytest.fixture
def paciente(setor):
    return Paciente(
        nome="João da Silva",
        dataNasc="1980-05-10",
        setorClinico=setor,
        leito=1,
        datain=datetime(2025, 1, 1),
        risco=False
    )

@pytest.fixture
def dieta_oral():
    #textura, numero_refeicoes, tipo_refeicao, descricao, usuario_responsavel
    return DietaOral("normal", 3, "almoço", "Dieta padrão", "Dr. Ana")

@pytest.fixture
def dieta_enteral():
    #setor_clinico, via_infusao, velocidade_ml_h, quantidade_gramas_por_porcao, porcoes_diarias, tipo_equipo
    return DietaEnteral("Enfermaria", "nasogástrica", 50.0, 200.0, 4, "bomba")

@pytest.fixture
def notificador():
    n = NotificadorService()
    n.registrar_observador(
        nome_canal="email",
        estrategia=NotificacaoEmail(),
        destinatarios=["enfermaria@hospital.com"]
    )
    return n

@pytest.fixture
def prescricao(paciente, dieta_oral, notificador):
    return Prescricao(
        paciente=paciente,
        dieta=dieta_oral,
        notificador=notificador,
        usuario_responsavel="Dra. Carla"
    )

class TestHistoricoAlteracao:

    def test_criacao_basica(self):
        hist = HistoricoAlteracao(
            tipo_alteracao="Alteração de dieta",
            descricao="Mudou de oral para enteral",
            usuario="Dr. Silva"
        )
        assert hist.tipo_alteracao == "Alteração de dieta"
        assert hist.descricao == "Mudou de oral para enteral"
        assert hist.usuario == "Dr. Silva"

    def test_data_hora_automatica(self):
        antes = datetime.now()
        hist = HistoricoAlteracao("Encerramento", "Prescrição encerrada")
        depois = datetime.now()
        assert antes <= hist.data_hora <= depois

    def test_usuario_default_sistema(self):
        hist = HistoricoAlteracao("Tipo", "Descrição qualquer")
        assert hist.usuario == "sistema"

    def test_usuario_vazio_vira_sistema(self):
        hist = HistoricoAlteracao("Tipo", "Desc", usuario="   ")
        assert hist.usuario == "sistema"

    def test_tipo_vazio_lanca_valueerror(self):
        with pytest.raises(ValueError, match="tipo_alteracao"):
            HistoricoAlteracao(tipo_alteracao="", descricao="Descrição")

    def test_tipo_apenas_espacos_lanca_valueerror(self):
        with pytest.raises(ValueError):
            HistoricoAlteracao(tipo_alteracao="   ", descricao="Descrição")

    def test_descricao_vazia_lanca_valueerror(self):
        with pytest.raises(ValueError, match="descricao"):
            HistoricoAlteracao(tipo_alteracao="Tipo", descricao="")

    def test_imutabilidade_sem_setter(self):
        hist = HistoricoAlteracao("Tipo", "Desc", "usuario")
        with pytest.raises(AttributeError):
            hist.tipo_alteracao = "Novo tipo"

    def test_repr_contem_informacoes(self):
        hist = HistoricoAlteracao("Encerramento", "Desc", "Dr. João")
        r = repr(hist)
        assert "Encerramento" in r
        assert "Dr. João" in r

    def test_strings_sao_strip(self):
        hist = HistoricoAlteracao("  Tipo com espaço  ", "  Desc  ", "  user  ")
        assert hist.tipo_alteracao == "Tipo com espaço"
        assert hist.descricao == "Desc"
        assert hist.usuario == "user"

class TestPrescricaoCriacao:

    def test_criacao_valida(self, prescricao, paciente, dieta_oral):
        assert prescricao.ativa is True
        assert prescricao.paciente == paciente
        assert prescricao.dieta == dieta_oral

    def test_id_unico(self, paciente, dieta_oral, notificador):
        p1 = Prescricao(paciente, dieta_oral, notificador)
        setor2 = SetorClinico("Cardio")
        pac2 = Paciente("Maria", "1990-01-01", setor2, 1, datetime(2025, 1, 1), False)
        dieta2 = DietaOral("mole", 3, "almoço")
        p2 = Prescricao(pac2, dieta2, notificador)
        assert p1.id_prescricao != p2.id_prescricao

    def test_historico_inicial_tem_criacao(self, prescricao):
        historico = prescricao.historico
        assert len(historico) == 1
        assert historico[0].tipo_alteracao == "Criação de prescrição"

    def test_auditoria_usuario_responsavel(self, prescricao):
        assert prescricao.usuario_responsavel == "Dra. Carla"

    def test_tipo_errado_paciente_lanca_typeerror(self, dieta_oral, notificador):
        with pytest.raises(TypeError, match="paciente"):
            Prescricao("não é paciente", dieta_oral, notificador)

    def test_tipo_errado_dieta_lanca_typeerror(self, paciente, notificador):
        with pytest.raises(TypeError, match="dieta"):
            Prescricao(paciente, "não é dieta", notificador)

    def test_tipo_errado_notificador_lanca_typeerror(self, paciente, dieta_oral):
        with pytest.raises(TypeError, match="notificador"):
            Prescricao(paciente, dieta_oral, "não é notificador")

    def test_historico_retorna_copia(self, prescricao):
        copia = prescricao.historico
        copia.clear()
        assert len(prescricao.historico) == 1  # original não foi alterado

class TestPrescricaoAlterarDieta:

    def test_alterar_dieta_atualiza_dieta(self, prescricao, dieta_enteral):
        prescricao.alterar_dieta(dieta_enteral, usuario="Dr. Pedro")
        assert prescricao.dieta == dieta_enteral

    def test_alterar_dieta_adiciona_historico(self, prescricao, dieta_enteral):
        prescricao.alterar_dieta(dieta_enteral, usuario="Dr. Pedro")
        historico = prescricao.historico
        assert len(historico) == 2
        ultimo = historico[-1]
        assert ultimo.tipo_alteracao == "Alteração de dieta"
        assert ultimo.usuario == "Dr. Pedro"

    def test_alterar_dieta_registra_auditoria(self, prescricao, dieta_enteral):
        ts_antes = prescricao.atualizado_em
        prescricao.alterar_dieta(dieta_enteral)
        assert prescricao.atualizado_em >= ts_antes

    def test_alterar_dieta_encerrada_lanca_valueerror(self, prescricao, dieta_enteral):
        prescricao.encerrar()
        with pytest.raises(ValueError, match="encerrada"):
            prescricao.alterar_dieta(dieta_enteral)

    def test_alterar_dieta_tipo_invalido_lanca_typeerror(self, prescricao):
        with pytest.raises(TypeError):
            prescricao.alterar_dieta("isso não é dieta")

    def test_alterar_dieta_multiplas_vezes(self, prescricao, dieta_enteral):
        dieta2 = DietaOral("mole", 5, "janta")
        prescricao.alterar_dieta(dieta_enteral)
        prescricao.alterar_dieta(dieta2)
        assert len(prescricao.historico) == 3  # criação + 2 alterações
        assert prescricao.dieta == dieta2

    def test_descricao_historico_contem_tipos(self, prescricao, dieta_enteral):
        prescricao.alterar_dieta(dieta_enteral, usuario="Nutricionista")
        ultimo = prescricao.historico[-1]
        assert "DietaOral" in ultimo.descricao
        assert "DietaEnteral" in ultimo.descricao


class TestPrescricaoEncerrar:
    #teste do método 'Encerrar'

    def test_encerrar_muda_ativa_para_false(self, prescricao):
        prescricao.encerrar(usuario="Admin")
        assert prescricao.ativa is False

    def test_encerrar_adiciona_historico(self, prescricao):
        prescricao.encerrar(usuario="Admin")
        historico = prescricao.historico
        ultimo = historico[-1]
        assert ultimo.tipo_alteracao == "Encerramento"
        assert ultimo.usuario == "Admin"

    def test_encerrar_ativa_encerrar_dieta(self, prescricao):
        prescricao.encerrar()
        assert prescricao.dieta.ativo is False

    def test_encerrar_duas_vezes_lanca_valueerror(self, prescricao):
        prescricao.encerrar()
        with pytest.raises(ValueError, match="encerrada"):
            prescricao.encerrar()

    def test_encerrar_registra_auditoria(self, prescricao):
        ts = prescricao.atualizado_em
        prescricao.encerrar()
        assert prescricao.atualizado_em >= ts


class TestPrescricaoResumo:
    #Obter resumo

    def test_resumo_contem_chaves_esperadas(self, prescricao):
        resumo = prescricao.obter_resumo()
        for chave in ["id", "paciente", "setor", "dieta_tipo", "ativa",
                      "total_alteracoes", "criado_em", "criado_por"]:
            assert chave in resumo

    def test_resumo_valores_corretos(self, prescricao, paciente):
        resumo = prescricao.obter_resumo()
        assert resumo["paciente"] == "João da Silva"
        assert resumo["setor"] == "Enfermaria"
        assert resumo["dieta_tipo"] == "DietaOral"
        assert resumo["ativa"] is True
        assert resumo["criado_por"] == "Dra. Carla"

    def test_resumo_apos_encerrar(self, prescricao):
        prescricao.encerrar()
        resumo = prescricao.obter_resumo()
        assert resumo["ativa"] is False

    def test_resumo_total_alteracoes_cresce(self, prescricao, dieta_enteral):
        assert prescricao.obter_resumo()["total_alteracoes"] == 1
        prescricao.alterar_dieta(dieta_enteral)
        assert prescricao.obter_resumo()["total_alteracoes"] == 2


class TestIntegracao:

    def test_fluxo_completo(self):
        """
        Fluxo realista completo:
        Criar setor → Criar paciente → Criar dieta →
        Prescrever → Alterar dieta → Encerrar → Verificar histórico
        """
        # 1. Setup
        setor = SetorClinico("Enfermaria Geral")
        paciente = Paciente(
            nome="Maria Aparecida",
            dataNasc="1975-03-20",
            setorClinico=setor,
            leito=5,
            datain=datetime(2025, 6, 1),
            risco=False
        )
        dieta_inicial = DietaOral("mole", 4, "almoço", "Dieta leve")
        dieta_nova = DietaEnteral("Enfermaria Geral", "nasogástrica", 60.0, 300.0, 3, "gravitacional")

        notificador = NotificadorService()
        notificador.registrar_observador(
            "push",
            NotificacaoEmail(),
            ["nutri@hospital.com", "medico@hospital.com"]
        )

        # 2. Cria prescrição
        prescricao = Prescricao(paciente, dieta_inicial, notificador, "Dra. Lima")
        assert prescricao.ativa
        assert len(prescricao.historico) == 1

        # 3. Altera dieta
        prescricao.alterar_dieta(dieta_nova, usuario="Dr. Ramos")
        assert prescricao.dieta == dieta_nova
        assert len(prescricao.historico) == 2

        # 4. Encerra
        prescricao.encerrar(usuario="Dra. Lima")
        assert not prescricao.ativa
        assert not prescricao.dieta.ativo
        assert len(prescricao.historico) == 3

        # 5. Não pode mais alterar
        dieta_extra = DietaOral("liquida", 2, "ceia")
        with pytest.raises(ValueError):
            prescricao.alterar_dieta(dieta_extra)

        # 6. Resumo final correto
        resumo = prescricao.obter_resumo()
        assert resumo["ativa"] is False
        assert resumo["total_alteracoes"] == 3
        assert resumo["paciente"] == "Maria Aparecida"
