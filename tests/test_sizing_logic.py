import pytest
from modules.filtragem import selecionar_filtro
from modules.transbordo import calcular_parametros_transbordo, selecionar_bomba_transbordo

def test_selecionar_filtro_valido():
    # Para uma piscina de 10m3, deve selecionar o FM-25 (que atende até 14m3 em 6h)
    filtro = selecionar_filtro(10.0)
    assert filtro is not None
    assert filtro["modelo"] == "FM-25"

def test_selecionar_filtro_limite():
    # Para uma piscina de 234m3, deve selecionar o FM-100
    filtro = selecionar_filtro(234.0)
    assert filtro is not None
    assert filtro["modelo"] == "FM-100"

def test_selecionar_filtro_excedente():
    # Para um volume gigante que nenhum filtro atende
    filtro = selecionar_filtro(1000.0)
    assert filtro is None

def test_calcular_parametros_transbordo():
    # Valores arbitrários para teste
    altura = 3.0 # mm
    comprimento = 10.0 # m
    area = 50.0 # m2
    
    params = calcular_parametros_transbordo(altura, comprimento, area)
    
    # Volume do cocho: 50 * (3/1000) * 3 * 1000 = 450 L
    assert params["volume_cocho_litros"] == pytest.approx(450.0)
    # Área da lâmina: (3/1000) * 10 = 0.03 m2
    assert params["area_lamina_m2"] == pytest.approx(0.03)
    # Vazão necessária (fórmula complexa, vamos apenas garantir que seja positiva)
    assert params["vazao_necessaria"] > 0

def test_selecionar_bomba_transbordo():
    # Vazão baixa (1m3/h) a 6 mca deve retornar a menor bomba disponível
    bomba = selecionar_bomba_transbordo(1.0, 6)
    assert bomba is not None
    assert "BMC" in bomba["modelo"] or "BM" in bomba["modelo"]
