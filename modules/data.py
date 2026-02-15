"""
Repositório Central de Dados e Constantes da Aplicação.

Este módulo contém:

- Constantes físicas (propriedades da água, gravidade)
- Bases de dados de equipamentos (Filtros, Bombas)
- Especificações de tubulação (Diâmetros, Fatores de atrito)
"""

# ==========================================
# CONSTANTES FÍSICAS
# ==========================================

GRAVIDADE = 9.81  # m/s²
VISCOSIDADE_AGUA_24C = 0.896e-6  # m²/s
RUGOSIDADE_PVC = 0.0000015  # m

# ==========================================
# DADOS DE TUBULAÇÃO (PVC)
# ==========================================

# Diâmetro Externo (mm) -> Diâmetro Interno (mm)
DIAMETROS_TUBULACAO = {
    25: 21.6,
    32: 27.8,
    40: 35.2,
    50: 44.0,
    60: 53.4,
    75: 66.6,
    85: 75.6,
    110: 97.8
}

CONEXOES_EQUIV = {
    "joelho 90º": {
        25: 1.2, 32: 1.5, 40: 2.0, 50: 3.2, 60: 3.4, 75: 3.7, 85: 3.9, 110: 4.3
    },
    "joelho 45º": {
        25: 0.5, 32: 0.7, 40: 1.0, 50: 1.3, 60: 1.5, 75: 1.7, 85: 1.8, 110: 1.9
    },
    "união": {
        25: 0.1, 32: 0.1, 40: 0.1, 50: 0.1, 60: 0.1, 75: 0.15, 85: 0.2, 110: 0.25
    },
    "Tê de passagem direta": {
        25: 0.8, 32: 0.9, 40: 1.5, 50: 2.2, 60: 2.3, 75: 2.4, 85: 2.5, 110: 2.6
    },
    "Tê de saída lateral": {
        32: 3.1, 40: 4.6, 50: 7.3, 60: 7.6, 75: 7.8, 85: 8.0, 110: 8.3
    },
    "registro esfera aberto": {
        25: 0.2, 32: 0.3, 40: 0.4, 50: 0.7, 60: 0.8, 75: 0.9, 85: 0.9, 110: 1.0
    },
    "curva 90º": {
        25: 0.5, 32: 0.6, 40: 0.7, 50: 1.2, 60: 1.3, 75: 1.4, 85: 1.5, 110: 1.6
    },
    "curva 45º": {
        25: 0.3, 32: 0.4, 40: 0.5, 50: 0.6, 60: 0.7, 75: 0.8, 85: 0.9, 110: 1.0
    }
}

# ==========================================
# BANCO DE DADOS DE EQUIPAMENTOS
# ==========================================

BANCO_FILTROS = [
    {
        "modelo": "FM-25",
        "volume_6h": 14,
        "volume_8h": 19,
        "carga_areia_kg": 18,
        "quant_sacos_25kg": 1,
        "diametro_mm": 335,
        "altura_mm": 583,
        "peso_bruto_com_areia_kg": 23.4,
        "peso_bruto_sem_areia_kg": 5.4,
        "modelo_motobomba": "BMC-25 M"
    },
    {
        "modelo": "FM-30",
        "volume_6h": 21,
        "volume_8h": 28,
        "carga_areia_kg": 25,
        "quant_sacos_25kg": 1,
        "diametro_mm": 325,
        "altura_mm": 735,
        "peso_bruto_com_areia_kg": 34.13,
        "peso_bruto_sem_areia_kg": 9.13,
        "modelo_motobomba": "BMC-25 M"
    },
    {
        "modelo": "FM-36",
        "volume_6h": 30,
        "volume_8h": 40,
        "carga_areia_kg": 40,
        "quant_sacos_25kg": 2,
        "diametro_mm": 380,
        "altura_mm": 772,
        "peso_bruto_com_areia_kg": 50.7,
        "peso_bruto_sem_areia_kg": 10.7,
        "modelo_motobomba": "BMC-33 M"
    },
    {
        "modelo": "FM-40",
        "volume_6h": 37,
        "volume_8h": 50,
        "carga_areia_kg": 65,
        "quant_sacos_25kg": 3,
        "diametro_mm": 430,
        "altura_mm": 835,
        "peso_bruto_com_areia_kg": 77.55,
        "peso_bruto_sem_areia_kg": 12.55,
        "modelo_motobomba": "BMC-50 M"
    },
    {
        "modelo": "FM-50",
        "volume_6h": 59,
        "volume_8h": 78,
        "carga_areia_kg": 125,
        "quant_sacos_25kg": 5,
        "diametro_mm": 525,
        "altura_mm": 930,
        "peso_bruto_com_areia_kg": 142.98,
        "peso_bruto_sem_areia_kg": 17.98,
        "modelo_motobomba": "BMC-75 M"
    },
    {
        "modelo": "FM-60 E",
        "volume_6h": 85,
        "volume_8h": 113,
        "carga_areia_kg": 150,
        "quant_sacos_25kg": 6,
        "diametro_mm": 650,
        "altura_mm": 860,
        "peso_bruto_com_areia_kg": 169.50,
        "peso_bruto_sem_areia_kg": 19.50,
        "modelo_motobomba": "BMC-100 M"
    },
    {
        "modelo": "FM-75 E",
        "volume_6h": 132,
        "volume_8h": 176,
        "carga_areia_kg": 225,
        "quant_sacos_25kg": 9,
        "diametro_mm": 770,
        "altura_mm": 1140,
        "peso_bruto_com_areia_kg": 253,
        "peso_bruto_sem_areia_kg": 28,
        "modelo_motobomba": "BMC-150 M"
    },
    {
        "modelo": "FM-100",
        "volume_6h": 234,
        "volume_8h": 312,
        "carga_areia_kg": 525,
        "quant_sacos_25kg": 21,
        "diametro_mm": 1120,
        "altura_mm": 1215,
        "peso_bruto_com_areia_kg": 579.8,
        "peso_bruto_sem_areia_kg": 54.8,
        "modelo_motobomba": "BM-300 T"
    }
]

# ==========================================
# BOMBAS – Linha BMC (monobloco)
# ==========================================
BANCO_BOMBAS_BMC = [
    {
        "modelo": "BMC-25",
        "potencia_cv": 0.25,
        "vazao_2_mca": 12.14,
        "vazao_4_mca": 11.47,
        "vazao_6_mca": 9.02,
        "vazao_8_mca": 7.28,
        "vazao_10_mca": None,
        "vazao_12_mca": None,
        "vazao_14_mca": None,
        "vazao_16_mca": None,
        "vazao_18_mca": None
    },
    {
        "modelo": "BMC-33",
        "potencia_cv": 0.33,
        "vazao_2_mca": None,
        "vazao_4_mca": 11.91,
        "vazao_6_mca": 9.44,
        "vazao_8_mca": 7.43,
        "vazao_10_mca": None,
        "vazao_12_mca": None,
        "vazao_14_mca": None,
        "vazao_16_mca": None,
        "vazao_18_mca": None
    },
    {
        "modelo": "BMC-50",
        "potencia_cv": 0.5,
        "vazao_2_mca": None,
        "vazao_4_mca": 12.77,
        "vazao_6_mca": 10.12,
        "vazao_8_mca": 8.03,
        "vazao_10_mca": 5.23,
        "vazao_12_mca": None,
        "vazao_14_mca": None,
        "vazao_16_mca": None,
        "vazao_18_mca": None
    },
    {
        "modelo": "BMC-75",
        "potencia_cv": 0.75,
        "vazao_2_mca": None,
        "vazao_4_mca": 16.26,
        "vazao_6_mca": 13.75,
        "vazao_8_mca": 12.24,
        "vazao_10_mca": 10.28,
        "vazao_12_mca": None,
        "vazao_14_mca": None,
        "vazao_16_mca": None,
        "vazao_18_mca": None
    },
    {
        "modelo": "BMC-100",
        "potencia_cv": 1.0,
        "vazao_2_mca": None,
        "vazao_4_mca": 19.88,
        "vazao_6_mca": 19.38,
        "vazao_8_mca": 16.71,
        "vazao_10_mca": 14.83,
        "vazao_12_mca": 13.25,
        "vazao_14_mca": 5.75,
        "vazao_16_mca": None,
        "vazao_18_mca": None
    },
    {
        "modelo": "BMC-150",
        "potencia_cv": 1.5,
        "vazao_2_mca": None,
        "vazao_4_mca": None,
        "vazao_6_mca": 26.79,
        "vazao_8_mca": 23.14,
        "vazao_10_mca": 22.77,
        "vazao_12_mca": 21.95,
        "vazao_14_mca": 18.63,
        "vazao_16_mca": 12.38,
        "vazao_18_mca": 4.46
    },
    {
        "modelo": "BMC-200",
        "potencia_cv": 2.0,
        "vazao_2_mca": None,
        "vazao_4_mca": None,
        "vazao_6_mca": 28.24,
        "vazao_8_mca": 27.11,
        "vazao_10_mca": 24.35,
        "vazao_12_mca": 20.94,
        "vazao_14_mca": 19.19,
        "vazao_16_mca": 15.92,
        "vazao_18_mca": 3.6
    }
]

# ==========================================
# BOMBAS – Linha BMU (ultra)
# ==========================================
BANCO_BOMBAS_BMU = [
    {
        "modelo": "BMU-200",
        "potencia_cv": 2.0,
        "vazao_2_mca": None,
        "vazao_4_mca": None,
        "vazao_6_mca": 40.0,
        "vazao_8_mca": 38.27,
        "vazao_10_mca": 36.55,
        "vazao_12_mca": 34.82,
        "vazao_14_mca": 31.36,
        "vazao_16_mca": 27.64,
        "vazao_18_mca": None
    },
    {
        "modelo": "BMU-300",
        "potencia_cv": 3.0,
        "vazao_2_mca": None,
        "vazao_4_mca": None,
        "vazao_6_mca": 44.4,
        "vazao_8_mca": 42.26,
        "vazao_10_mca": 40.16,
        "vazao_12_mca": 38.2,
        "vazao_14_mca": 36.6,
        "vazao_16_mca": 34.31,
        "vazao_18_mca": None
    },
    {
        "modelo": "BMU-400",
        "potencia_cv": 4.0,
        "vazao_2_mca": None,
        "vazao_4_mca": None,
        "vazao_6_mca": 54.0,
        "vazao_8_mca": 50.4,
        "vazao_10_mca": 46.8,
        "vazao_12_mca": 43.2,
        "vazao_14_mca": 38.4,
        "vazao_16_mca": 35.6,
        "vazao_18_mca": None
    }
]

# ==========================================
# BOMBAS – Linha BM (linha padrão)
# ==========================================
BANCO_BOMBAS_BM = [
    {
        "modelo": "BM-25",
        "potencia_cv": 0.25,
        "vazao_2_mca": 11.89,
        "vazao_4_mca": 11.24,
        "vazao_6_mca": 8.83,
        "vazao_8_mca": 7.13,
        "vazao_10_mca": None,
        "vazao_12_mca": None,
        "vazao_14_mca": None,
        "vazao_16_mca": None,
        "vazao_18_mca": None
    },
    {
        "modelo": "BM-33",
        "potencia_cv": 0.33,
        "vazao_2_mca": 12.07,
        "vazao_4_mca": 11.67,
        "vazao_6_mca": 9.95,
        "vazao_8_mca": 7.28,
        "vazao_10_mca": None,
        "vazao_12_mca": None,
        "vazao_14_mca": None,
        "vazao_16_mca": None,
        "vazao_18_mca": None
    },
    {
        "modelo": "BM-50",
        "potencia_cv": 0.5,
        "vazao_2_mca": None,
        "vazao_4_mca": 12.51,
        "vazao_6_mca": 9.91,
        "vazao_8_mca": 7.86,
        "vazao_10_mca": 5.12,
        "vazao_12_mca": None,
        "vazao_14_mca": None,
        "vazao_16_mca": None,
        "vazao_18_mca": None
    },
    {
        "modelo": "BM-75",
        "potencia_cv": 0.75,
        "vazao_2_mca": None,
        "vazao_4_mca": 15.93,
        "vazao_6_mca": 13.97,
        "vazao_8_mca": 11.99,
        "vazao_10_mca": 10.1,
        "vazao_12_mca": 6.9,
        "vazao_14_mca": None,
        "vazao_16_mca": None,
        "vazao_18_mca": None
    },
    {
        "modelo": "BM-100",
        "potencia_cv": 1.0,
        "vazao_2_mca": None,
        "vazao_4_mca": 19.48,
        "vazao_6_mca": 19.43,
        "vazao_8_mca": 16.37,
        "vazao_10_mca": 14.5,
        "vazao_12_mca": 13.0,
        "vazao_14_mca": 5.63,
        "vazao_16_mca": None,
        "vazao_18_mca": None
    },
    {
        "modelo": "BM-150",
        "potencia_cv": 1.5,
        "vazao_2_mca": None,
        "vazao_4_mca": 28.22,
        "vazao_6_mca": 26.25,
        "vazao_8_mca": 22.67,
        "vazao_10_mca": 22.3,
        "vazao_12_mca": 21.5,
        "vazao_14_mca": 18.3,
        "vazao_16_mca": 12.1,
        "vazao_18_mca": 4.4
    },
    {
        "modelo": "BM-200",
        "potencia_cv": 2.0,
        "vazao_2_mca": None,
        "vazao_4_mca": 31.17,
        "vazao_6_mca": 29.1,
        "vazao_8_mca": 28.24,
        "vazao_10_mca": 24.9,
        "vazao_12_mca": 20.9,
        "vazao_14_mca": 19.2,
        "vazao_16_mca": 15.9,
        "vazao_18_mca": 3.6
    },
    {
        "modelo": "BM-300",
        "potencia_cv": 3.0,
        "vazao_2_mca": None,
        "vazao_4_mca": None,
        "vazao_6_mca": 34.1,
        "vazao_8_mca": 32.14,
        "vazao_10_mca": 31.3,
        "vazao_12_mca": 29.8,
        "vazao_14_mca": 27.4,
        "vazao_16_mca": 20.6,
        "vazao_18_mca": 6.9
    }
]

# ==========================================
# BOMBAS – Linha BMGC (linha com maior pressão)
# ==========================================
BANCO_BOMBAS_BMGC = [
    {
        "modelo": "BMGC-25",
        "potencia_cv": 0.25,
        "vazao_2_mca": 11.9,
        "vazao_4_mca": 11.2,
        "vazao_6_mca": 8.8,
        "vazao_8_mca": 7.1,
        "vazao_10_mca": None,
        "vazao_12_mca": None,
        "vazao_14_mca": None,
        "vazao_16_mca": None,
        "vazao_18_mca": None
    },
    {
        "modelo": "BMGC-33",
        "potencia_cv": 0.33,
        "vazao_2_mca": None,
        "vazao_4_mca": 12.0,
        "vazao_6_mca": 9.2,
        "vazao_8_mca": 7.2,
        "vazao_10_mca": None,
        "vazao_12_mca": None,
        "vazao_14_mca": None,
        "vazao_16_mca": None,
        "vazao_18_mca": None
    },
    {
        "modelo": "BMGC-50",
        "potencia_cv": 0.5,
        "vazao_2_mca": None,
        "vazao_4_mca": 12.5,
        "vazao_6_mca": 9.9,
        "vazao_8_mca": 7.8,
        "vazao_10_mca": 5.1,
        "vazao_12_mca": None,
        "vazao_14_mca": None,
        "vazao_16_mca": None,
        "vazao_18_mca": None
    },
    {
        "modelo": "BMGC-75",
        "potencia_cv": 0.75,
        "vazao_2_mca": None,
        "vazao_4_mca": 15.9,
        "vazao_6_mca": 13.4,
        "vazao_8_mca": 11.9,
        "vazao_10_mca": 10.0,
        "vazao_12_mca": 6.9,
        "vazao_14_mca": None,
        "vazao_16_mca": None,
        "vazao_18_mca": None
    },
    {
        "modelo": "BMGC-100",
        "potencia_cv": 1.0,
        "vazao_2_mca": None,
        "vazao_4_mca": 19.4,
        "vazao_6_mca": 18.4,
        "vazao_8_mca": 16.3,
        "vazao_10_mca": 14.5,
        "vazao_12_mca": 12.9,
        "vazao_14_mca": 5.6,
        "vazao_16_mca": None,
        "vazao_18_mca": None
    }
]


# ==========================================
# BOMBAS – Lista combinada (para compatibilidade)
# ==========================================
BANCO_BOMBAS = BANCO_BOMBAS_BMC + BANCO_BOMBAS_BMU
BANCO_BOMBAS_TT = BANCO_BOMBAS_BMC + BANCO_BOMBAS_BMU + BANCO_BOMBAS_BM + BANCO_BOMBAS_BMGC