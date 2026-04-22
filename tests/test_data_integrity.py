import pytest
from modules.data import BANCO_FILTROS, BANCO_BOMBAS_TT, DIAMETROS_TUBULACAO

def test_banco_filtros_integrity():
    for filtro in BANCO_FILTROS:
        assert "modelo" in filtro
        assert "volume_6h" in filtro
        assert filtro["volume_6h"] > 0
        assert "modelo_motobomba" in filtro

def test_banco_bombas_integrity():
    for bomba in BANCO_BOMBAS_TT:
        assert "modelo" in bomba
        assert "potencia_cv" in bomba
        assert bomba["potencia_cv"] > 0
        # Pelo menos um ponto de vazão deve ser definido
        vazoes = [v for k, v in bomba.items() if k.startswith("vazao_") and v is not None]
        assert len(vazoes) > 0

def test_diametros_tubulacao_integrity():
    for ext, int_val in DIAMETROS_TUBULACAO.items():
        assert ext > int_val
        assert int_val > 0
