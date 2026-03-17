import pytest
from src.snh_project.core.diets import DietaParenteral


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def dieta_parenteral_basica():
    """DietaParenteral com parâmetros mínimos válidos."""
    return DietaParenteral(
        tipo_acesso="central",
        volume_ml_dia=2000.0,
        composicao="Glicose 50% + Aminoácidos 10% + Lipídios 20%",
        velocidade_ml_h=83.3  # 83.3 * 24 = 1999.2 ml (~100% do volume)
    )


@pytest.fixture
def dieta_parenteral_completa():
    """DietaParenteral com todos os parâmetros."""
    return DietaParenteral(
        tipo_acesso="picc",
        volume_ml_dia=1500.0,
        composicao="Glicose 70% + Aminoácidos 15%",
        velocidade_ml_h=62.5,  # 62.5 * 24 = 1500 ml (100% do volume)
        descricao="NPT pós-operatório",
        usuario_responsavel="Dr. Silva"
    )


@pytest.fixture
def dieta_parenteral_periferico():
    """DietaParenteral com acesso periférico."""
    return DietaParenteral(
        tipo_acesso="periférico",
        volume_ml_dia=1000.0,
        composicao="Glicose 10% + Aminoácidos 5%",
        velocidade_ml_h=41.7  # 41.7 * 24 = 1000.8 ml
    )


# =============================================================================
# TESTES DE CRIAÇÃO
# =============================================================================

def test_criar_dieta_parenteral_parametros_minimos():
    """Deve criar DietaParenteral com parâmetros mínimos válidos."""
    dieta = DietaParenteral(
        tipo_acesso="central",
        volume_ml_dia=2000.0,
        composicao="Glicose 50% + Aminoácidos 10%",
        velocidade_ml_h=83.3
    )
    
    assert dieta.tipo_acesso == "central"
    assert dieta.volume_ml_dia == 2000.0
    assert dieta.velocidade_ml_h == 83.3
    assert "Glicose" in dieta.composicao


def test_criar_dieta_parenteral_parametros_completos(dieta_parenteral_completa):
    """Deve armazenar todos os parâmetros corretamente."""
    assert dieta_parenteral_completa.tipo_acesso == "picc"
    assert dieta_parenteral_completa.volume_ml_dia == 1500.0
    assert dieta_parenteral_completa.velocidade_ml_h == 62.5
    assert dieta_parenteral_completa.composicao == "Glicose 70% + Aminoácidos 15%"
    assert dieta_parenteral_completa.descricao == "NPT pós-operatório"
    assert dieta_parenteral_completa.usuario_responsavel == "Dr. Silva"


def test_tipo_acesso_normalizado_para_lowercase():
    """Tipo de acesso deve ser normalizado para lowercase."""
    dieta = DietaParenteral(
        tipo_acesso="CENTRAL",
        volume_ml_dia=2000.0,
        composicao="Glicose 50%",
        velocidade_ml_h=83.3
    )
    
    assert dieta.tipo_acesso == "central"


def test_composicao_com_espacos_removidos():
    """Composição deve ter espaços extras removidos."""
    dieta = DietaParenteral(
        tipo_acesso="central",
        volume_ml_dia=2000.0,
        composicao="  Glicose 50% + Aminoácidos 10%  ",
        velocidade_ml_h=83.3
    )
    
    assert dieta.composicao == "Glicose 50% + Aminoácidos 10%"


def test_descricao_default_quando_nao_fornecida():
    """Quando descricao não é fornecida, deve gerar uma automática."""
    dieta = DietaParenteral(
        tipo_acesso="central",
        volume_ml_dia=2000.0,
        composicao="Glicose 50%",
        velocidade_ml_h=83.3
    )
    
    assert dieta.descricao == "Dieta Parenteral via central"


def test_dieta_inicia_ativa(dieta_parenteral_basica):
    """Dieta deve iniciar ativa."""
    assert dieta_parenteral_basica.ativo == True
    assert dieta_parenteral_basica.data_fim is None


# =============================================================================
# TESTES DE VALIDAÇÃO DE TIPO DE ACESSO
# =============================================================================

def test_tipos_acesso_validos():
    """Todos os tipos de acesso válidos devem ser aceitos."""
    tipos_validos = ["periférico", "central", "cateter central", "picc"]
    
    for tipo in tipos_validos:
        dieta = DietaParenteral(
            tipo_acesso=tipo,
            volume_ml_dia=1000.0,
            composicao="Glicose 50%",
            velocidade_ml_h=41.7
        )
        assert dieta.tipo_acesso == tipo.lower()


def test_erro_tipo_acesso_invalido():
    """Tipo de acesso inválido deve lançar ValueError."""
    with pytest.raises(ValueError, match="Tipo de acesso inválido"):
        DietaParenteral(
            tipo_acesso="subcutâneo",
            volume_ml_dia=1000.0,
            composicao="Glicose 50%",
            velocidade_ml_h=41.7
        )


def test_erro_tipo_acesso_vazio():
    """Tipo de acesso vazio deve lançar ValueError."""
    with pytest.raises(ValueError, match="Tipo de acesso inválido"):
        DietaParenteral(
            tipo_acesso="",
            volume_ml_dia=1000.0,
            composicao="Glicose 50%",
            velocidade_ml_h=41.7
        )


# =============================================================================
# TESTES DE VALIDAÇÃO DE VOLUME
# =============================================================================

def test_erro_volume_zero():
    """Volume zero deve lançar ValueError."""
    with pytest.raises(ValueError, match="Volume por dia deve ser maior que 0"):
        DietaParenteral(
            tipo_acesso="central",
            volume_ml_dia=0.0,
            composicao="Glicose 50%",
            velocidade_ml_h=83.3
        )


def test_erro_volume_negativo():
    """Volume negativo deve lançar ValueError."""
    with pytest.raises(ValueError, match="Volume por dia deve ser maior que 0"):
        DietaParenteral(
            tipo_acesso="central",
            volume_ml_dia=-500.0,
            composicao="Glicose 50%",
            velocidade_ml_h=83.3
        )


# =============================================================================
# TESTES DE VALIDAÇÃO DE VELOCIDADE
# =============================================================================

def test_erro_velocidade_zero():
    """Velocidade zero deve lançar ValueError."""
    with pytest.raises(ValueError, match="Velocidade de infusão deve ser maior que 0"):
        DietaParenteral(
            tipo_acesso="central",
            volume_ml_dia=2000.0,
            composicao="Glicose 50%",
            velocidade_ml_h=0.0
        )


def test_erro_velocidade_negativa():
    """Velocidade negativa deve lançar ValueError."""
    with pytest.raises(ValueError, match="Velocidade de infusão deve ser maior que 0"):
        DietaParenteral(
            tipo_acesso="central",
            volume_ml_dia=2000.0,
            composicao="Glicose 50%",
            velocidade_ml_h=-10.0
        )


# =============================================================================
# TESTES DE VALIDAÇÃO DE COMPOSIÇÃO
# =============================================================================

def test_erro_composicao_vazia():
    """Composição vazia deve lançar ValueError."""
    with pytest.raises(ValueError, match="Composição não pode ser vazia"):
        DietaParenteral(
            tipo_acesso="central",
            volume_ml_dia=2000.0,
            composicao="",
            velocidade_ml_h=83.3
        )


def test_erro_composicao_apenas_espacos():
    """Composição com apenas espaços deve lançar ValueError."""
    with pytest.raises(ValueError, match="Composição não pode ser vazia"):
        DietaParenteral(
            tipo_acesso="central",
            volume_ml_dia=2000.0,
            composicao="   ",
            velocidade_ml_h=83.3
        )


# =============================================================================
# TESTES DE VALIDAÇÃO DE CONSISTÊNCIA VOLUME vs VELOCIDADE
# =============================================================================

def test_erro_velocidade_muito_baixa_para_volume():
    """Velocidade que infunde <80% do volume deve lançar ValueError."""
    with pytest.raises(ValueError, match="Velocidade.*ml/h infundiria"):
        DietaParenteral(
            tipo_acesso="central",
            volume_ml_dia=2000.0,
            composicao="Glicose 50%",
            velocidade_ml_h=60.0  # 60 * 24 = 1440 ml (72% do volume)
        )


def test_erro_velocidade_muito_alta_para_volume():
    """Velocidade que infunde >120% do volume deve lançar ValueError."""
    with pytest.raises(ValueError, match="Velocidade.*ml/h infundiria"):
        DietaParenteral(
            tipo_acesso="central",
            volume_ml_dia=2000.0,
            composicao="Glicose 50%",
            velocidade_ml_h=110.0  # 110 * 24 = 2640 ml (132% do volume)
        )


def test_tolerancia_20_porcento_aceita():
    """Velocidade dentro da tolerância de ±20% deve ser aceita."""
    # Teste com 80% (limite inferior)
    dieta1 = DietaParenteral(
        tipo_acesso="central",
        volume_ml_dia=2000.0,
        composicao="Glicose 50%",
        velocidade_ml_h=66.7  # 66.7 * 24 = 1600.8 ml (80% do volume)
    )
    assert dieta1.volume_ml_dia == 2000.0
    
    # Teste com 120% (limite superior)
    dieta2 = DietaParenteral(
        tipo_acesso="central",
        volume_ml_dia=2000.0,
        composicao="Glicose 50%",
        velocidade_ml_h=100.0  # 100 * 24 = 2400 ml (120% do volume)
    )
    assert dieta2.volume_ml_dia == 2000.0


# =============================================================================
# TESTES DE ALTERAÇÃO DE PROPRIEDADES (SETTERS)
# =============================================================================

def test_alterar_tipo_acesso_valido(dieta_parenteral_basica):
    """Deve permitir alterar tipo de acesso para outro válido."""
    dieta_parenteral_basica.tipo_acesso = "periférico"
    
    assert dieta_parenteral_basica.tipo_acesso == "periférico"


def test_erro_alterar_tipo_acesso_invalido(dieta_parenteral_basica):
    """Alterar para tipo de acesso inválido deve lançar ValueError."""
    with pytest.raises(ValueError, match="Tipo de acesso inválido"):
        dieta_parenteral_basica.tipo_acesso = "intramuscular"


def test_alterar_volume_valido(dieta_parenteral_basica):
    """Deve permitir alterar volume para valor válido."""
    dieta_parenteral_basica.volume_ml_dia = 1500.0
    
    assert dieta_parenteral_basica.volume_ml_dia == 1500.0


def test_erro_alterar_volume_zero(dieta_parenteral_basica):
    """Alterar volume para zero deve lançar ValueError."""
    with pytest.raises(ValueError, match="Volume por dia deve ser maior que 0"):
        dieta_parenteral_basica.volume_ml_dia = 0.0


def test_alterar_velocidade_valida(dieta_parenteral_basica):
    """Deve permitir alterar velocidade para valor válido."""
    dieta_parenteral_basica.velocidade_ml_h = 100.0
    
    assert dieta_parenteral_basica.velocidade_ml_h == 100.0


def test_erro_alterar_velocidade_zero(dieta_parenteral_basica):
    """Alterar velocidade para zero deve lançar ValueError."""
    with pytest.raises(ValueError, match="Velocidade de infusão deve ser maior que 0"):
        dieta_parenteral_basica.velocidade_ml_h = 0.0


def test_alterar_composicao_valida(dieta_parenteral_basica):
    """Deve permitir alterar composição para valor válido."""
    dieta_parenteral_basica.composicao = "Glicose 70% + Lipídios 30%"
    
    assert dieta_parenteral_basica.composicao == "Glicose 70% + Lipídios 30%"


def test_erro_alterar_composicao_vazia(dieta_parenteral_basica):
    """Alterar composição para vazia deve lançar ValueError."""
    with pytest.raises(ValueError, match="Composição não pode ser vazia"):
        dieta_parenteral_basica.composicao = ""


# =============================================================================
# TESTES DE PROPRIEDADES CALCULADAS
# =============================================================================

def test_volume_infundido_24h(dieta_parenteral_basica):
    """Deve calcular corretamente o volume infundido em 24 horas."""
    # velocidade = 83.3 ml/h
    # 83.3 ml/h * 24h = 1999.2 ml
    assert dieta_parenteral_basica.volume_infundido_24h == pytest.approx(1999.2, rel=0.01)


def test_volume_infundido_24h_com_velocidade_alterada(dieta_parenteral_basica):
    """Volume infundido deve atualizar quando velocidade muda."""
    dieta_parenteral_basica.velocidade_ml_h = 100.0
    
    # 100 ml/h * 24h = 2400 ml
    assert dieta_parenteral_basica.volume_infundido_24h == 2400.0


def test_percentual_volume_atingido(dieta_parenteral_basica):
    """Deve calcular corretamente o percentual do volume atingido."""
    # volume_infundido_24h = 1999.2 ml
    # volume_ml_dia = 2000.0 ml
    # percentual = (1999.2 / 2000.0) * 100 ≈ 99.96%
    assert dieta_parenteral_basica.percentual_volume_atingido == pytest.approx(99.96, rel=0.01)


def test_percentual_volume_atingido_100_porcento():
    """Percentual deve ser exatamente 100% quando velocidade é perfeita."""
    dieta = DietaParenteral(
        tipo_acesso="central",
        volume_ml_dia=2400.0,
        composicao="Glicose 50%",
        velocidade_ml_h=100.0  # 100 * 24 = 2400 ml (100%)
    )
    
    assert dieta.percentual_volume_atingido == pytest.approx(100.0)


def test_tempo_para_infundir_horas(dieta_parenteral_basica):
    """Deve calcular corretamente o tempo para infundir todo o volume."""
    # volume_ml_dia = 2000.0 ml
    # velocidade_ml_h = 83.3 ml/h
    # tempo = 2000.0 / 83.3 ≈ 24.01 horas
    assert dieta_parenteral_basica.tempo_para_infundir_horas == pytest.approx(24.01, rel=0.01)


def test_tempo_para_infundir_24h_exatas():
    """Quando velocidade é perfeita, tempo deve ser exatamente 24h."""
    dieta = DietaParenteral(
        tipo_acesso="central",
        volume_ml_dia=2400.0,
        composicao="Glicose 50%",
        velocidade_ml_h=100.0  # 2400 / 100 = 24h
    )
    
    assert dieta.tempo_para_infundir_horas == pytest.approx(24.0)


# =============================================================================
# TESTES DE calcular_nutrientes()
# =============================================================================

def test_calcular_nutrientes_retorna_metadados(dieta_parenteral_basica):
    """calcular_nutrientes() deve retornar estrutura correta."""
    resultado = dieta_parenteral_basica.calcular_nutrientes()
    
    assert resultado["tipo_dieta"] == "Parenteral"
    assert resultado["tipo_acesso"] == "central"
    assert resultado["volume_ml_dia"] == 2000.0
    assert "Glicose" in resultado["composicao"]
    assert resultado["velocidade_ml_h"] == 83.3
    assert "volume_infundido_24h" in resultado
    assert "percentual_volume_atingido" in resultado
    assert "tempo_para_infundir_horas" in resultado
    assert "quantidade_itens" in resultado


def test_calcular_nutrientes_valores_corretos(dieta_parenteral_completa):
    """Valores calculados devem estar corretos."""
    resultado = dieta_parenteral_completa.calcular_nutrientes()
    
    assert resultado["volume_ml_dia"] == 1500.0
    assert resultado["velocidade_ml_h"] == 62.5
    assert resultado["volume_infundido_24h"] == 1500.0  # 62.5 * 24
    assert resultado["percentual_volume_atingido"] == pytest.approx(100.0)
    assert resultado["tempo_para_infundir_horas"] == pytest.approx(24.0)  # 1500 / 62.5


# =============================================================================
# TESTES DE validar_compatibilidade()
# =============================================================================

def test_validar_compatibilidade_dieta_valida(dieta_parenteral_basica):
    """Dieta válida deve passar na validação."""
    assert dieta_parenteral_basica.validar_compatibilidade() == True


def test_validar_compatibilidade_com_todos_parametros(dieta_parenteral_completa):
    """Dieta completa deve passar na validação."""
    assert dieta_parenteral_completa.validar_compatibilidade() == True


def test_validar_compatibilidade_tipo_acesso_invalido(dieta_parenteral_basica):
    """Dieta com tipo de acesso inválido deve falhar na validação."""
    # Forçar tipo de acesso inválido (manipulando atributo privado)
    dieta_parenteral_basica._tipo_acesso = "invalido"
    
    assert dieta_parenteral_basica.validar_compatibilidade() == False


def test_validar_compatibilidade_volume_zero(dieta_parenteral_basica):
    """Dieta com volume zero deve falhar na validação."""
    dieta_parenteral_basica._volume_ml_dia = 0.0
    
    assert dieta_parenteral_basica.validar_compatibilidade() == False


def test_validar_compatibilidade_velocidade_zero(dieta_parenteral_basica):
    """Dieta com velocidade zero deve falhar na validação."""
    dieta_parenteral_basica._velocidade_ml_h = 0.0
    
    assert dieta_parenteral_basica.validar_compatibilidade() == False


def test_validar_compatibilidade_composicao_vazia(dieta_parenteral_basica):
    """Dieta com composição vazia deve falhar na validação."""
    dieta_parenteral_basica._composicao = ""
    
    assert dieta_parenteral_basica.validar_compatibilidade() == False


def test_validar_compatibilidade_volume_velocidade_inconsistentes(dieta_parenteral_basica):
    """Dieta com volume e velocidade inconsistentes deve falhar."""
    # Forçar velocidade muito baixa
    dieta_parenteral_basica._velocidade_ml_h = 50.0  # 50 * 24 = 1200 ml (60% do volume)
    
    assert dieta_parenteral_basica.validar_compatibilidade() == False


# =============================================================================
# TESTES DE HERANÇA DOS MIXINS
# =============================================================================

def test_dieta_herda_auditoria_mixin(dieta_parenteral_basica):
    """Deve herdar propriedades de AuditoriaMixin."""
    assert hasattr(dieta_parenteral_basica, 'criado_em')
    assert hasattr(dieta_parenteral_basica, 'atualizado_em')
    assert hasattr(dieta_parenteral_basica, 'usuario_responsavel')


def test_dieta_herda_status_dieta_mixin(dieta_parenteral_basica):
    """Deve herdar propriedades de StatusDietaMixin."""
    assert hasattr(dieta_parenteral_basica, 'ativo')
    assert hasattr(dieta_parenteral_basica, 'data_inicio')
    assert hasattr(dieta_parenteral_basica, 'encerrar_dieta')


def test_usuario_responsavel_default():
    """Usuario responsável deve ser 'sistema' por padrão."""
    dieta = DietaParenteral(
        tipo_acesso="central",
        volume_ml_dia=2000.0,
        composicao="Glicose 50%",
        velocidade_ml_h=83.3
    )
    
    assert dieta.usuario_responsavel == "sistema"


def test_registrar_atualizacao_ao_alterar_propriedade(dieta_parenteral_basica):
    """atualizado_em deve mudar quando propriedade é alterada."""
    import time
    
    timestamp_inicial = dieta_parenteral_basica.atualizado_em
    time.sleep(0.01)  # Pequeno delay para garantir timestamp diferente
    
    dieta_parenteral_basica.velocidade_ml_h = 90.0
    
    assert dieta_parenteral_basica.atualizado_em > timestamp_inicial


# =============================================================================
# TESTES DE ENCERRAMENTO DE DIETA
# =============================================================================

def test_encerrar_dieta(dieta_parenteral_basica):
    """Deve encerrar dieta corretamente."""
    assert dieta_parenteral_basica.ativo == True
    
    dieta_parenteral_basica.encerrar_dieta()
    
    assert dieta_parenteral_basica.ativo == False
    assert dieta_parenteral_basica.data_fim is not None


def test_erro_encerrar_dieta_ja_encerrada(dieta_parenteral_basica):
    """Tentar encerrar dieta já encerrada deve lançar ValueError."""
    dieta_parenteral_basica.encerrar_dieta()
    
    with pytest.raises(ValueError, match="Dieta já foi encerrada"):
        dieta_parenteral_basica.encerrar_dieta()


# =============================================================================
# TESTES DE __repr__
# =============================================================================

def test_repr_formato_correto(dieta_parenteral_basica):
    """__repr__ deve ter formato legível."""
    repr_str = repr(dieta_parenteral_basica)
    
    assert "DietaParenteral" in repr_str
    assert "acesso=central" in repr_str
    assert "volume=2000.0ml" in repr_str
    assert "vel=83.3ml/h" in repr_str
    assert "ativo=True" in repr_str


# =============================================================================
# TESTES DE FLUXO COMPLETO
# =============================================================================

def test_fluxo_completo_criacao_e_modificacao():
    """Teste de fluxo completo: criação, modificação e cálculos."""
    # 1. Criar dieta
    dieta = DietaParenteral(
        tipo_acesso="periférico",
        volume_ml_dia=1000.0,
        composicao="Glicose 10%",
        velocidade_ml_h=41.7  # 41.7 * 24 = 1000.8 ml
    )
    
    # 2. Verificar valores iniciais
    assert dieta.tipo_acesso == "periférico"
    assert dieta.volume_ml_dia == 1000.0
    assert dieta.velocidade_ml_h == 41.7
    
    # 3. Modificar parâmetros
    dieta.tipo_acesso = "central"
    dieta.volume_ml_dia = 2000.0
    # Não alteramos velocidade ainda (seria inconsistente)
    
    # 4. Ajustar velocidade para nova volume
    dieta.velocidade_ml_h = 83.3  # 83.3 * 24 ≈ 2000 ml
    
    # 5. Verificar valores atualizados
    assert dieta.tipo_acesso == "central"
    assert dieta.volume_ml_dia == 2000.0
    assert dieta.velocidade_ml_h == 83.3
    
    # 6. Calcular nutrientes com novos valores
    resultado = dieta.calcular_nutrientes()
    
    assert resultado["volume_ml_dia"] == 2000.0
    assert resultado["velocidade_ml_h"] == 83.3
    assert resultado["percentual_volume_atingido"] == pytest.approx(99.96, rel=0.01)


def test_fluxo_volume_infundido_dinamico():
    """Volume infundido deve atualizar dinamicamente."""
    dieta = DietaParenteral(
        tipo_acesso="central",
        volume_ml_dia=2400.0,
        composicao="Glicose 50%",
        velocidade_ml_h=80.0
    )
    
    # Inicial: 80 ml/h * 24h = 1920 ml
    assert dieta.volume_infundido_24h == 1920.0
    
    # Aumenta velocidade: 100 ml/h * 24h = 2400 ml
    dieta.velocidade_ml_h = 100.0
    assert dieta.volume_infundido_24h == 2400.0


def test_fluxo_percentual_dinamico():
    """Percentual deve atualizar dinamicamente."""
    dieta = DietaParenteral(
        tipo_acesso="central",
        volume_ml_dia=2000.0,
        composicao="Glicose 50%",
        velocidade_ml_h=66.7  # 66.7 * 24 = 1600.8 ml (80%)
    )
    
    # Inicial: ~80%
    assert dieta.percentual_volume_atingido == pytest.approx(80.04, rel=0.01)
    
    # Aumenta para ~100%
    dieta.velocidade_ml_h = 83.3  # 83.3 * 24 = 1999.2 ml
    assert dieta.percentual_volume_atingido == pytest.approx(99.96, rel=0.01)


# =============================================================================
# TESTES DE CASOS EXTREMOS
# =============================================================================

def test_volume_muito_pequeno():
    """Deve aceitar volumes muito pequenos."""
    dieta = DietaParenteral(
        tipo_acesso="central",
        volume_ml_dia=100.0,
        composicao="Glicose 5%",
        velocidade_ml_h=4.17  # 4.17 * 24 = 100.08 ml
    )
    
    assert dieta.volume_ml_dia == 100.0


def test_volume_muito_grande():
    """Deve aceitar volumes muito grandes."""
    dieta = DietaParenteral(
        tipo_acesso="central",
        volume_ml_dia=5000.0,
        composicao="Glicose 50%",
        velocidade_ml_h=208.3  # 208.3 * 24 = 4999.2 ml
    )
    
    assert dieta.volume_ml_dia == 5000.0


def test_velocidade_decimal_precisa():
    """Deve aceitar velocidades com decimais."""
    dieta = DietaParenteral(
        tipo_acesso="central",
        volume_ml_dia=1234.0,
        composicao="Glicose 50%",
        velocidade_ml_h=51.42  # 51.42 * 24 = 1234.08 ml
    )
    
    assert dieta.velocidade_ml_h == 51.42


def test_composicao_muito_longa():
    """Deve aceitar composições longas e detalhadas."""
    composicao_longa = (
        "Glicose 50% 500ml + Aminoácidos 10% 500ml + "
        "Lipídios 20% 250ml + NaCl 20% 20ml + KCl 19.1% 10ml + "
        "Vitaminas + Oligoelementos"
    )
    
    dieta = DietaParenteral(
        tipo_acesso="central",
        volume_ml_dia=1500.0,
        composicao=composicao_longa,
        velocidade_ml_h=62.5
    )
    
    assert dieta.composicao == composicao_longa


def test_acesso_periferio_com_acento():
    """Deve aceitar 'periférico' com acento."""
    dieta = DietaParenteral(
        tipo_acesso="periférico",
        volume_ml_dia=1000.0,
        composicao="Glicose 10%",
        velocidade_ml_h=41.7
    )
    
    assert dieta.tipo_acesso == "periférico"


def test_acesso_cateter_central_completo():
    """Deve aceitar 'cateter central' por extenso."""
    dieta = DietaParenteral(
        tipo_acesso="cateter central",
        volume_ml_dia=2000.0,
        composicao="Glicose 50%",
        velocidade_ml_h=83.3
    )
    
    assert dieta.tipo_acesso == "cateter central"