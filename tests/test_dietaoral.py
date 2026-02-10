import pytest
from src.snh_project.core.diet import DietaOral, ItemCardapio

@pytest.fixture
def dieta_oral_basica():
    return DietaOral(
        textura="normal",
        numero_refeicoes=3,
        tipo_refeicao="almoço"
    )


@pytest.fixture
def dieta_oral_completa():
    return DietaOral(
        textura="pastosa",
        numero_refeicoes=6,
        tipo_refeicao="janta",
        descricao="Dieta pós-operatória",
        usuario_responsavel="Dra. Silva"
    )


@pytest.fixture
def item_arroz():
    return ItemCardapio("Arroz Branco", 200.0)


@pytest.fixture
def item_leite():
    return ItemCardapio("Leite", 250.0, restricoes=["lactose"])


@pytest.fixture
def item_pao():
    return ItemCardapio("Pão Francês", 80.0, restricoes=["glúten"])


def test_criar_dieta_oral_parametros_minimos():
    dieta = DietaOral(
        textura="normal",
        numero_refeicoes=4,
        tipo_refeicao="desjejum"
    )
    
    assert dieta.textura == "normal"
    assert dieta._numero_refeicoes == 4
    assert dieta._tipo_refeicao == "desjejum"


def test_criar_dieta_oral_parametros_completos(dieta_oral_completa):
    assert dieta_oral_completa.textura == "pastosa"
    assert dieta_oral_completa._numero_refeicoes == 6
    assert dieta_oral_completa._tipo_refeicao == "janta"
    assert dieta_oral_completa.descricao == "Dieta pós-operatória"
    assert dieta_oral_completa.usuario_responsavel == "Dra. Silva"


def test_textura_normalizada_para_lowercase():
    dieta = DietaOral(
        textura="PASTOSA",
        numero_refeicoes=3,
        tipo_refeicao="almoço"
    )
    
    assert dieta.textura == "pastosa" 


def test_tipo_refeicao_normalizado_para_lowercase():
    dieta = DietaOral(
        textura="normal",
        numero_refeicoes=3,
        tipo_refeicao="JANTA"
    )
    
    assert dieta._tipo_refeicao == "janta"


def test_dieta_inicia_ativa():
    dieta = DietaOral("normal", 3, "almoço")
    
    assert dieta.ativo == True
    assert dieta.data_fim is None


def test_erro_textura_invalida():
    with pytest.raises(ValueError, match="Textura inválida"):
        DietaOral(
            textura="crocante",  
            numero_refeicoes=3,
            tipo_refeicao="almoço"
        )


def test_erro_numero_refeicoes_zero():
    with pytest.raises(ValueError, match="Número de refeições deve ser maior que 0"):
        DietaOral(
            textura="normal",
            numero_refeicoes=0,
            tipo_refeicao="almoço"
        )


def test_erro_numero_refeicoes_negativo():
    with pytest.raises(ValueError, match="Número de refeições deve ser maior que 0"):
        DietaOral(
            textura="normal",
            numero_refeicoes=-5,
            tipo_refeicao="almoço"
        )


def test_erro_tipo_refeicao_invalido():
    with pytest.raises(ValueError, match="Tipo de refeição inválido"):
        DietaOral(
            textura="normal",
            numero_refeicoes=3,
            tipo_refeicao="merenda"  
        )



def test_textura_normal_valida():
    dieta = DietaOral("normal", 3, "almoço")
    assert dieta.textura == "normal"


def test_textura_mole_valida():
    dieta = DietaOral("mole", 3, "almoço")
    assert dieta.textura == "mole"


def test_textura_pastosa_valida():
    dieta = DietaOral("pastosa", 3, "almoço")
    assert dieta.textura == "pastosa"


def test_textura_liquida_valida():
    dieta = DietaOral("liquida", 3, "almoço")
    assert dieta.textura == "liquida"


def test_tipo_refeicao_desjejum():
    dieta = DietaOral("normal", 3, "desjejum")
    assert dieta._tipo_refeicao == "desjejum"


def test_tipo_refeicao_almoco():
    dieta = DietaOral("normal", 3, "almoco")
    assert dieta._tipo_refeicao == "almoco"


def test_tipo_refeicao_almoco_com_acento():
    dieta = DietaOral("normal", 3, "almoço")
    assert dieta._tipo_refeicao == "almoço"


def test_tipo_refeicao_janta():
    dieta = DietaOral("normal", 3, "janta")
    assert dieta._tipo_refeicao == "janta"


def test_tipo_refeicao_lanche():
    dieta = DietaOral("normal", 3, "lanche")
    assert dieta._tipo_refeicao == "lanche"


def test_tipo_refeicao_ceia():
    dieta = DietaOral("normal", 3, "ceia")
    assert dieta._tipo_refeicao == "ceia"


def test_adicionar_restricao_proibida(dieta_oral_basica):
    dieta_oral_basica.adicionar_restricao_proibida("lactose")
    
    assert dieta_oral_basica.tem_restricao_proibida("lactose")


def test_adicionar_multiplas_restricoes_proibidas(dieta_oral_basica):
    dieta_oral_basica.adicionar_restricao_proibida("lactose")
    dieta_oral_basica.adicionar_restricao_proibida("glúten")
    dieta_oral_basica.adicionar_restricao_proibida("soja")
    
    restricoes = dieta_oral_basica.listar_restricoes_proibidas()
    
    assert len(restricoes) == 3
    assert "glúten" in restricoes
    assert "lactose" in restricoes
    assert "soja" in restricoes


def test_restricao_proibida_normalizada_para_lowercase(dieta_oral_basica):
    dieta_oral_basica.adicionar_restricao_proibida("LACTOSE")
    
    assert dieta_oral_basica.tem_restricao_proibida("lactose")
    assert "lactose" in dieta_oral_basica.listar_restricoes_proibidas()


def test_remover_restricao_proibida_existente(dieta_oral_basica):
    dieta_oral_basica.adicionar_restricao_proibida("glúten")
    
    removido = dieta_oral_basica.remover_restricao_proibida("glúten")
    
    assert removido == True
    assert not dieta_oral_basica.tem_restricao_proibida("glúten")


def test_remover_restricao_proibida_inexistente(dieta_oral_basica):
    removido = dieta_oral_basica.remover_restricao_proibida("lactose")
    
    assert removido == False


def test_erro_adicionar_restricao_vazia(dieta_oral_basica):
    with pytest.raises(ValueError, match="Restrição inválida"):
        dieta_oral_basica.adicionar_restricao_proibida("")


def test_erro_adicionar_restricao_apenas_espacos(dieta_oral_basica):
    with pytest.raises(ValueError, match="Restrição inválida"):
        dieta_oral_basica.adicionar_restricao_proibida("   ")


def test_adicionar_item_sem_conflito(dieta_oral_basica, item_arroz):
    dieta_oral_basica.adicionar_item(item_arroz)
    
    assert dieta_oral_basica.quantidade_itens == 1
    assert dieta_oral_basica.obter_item("Arroz Branco") == item_arroz


def test_adicionar_item_com_restricao_mas_sem_conflito(dieta_oral_basica, item_leite):
    dieta_oral_basica.adicionar_item(item_leite)
    
    assert dieta_oral_basica.quantidade_itens == 1


def test_erro_adicionar_item_com_restricao_proibida(dieta_oral_basica, item_leite):
    dieta_oral_basica.adicionar_restricao_proibida("lactose")
    
    with pytest.raises(ValueError, match="conflita com restrições da dieta"):
        dieta_oral_basica.adicionar_item(item_leite)


def test_erro_adicionar_item_multiplas_restricoes_conflitantes(dieta_oral_basica):
    dieta_oral_basica.adicionar_restricao_proibida("lactose")
    dieta_oral_basica.adicionar_restricao_proibida("soja")
    
    item_problema = ItemCardapio(
        "Iogurte de Soja",
        200.0,
        restricoes=["lactose", "soja"]
    )
    
    with pytest.raises(ValueError, match="conflita com restrições da dieta"):
        dieta_oral_basica.adicionar_item(item_problema)


def test_calcular_nutrientes_retorna_metadados(dieta_oral_completa):
    resultado = dieta_oral_completa.calcular_nutrientes()
    
    assert resultado["tipo_dieta"] == "Oral"
    assert resultado["textura"] == "pastosa"
    assert resultado["prescrito"]["numero_refeicoes"] == 6
    assert resultado["prescrito"]["tipo_refeicao"] == "janta"
    assert "restricoes" in resultado
    assert "quantidade_itens" in resultado


def test_calcular_nutrientes_sem_itens(dieta_oral_basica):
    resultado = dieta_oral_basica.calcular_nutrientes()
    
    assert resultado["quantidade_itens"] == 0


def test_calcular_nutrientes_com_itens(dieta_oral_basica, item_arroz, item_pao):
    dieta_oral_basica.adicionar_item(item_arroz)
    dieta_oral_basica.adicionar_item(item_pao)
    
    resultado = dieta_oral_basica.calcular_nutrientes()
    
    assert resultado["quantidade_itens"] == 2


def test_calcular_nutrientes_com_restricoes_proibidas(dieta_oral_basica):
    dieta_oral_basica.adicionar_restricao_proibida("lactose")
    dieta_oral_basica.adicionar_restricao_proibida("glúten")
    
    resultado = dieta_oral_basica.calcular_nutrientes()
    
    assert "glúten" in resultado["restricoes"]["proibidas"]
    assert "lactose" in resultado["restricoes"]["proibidas"]


def test_calcular_nutrientes_restricoes_ordenadas(dieta_oral_basica):
    dieta_oral_basica.adicionar_restricao_proibida("soja")
    dieta_oral_basica.adicionar_restricao_proibida("glúten")
    dieta_oral_basica.adicionar_restricao_proibida("lactose")
    
    resultado = dieta_oral_basica.calcular_nutrientes()
    restricoes = resultado["restricoes"]["proibidas"]
    
    assert restricoes == sorted(restricoes)


def test_validar_compatibilidade_dieta_valida(dieta_oral_basica):
    assert dieta_oral_basica.validar_compatibilidade() == True


def test_validar_compatibilidade_com_itens(dieta_oral_basica, item_arroz):
    dieta_oral_basica.adicionar_item(item_arroz)
    
    assert dieta_oral_basica.validar_compatibilidade() == True


def test_dieta_herda_auditoria_mixin(dieta_oral_basica):
    assert hasattr(dieta_oral_basica, 'criado_em')
    assert hasattr(dieta_oral_basica, 'atualizado_em')
    assert hasattr(dieta_oral_basica, 'usuario_responsavel')


def test_dieta_herda_status_dieta_mixin(dieta_oral_basica):
    assert hasattr(dieta_oral_basica, 'ativo')
    assert hasattr(dieta_oral_basica, 'data_inicio')
    assert hasattr(dieta_oral_basica, 'encerrar_dieta')


def test_encerrar_dieta(dieta_oral_basica):
    assert dieta_oral_basica.ativo == True
    
    dieta_oral_basica.encerrar_dieta()
    
    assert dieta_oral_basica.ativo == False
    assert dieta_oral_basica.data_fim is not None


def test_erro_encerrar_dieta_ja_encerrada(dieta_oral_basica):
    dieta_oral_basica.encerrar_dieta()
    
    with pytest.raises(ValueError, match="Dieta já foi encerrada"):
        dieta_oral_basica.encerrar_dieta()


def test_fluxo_completo_criacao_e_uso():
    dieta = DietaOral(
        textura="pastosa",
        numero_refeicoes=5,
        tipo_refeicao="janta",
        descricao="Dieta pós-cirurgia",
        usuario_responsavel="Dr. Carlos"
    )
    
    dieta.adicionar_restricao_proibida("glúten")
    dieta.adicionar_restricao_proibida("lactose")
    
    item_proibido = ItemCardapio("Pão", 80.0, restricoes=["glúten"])
    
    with pytest.raises(ValueError):
        dieta.adicionar_item(item_proibido)
    
    item_permitido = ItemCardapio("Arroz", 200.0)
    dieta.adicionar_item(item_permitido)
    
    assert dieta.quantidade_itens == 1
    assert dieta.tem_restricao_proibida("glúten")
    assert dieta.tem_restricao_proibida("lactose")
    
    resultado = dieta.calcular_nutrientes()
    assert resultado["tipo_dieta"] == "Oral"
    assert resultado["quantidade_itens"] == 1
    assert len(resultado["restricoes"]["proibidas"]) == 2


def test_fluxo_alterar_restricoes_dinamicamente():
    dieta = DietaOral("normal", 3, "almoço")
    
    dieta.adicionar_restricao_proibida("lactose")
    assert dieta.tem_restricao_proibida("lactose")
    
    item_leite = ItemCardapio("Leite", 250.0, restricoes=["lactose"])
    with pytest.raises(ValueError):
        dieta.adicionar_item(item_leite)
    
    dieta.remover_restricao_proibida("lactose")
    assert not dieta.tem_restricao_proibida("lactose")
    
    dieta.adicionar_item(item_leite)
    assert dieta.quantidade_itens == 1