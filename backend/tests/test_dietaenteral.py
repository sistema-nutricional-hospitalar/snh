import pytest
from src.snh_project.core.diets import DietaEnteral
from src.snh_project.core.patient import SetorClinico

@pytest.fixture
def setor_uti():
    return SetorClinico("UTI")


@pytest.fixture
def setor_enfermaria():
    return SetorClinico("Enfermaria")


@pytest.fixture
def dieta_enteral_basica(setor_uti):
    return DietaEnteral(
        setor_clinico=setor_uti,
        via_infusao="nasogástrica",
        velocidade_ml_h=50.0,
        quantidade_gramas_por_porção=200.0
    )


@pytest.fixture
def dieta_enteral_completa(setor_enfermaria):
    return DietaEnteral(
        setor_clinico=setor_enfermaria,
        via_infusao="gastrostomia",
        velocidade_ml_h=75.0,
        quantidade_gramas_por_porção=250.0,
        porcoes_diarias=4,
        tipo_equipo="gravitacional",
        usuario_responsavel="Enf. Ana"
    )


def test_criar_dieta_enteral_parametros_minimos(setor_uti):
    dieta = DietaEnteral(
        setor_clinico=setor_uti,
        via_infusao="nasogástrica",
        velocidade_ml_h=60.0,
        quantidade_gramas_por_porção=180.0
    )
    
    assert dieta.via_infusao == "nasogástrica"
    assert dieta.velocidade_ml_h == 60.0
    assert dieta._quantidade_gramas_por_porção == 180.0
    assert dieta.porcoes_diarias == 1  


def test_criar_dieta_enteral_parametros_completos(dieta_enteral_completa):
    assert dieta_enteral_completa.via_infusao == "gastrostomia"
    assert dieta_enteral_completa.velocidade_ml_h == 75.0
    assert dieta_enteral_completa._quantidade_gramas_por_porção == 250.0
    assert dieta_enteral_completa.porcoes_diarias == 4
    assert dieta_enteral_completa.tipo_equipo == "gravitacional"
    assert dieta_enteral_completa.usuario_responsavel == "Enf. Ana"


def test_via_infusao_normalizada_para_lowercase(setor_uti):
    dieta = DietaEnteral(
        setor_clinico=setor_uti,
        via_infusao="NASOGÁSTRICA",
        velocidade_ml_h=50.0,
        quantidade_gramas_por_porção=200.0
    )
    
    assert dieta.via_infusao == "nasogástrica" 


def test_tipo_equipo_default_eh_bomba(setor_uti):
    dieta = DietaEnteral(
        setor_clinico=setor_uti,
        via_infusao="sng",
        velocidade_ml_h=50.0,
        quantidade_gramas_por_porção=200.0
    )
    
    assert dieta.tipo_equipo == "bomba"


def test_porcoes_diarias_default_eh_1(setor_uti):
    dieta = DietaEnteral(
        setor_clinico=setor_uti,
        via_infusao="sng",
        velocidade_ml_h=50.0,
        quantidade_gramas_por_porção=200.0
    )
    
    assert dieta.porcoes_diarias == 1


def test_dieta_inicia_ativa(dieta_enteral_basica):
    assert dieta_enteral_basica.ativo == True
    assert dieta_enteral_basica.data_fim is None


def test_erro_via_infusao_invalida(setor_uti):
    with pytest.raises(ValueError, match="Via.*inválida"):
        DietaEnteral(
            setor_clinico=setor_uti,
            via_infusao="via_espacial", 
            velocidade_ml_h=50.0,
            quantidade_gramas_por_porção=200.0
        )


def test_erro_velocidade_zero(setor_uti):
    with pytest.raises(ValueError, match="Velocidade de infusão deve ser maior que 0"):
        DietaEnteral(
            setor_clinico=setor_uti,
            via_infusao="sng",
            velocidade_ml_h=0.0,
            quantidade_gramas_por_porção=200.0
        )


def test_erro_velocidade_negativa(setor_uti):
    with pytest.raises(ValueError, match="Velocidade de infusão deve ser maior que 0"):
        DietaEnteral(
            setor_clinico=setor_uti,
            via_infusao="sng",
            velocidade_ml_h=-10.0,
            quantidade_gramas_por_porção=200.0
        )


def test_erro_quantidade_gramas_zero(setor_uti):
    with pytest.raises(ValueError, match="quantidade_gramas_por_porção deve ser maior que 0"):
        DietaEnteral(
            setor_clinico=setor_uti,
            via_infusao="sng",
            velocidade_ml_h=50.0,
            quantidade_gramas_por_porção=0.0
        )


def test_erro_quantidade_gramas_negativa(setor_uti):
    with pytest.raises(ValueError, match="quantidade_gramas_por_porção deve ser maior que 0"):
        DietaEnteral(
            setor_clinico=setor_uti,
            via_infusao="sng",
            velocidade_ml_h=50.0,
            quantidade_gramas_por_porção=-100.0
        )


def test_erro_tipo_equipo_invalido(setor_uti):
    with pytest.raises(ValueError, match="tipo_equipo inválido"):
        DietaEnteral(
            setor_clinico=setor_uti,
            via_infusao="sng",
            velocidade_ml_h=50.0,
            quantidade_gramas_por_porção=200.0,
            tipo_equipo="laser" 
        )


def test_erro_porcoes_diarias_zero(setor_uti):
    with pytest.raises(ValueError, match="porcoes_diarias deve ser inteiro maior ou igual a 1"):
        DietaEnteral(
            setor_clinico=setor_uti,
            via_infusao="sng",
            velocidade_ml_h=50.0,
            quantidade_gramas_por_porção=200.0,
            porcoes_diarias=0
        )


def test_erro_porcoes_diarias_negativo(setor_uti):
    with pytest.raises(ValueError, match="porcoes_diarias deve ser inteiro maior ou igual a 1"):
        DietaEnteral(
            setor_clinico=setor_uti,
            via_infusao="sng",
            velocidade_ml_h=50.0,
            quantidade_gramas_por_porção=200.0,
            porcoes_diarias=-3
        )



def test_via_nasogastrica_valida(setor_uti):
    dieta = DietaEnteral(
        setor_clinico=setor_uti,
        via_infusao="nasogástrica",
        velocidade_ml_h=50.0,
        quantidade_gramas_por_porção=200.0
    )
    assert dieta.via_infusao == "nasogástrica"


def test_via_gastrostomia_valida(setor_uti):
    dieta = DietaEnteral(
        setor_clinico=setor_uti,
        via_infusao="gastrostomia",
        velocidade_ml_h=50.0,
        quantidade_gramas_por_porção=200.0
    )
    assert dieta.via_infusao == "gastrostomia"


def test_via_jejunostomia_valida(setor_uti):
    dieta = DietaEnteral(
        setor_clinico=setor_uti,
        via_infusao="jejunostomia",
        velocidade_ml_h=50.0,
        quantidade_gramas_por_porção=200.0
    )
    assert dieta.via_infusao == "jejunostomia"



def test_alterar_via_infusao_valida(dieta_enteral_basica):
    dieta_enteral_basica.via_infusao = "gastrostomia"
    
    assert dieta_enteral_basica.via_infusao == "gastrostomia"


def test_erro_alterar_via_infusao_invalida(dieta_enteral_basica):
    with pytest.raises(ValueError, match="Via.*inválida"):
        dieta_enteral_basica.via_infusao = "via_impossivel"


def test_alterar_velocidade_valida(dieta_enteral_basica):
    dieta_enteral_basica.velocidade_ml_h = 100.0
    
    assert dieta_enteral_basica.velocidade_ml_h == 100.0


def test_erro_alterar_velocidade_zero(dieta_enteral_basica):
    with pytest.raises(ValueError, match="Velocidade deve ser maior que 0"):
        dieta_enteral_basica.velocidade_ml_h = 0.0


def test_alterar_tipo_equipo_valido(dieta_enteral_basica):
    assert dieta_enteral_basica.tipo_equipo == "bomba"  #
    
    dieta_enteral_basica.tipo_equipo = "gravitacional"
    
    assert dieta_enteral_basica.tipo_equipo == "gravitacional"


def test_erro_alterar_tipo_equipo_invalido(dieta_enteral_basica):
    with pytest.raises(ValueError, match="tipo_equipo inválido"):
        dieta_enteral_basica.tipo_equipo = "manual"


def test_alterar_porcoes_diarias_valido(dieta_enteral_basica):
    dieta_enteral_basica.porcoes_diarias = 5
    
    assert dieta_enteral_basica.porcoes_diarias == 5


def test_erro_alterar_porcoes_diarias_zero(dieta_enteral_basica):
    with pytest.raises(ValueError, match="porcoes_diarias deve ser inteiro maior ou igual a 1"):
        dieta_enteral_basica.porcoes_diarias = 0


def test_volume_infundido_24h(dieta_enteral_basica):
    """Testa cálculo de volume infundido em 24 horas."""
    # velocidade = 50 ml/h
    # 50 ml/h * 24h = 1200 ml
    assert dieta_enteral_basica.volume_infundido_24h == 1200.0


def test_volume_infundido_24h_com_velocidade_alterada(dieta_enteral_basica):
    dieta_enteral_basica.velocidade_ml_h = 100.0
    
    # 100 ml/h * 24h = 2400 ml
    assert dieta_enteral_basica.volume_infundido_24h == 2400.0


# --- Testes de calcular_nutrientes() ---

def test_calcular_nutrientes_retorna_metadados(dieta_enteral_basica):
    resultado = dieta_enteral_basica.calcular_nutrientes()
    
    assert resultado["tipo_dieta"] == "Enteral"
    assert resultado["via_infusao"] == "nasogástrica"
    assert resultado["tipo_equipo"] == "bomba"
    assert resultado["porcoes_diarias"] == 1
    assert resultado["quantidade_gramas_por_porção"] == 200.0
    assert "total_gramas_diarias" in resultado
    assert "velocidade_ml_h" in resultado
    assert "equipo_por_porção" in resultado
    assert "equipo_unico_por_dia" in resultado


def test_calcular_total_gramas_diarias_1_porcao(dieta_enteral_basica):
    resultado = dieta_enteral_basica.calcular_nutrientes()
    
    # 200g/porção * 1 porção = 200g
    assert resultado["total_gramas_diarias"] == 200.0


def test_calcular_total_gramas_diarias_multiplas_porcoes(dieta_enteral_completa):
    resultado = dieta_enteral_completa.calcular_nutrientes()
    
    # 250g/porção * 4 porções = 1000g
    assert resultado["total_gramas_diarias"] == 1000.0


def test_equipo_flags_bomba(dieta_enteral_basica):
    resultado = dieta_enteral_basica.calcular_nutrientes()
    
    assert resultado["equipo_unico_por_dia"] == True
    assert resultado["equipo_por_porção"] == False


def test_equipo_flags_gravitacional(dieta_enteral_completa):
    resultado = dieta_enteral_completa.calcular_nutrientes()
    
    assert resultado["equipo_por_porção"] == True
    assert resultado["equipo_unico_por_dia"] == False


def test_validar_compatibilidade_dieta_valida(dieta_enteral_basica):
    assert dieta_enteral_basica.validar_compatibilidade() == True


def test_validar_compatibilidade_com_todos_parametros(dieta_enteral_completa):
    assert dieta_enteral_completa.validar_compatibilidade() == True


def test_dieta_herda_auditoria_mixin(dieta_enteral_basica):
    assert hasattr(dieta_enteral_basica, 'criado_em')
    assert hasattr(dieta_enteral_basica, 'atualizado_em')
    assert hasattr(dieta_enteral_basica, 'usuario_responsavel')


def test_dieta_herda_status_dieta_mixin(dieta_enteral_basica):
    assert hasattr(dieta_enteral_basica, 'ativo')
    assert hasattr(dieta_enteral_basica, 'data_inicio')
    assert hasattr(dieta_enteral_basica, 'encerrar_dieta')


def test_encerrar_dieta(dieta_enteral_basica):
    assert dieta_enteral_basica.ativo == True
    
    dieta_enteral_basica.encerrar_dieta()
    
    assert dieta_enteral_basica.ativo == False
    assert dieta_enteral_basica.data_fim is not None


def test_erro_encerrar_dieta_ja_encerrada(dieta_enteral_basica):
    dieta_enteral_basica.encerrar_dieta()
    
    with pytest.raises(ValueError, match="Dieta já foi encerrada"):
        dieta_enteral_basica.encerrar_dieta()


def test_fluxo_completo_criacao_e_modificacao(setor_uti):
    # 1. Criar dieta
    dieta = DietaEnteral(
        setor_clinico=setor_uti,
        via_infusao="sng",
        velocidade_ml_h=50.0,
        quantidade_gramas_por_porção=200.0,
        porcoes_diarias=1,
        tipo_equipo="bomba"
    )
    
    # 2. Verificar valores iniciais
    assert dieta.via_infusao == "sng"
    assert dieta.velocidade_ml_h == 50.0
    assert dieta.porcoes_diarias == 1
    
    # 3. Modificar parâmetros
    dieta.via_infusao = "gastrostomia"
    dieta.velocidade_ml_h = 75.0
    dieta.porcoes_diarias = 3
    dieta.tipo_equipo = "gravitacional"
    
    # 4. Verificar valores atualizados
    assert dieta.via_infusao == "gastrostomia"
    assert dieta.velocidade_ml_h == 75.0
    assert dieta.porcoes_diarias == 3
    assert dieta.tipo_equipo == "gravitacional"
    
    # 5. Calcular nutrientes com novos valores
    resultado = dieta.calcular_nutrientes()
    
    # 200g/porção * 3 porções = 600g
    assert resultado["total_gramas_diarias"] == 600.0
    assert resultado["equipo_por_porção"] == True
    assert resultado["velocidade_ml_h"] == 75.0


def test_fluxo_calculo_gramas_dinamico(setor_uti):
    dieta = DietaEnteral(
        setor_clinico=setor_uti,
        via_infusao="sng",
        velocidade_ml_h=50.0,
        quantidade_gramas_por_porção=150.0,
        porcoes_diarias=2
    )
    
    # Inicial: 150g * 2 = 300g
    resultado = dieta.calcular_nutrientes()
    assert resultado["total_gramas_diarias"] == 300.0
    
    # Aumenta porções: 150g * 4 = 600g
    dieta.porcoes_diarias = 4
    resultado = dieta.calcular_nutrientes()
    assert resultado["total_gramas_diarias"] == 600.0


def test_fluxo_volume_infundido_dinamico(setor_uti):
    dieta = DietaEnteral(
        setor_clinico=setor_uti,
        via_infusao="sng",
        velocidade_ml_h=40.0,
        quantidade_gramas_por_porção=200.0
    )
    
    # Inicial: 40 ml/h * 24h = 960 ml
    assert dieta.volume_infundido_24h == 960.0
    
    # Aumenta velocidade: 80 ml/h * 24h = 1920 ml
    dieta.velocidade_ml_h = 80.0
    assert dieta.volume_infundido_24h == 1920.0


def test_quantidade_gramas_muito_pequena(setor_uti):
    dieta = DietaEnteral(
        setor_clinico=setor_uti,
        via_infusao="sng",
        velocidade_ml_h=50.0,
        quantidade_gramas_por_porção=0.1  
    )
    
    assert dieta._quantidade_gramas_por_porção == 0.1


def test_quantidade_gramas_muito_grande(setor_uti):
    dieta = DietaEnteral(
        setor_clinico=setor_uti,
        via_infusao="sng",
        velocidade_ml_h=50.0,
        quantidade_gramas_por_porção=10000.0  
    )
    
    assert dieta._quantidade_gramas_por_porção == 10000.0


def test_velocidade_decimal(setor_uti):
    dieta = DietaEnteral(
        setor_clinico=setor_uti,
        via_infusao="sng",
        velocidade_ml_h=37.5,
        quantidade_gramas_por_porção=200.0
    )
    
    assert dieta.velocidade_ml_h == 37.5


def test_porcoes_diarias_numero_grande(setor_uti):
    dieta = DietaEnteral(
        setor_clinico=setor_uti,
        via_infusao="sng",
        velocidade_ml_h=50.0,
        quantidade_gramas_por_porção=100.0,
        porcoes_diarias=10 
    )
    
    resultado = dieta.calcular_nutrientes()
    assert resultado["total_gramas_diarias"] == 1000.0