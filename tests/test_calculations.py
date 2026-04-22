import pytest
import numpy as np
from modules.calc_utils import calcular_fator_atrito, ajustar_curva_pchip, encontrar_interseccao_curvas

def test_calcular_fator_atrito_laminar():
    # Re < 2000 -> f = 64/Re
    re = 1000
    expected = 64 / re
    assert calcular_fator_atrito(re, 0.05) == pytest.approx(expected)

def test_calcular_fator_atrito_turbulento():
    # Re > 4000. Valores típicos para PVC
    re = 50000
    d_int = 0.05 # 50mm
    f = calcular_fator_atrito(re, d_int)
    # Fator de atrito para PVC em regime turbulento costuma ficar entre 0.015 e 0.03
    assert 0.01 < f < 0.05

def test_ajustar_curva_pchip():
    x = [0, 5, 10, 15]
    y = [10, 8, 5, 0]
    x_interp, y_interp, func = ajustar_curva_pchip(x, y, num_pontos=50)
    
    assert len(x_interp) == 50
    assert len(y_interp) == 50
    # O valor no ponto original deve ser aproximado (PCHIP passa pelos pontos)
    assert func(5) == pytest.approx(8)

def test_encontrar_interseccao_curvas():
    # Curva 1: y = 10 - x (reta descendente - ex: bomba)
    # Curva 2: y = x (reta ascendente - ex: sistema)
    # Interseção em x=5, y=5
    x_range = np.linspace(0, 10, 100)
    y_curva1 = 10 - x_range
    def func_curva2(x): return x
    
    interseccoes = encontrar_interseccao_curvas(x_range, y_curva1, func_curva2)
    
    assert len(interseccoes) == 1
    x_int, y_int = interseccoes[0]
    assert x_int == pytest.approx(5.0)
    assert y_int == pytest.approx(5.0)
