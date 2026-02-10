import pytest
from src.snh_project.core.diet import ItemCardapio

@pytest.fixture
def item_simples():
    return ItemCardapio("Arroz Branco", 200.0)


@pytest.fixture
def item_com_restricoes():
    return ItemCardapio(
        "Leite Integral",
        250.0,
        restricoes=["LACTOSE", "Proteína do Leite  "]
    )


def test_criar_item_valido_simples():
    item = ItemCardapio("Feijão Preto", 150.0)
    
    assert item.nome == "Feijão Preto"
    assert item.quantidade_gramas == 150.0
    assert item.restricoes == []


def test_criar_item_com_uma_restricao():
    item = ItemCardapio("Pão", 50.0, restricoes=["glúten"])
    
    assert item.nome == "Pão"
    assert item.quantidade_gramas == 50.0
    assert "glúten" in item.restricoes


def test_criar_item_com_multiplas_restricoes():
    item = ItemCardapio(
        "Chocolate",
        30.0,
        restricoes=["lactose", "soja", "glúten"]
    )
    
    assert len(item.restricoes) == 3
    assert "lactose" in item.restricoes
    assert "soja" in item.restricoes
    assert "glúten" in item.restricoes


def test_nome_com_espacos_extras_eh_normalizado():
    item = ItemCardapio("  Arroz Integral  ", 200.0)
    
    assert item.nome == "Arroz Integral"


def test_restricoes_sao_normalizadas_para_lowercase(item_com_restricoes):
    restricoes = item_com_restricoes.restricoes
    
    assert "lactose" in restricoes 
    assert "proteína do leite" in restricoes  
    assert "LACTOSE" not in restricoes 


def test_restricoes_com_espacos_extras_sao_limpas():
    item = ItemCardapio(
        "Queijo",
        100.0,
        restricoes=["  lactose  ", "caseína  "]
    )
    
    assert "lactose" in item.restricoes
    assert "caseína" in item.restricoes


def test_quantidade_gramas_aceita_float():
    item = ItemCardapio("Azeite", 10.5)
    
    assert item.quantidade_gramas == 10.5


def test_erro_nome_vazio():
    with pytest.raises(ValueError, match="Nome do item não pode ser vazio"):
        ItemCardapio("", 100.0)


def test_erro_nome_apenas_espacos():
    with pytest.raises(ValueError, match="Nome do item não pode ser vazio"):
        ItemCardapio("   ", 100.0)


def test_erro_quantidade_zero():
    with pytest.raises(ValueError, match="Quantidade deve ser maior que 0 gramas"):
        ItemCardapio("Sal", 0.0)


def test_erro_quantidade_negativa():
    with pytest.raises(ValueError, match="Quantidade deve ser maior que 0 gramas"):
        ItemCardapio("Açúcar", -50.0)


def test_nome_property_somente_leitura(item_simples):
    with pytest.raises(AttributeError):
        item_simples.nome = "Novo Nome" 


def test_quantidade_gramas_property_somente_leitura(item_simples):
    with pytest.raises(AttributeError):
        item_simples.quantidade_gramas = 999.0  


def test_restricoes_retorna_copia_nao_original(item_com_restricoes):
    restricoes_retornadas = item_com_restricoes.restricoes
    restricoes_retornadas.append("nova_restricao")
    
    assert "nova_restricao" not in item_com_restricoes.restricoes


def test_repr_contem_nome_e_quantidade():
    item = ItemCardapio("Café", 50.0, restricoes=["cafeína"])
    repr_str = repr(item)
    
    assert "Café" in repr_str
    assert "50" in repr_str or "50.0" in repr_str


def test_igualdade_por_nome():
    item1 = ItemCardapio("Arroz", 200.0)
    item2 = ItemCardapio("Arroz", 300.0)
    
    assert item1 == item2 


def test_desigualdade_por_nome():
    item1 = ItemCardapio("Arroz", 200.0)
    item2 = ItemCardapio("Feijão", 200.0) 
    
    assert item1 != item2


def test_igualdade_com_tipo_diferente():
    item = ItemCardapio("Arroz", 200.0)
    
    assert item != "Arroz" 
    assert item != 200.0   
    assert item != None     


def test_restricoes_none_vira_lista_vazia():
    item = ItemCardapio("Água", 500.0, restricoes=None)
    
    assert item.restricoes == []
    assert isinstance(item.restricoes, list)


def test_restricoes_lista_vazia_explicitamente():
    item = ItemCardapio("Sal", 5.0, restricoes=[])
    
    assert item.restricoes == []


def test_quantidade_muito_pequena():
    item = ItemCardapio("Pimenta", 0.1)
    
    assert item.quantidade_gramas == 0.1


def test_quantidade_muito_grande():
    item = ItemCardapio("Água", 5000.0)
    
    assert item.quantidade_gramas == 5000.0


def test_nome_com_caracteres_especiais():
    item = ItemCardapio("Café com Açúcar & Leite", 150.0)
    
    assert item.nome == "Café com Açúcar & Leite"


def test_restricoes_com_caracteres_especiais():
    item = ItemCardapio(
        "Pão Francês",
        80.0,
        restricoes=["glúten", "açúcar"]
    )
    
    assert "glúten" in item.restricoes
    assert "açúcar" in item.restricoes


def test_restricoes_duplicadas_sao_preservadas():
    item = ItemCardapio(
        "Item Teste",
        100.0,
        restricoes=["lactose", "lactose", "glúten"]
    )
    

    restricoes = item.restricoes
    assert restricoes.count("lactose") == 2



def test_uso_tipico_item_sem_restricoes():
    item = ItemCardapio("Arroz Integral", 250.0)
    
    assert item.nome == "Arroz Integral"
    assert item.quantidade_gramas == 250.0
    assert len(item.restricoes) == 0


def test_uso_tipico_item_com_restricoes():
    item = ItemCardapio(
        "Iogurte Natural",
        200.0,
        restricoes=["Lactose", "Proteína Animal"]
    )
 
    assert "lactose" in item.restricoes
    assert "proteína animal" in item.restricoes
    assert len(item.restricoes) == 2


def test_comparacao_multiplos_itens():
    arroz1 = ItemCardapio("Arroz", 100.0)
    arroz2 = ItemCardapio("Arroz", 200.0)
    feijao = ItemCardapio("Feijão", 100.0)
    
    assert arroz1 == arroz2 
    assert arroz1 != feijao  
    assert arroz2 != feijao  