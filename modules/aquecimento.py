"""
Módulo de Dimensionamento de Aquecimento Sodramar
Replica a lógica da Planilha de Dimensionamento Sodramar 2022 (Rev. Nov/2023)
"""

import io
from datetime import datetime

import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ─────────────────────────────────────────────────────────────────────────────
# 1. TABELAS DE DADOS  (hardcoded conforme a planilha)
# ─────────────────────────────────────────────────────────────────────────────

# Dados climáticos por região
# { codigo: (nome, fator_aberta, fator_fechada, t_inverno, t_verao) }
REGIOES = {
    1: ("QUENTE", 3 / 11,               0.374,    19.0, 24.0),
    2: ("FRIO",   0.4375,               11 / 15,  11.0, 20.0),
    3: ("MÉDIO",  0.411764705882353,     11 / 14,  15.6, 22.0),
}

# Perda de calor base por m²  —  BTU/m²  (aba FATOR linhas 3-19)
# { temp_agua: (medio, frio, quente) }
FATOR_PERDA_BASE = {
    25: (650,         994.44,      343),
    26: (770.83,      1119.44,     458),
    27: (902.80,      1251.39,     579),
    28: (961.11,      1319.44,     642),
    29: (1095.83,     1461.11,     772),
    30: (1238.89,     1611.11,     908),
    31: (1388.89,     1768.06,     1053),
    32: (1545.83,     1933.33,     1206),
    33: (1629.17,     2019.44,     1283),
    34: (1800.00,     2198.61,     1449),
    35: (1980.56,     2387.50,     1622),
    36: (2102.0833,   2505.4167,   1806.7917),
    37: (2297.4583,   2710.0833,   2000.9167),
    38: (2399.3333,   2816.8333,   2102.1667),
    39: (2611.9167,   3039.5833,   2313.375),
    40: (2837.00,     3275.4583,   2537.00),
    41: (3075.4583,   3525.25,     2773.9167),
}

# Fator velocidade do vento  (aba FATOR linhas 40-43)
FATOR_VENTO = {
    0.1: 0.70,
    1.5: 1.00,
    3.0: 1.27167630057803,
    4.5: 1.51878612716763,
}

# Fator de reducao com capa  (aba FATOR linhas 40-56, colunas M-N)
FATOR_CAPA = {
    0: 1.002,  1: 0.9705, 2: 0.939,  3: 0.9075,
    4: 0.876,  5: 0.8445, 6: 0.813,  7: 0.7815,
    8: 0.750,  9: 0.7185, 10: 0.687, 11: 0.6555,
    12: 0.624, 13: 0.5925, 14: 0.561, 15: 0.5295,
    16: 0.498,
}

# COP por temperatura da agua  (aba MAQUINAS linhas 19-25)
# { temp_agua: (quente, frio, medio) }
# NOTA: T=31 e intencionalmente omitido. O HLOOKUP da planilha retorna o COP
# de T=30 para T=31 por imprecisao de ponto flutuante nos cabecalhos da tabela.
# Com busca floor (<=), T=31 cai para a chave T=30, replicando esse comportamento.
COP_TABLE = {
    25: (5.0,  4.64, 5.1),  26: (5.0,  4.57, 5.0),
    27: (4.9,  4.49, 4.9),  28: (4.9,  4.45, 4.9),
    29: (4.8,  4.38, 4.8),  30: (4.7,  4.30, 4.7),
    # 31 omitido — HLOOKUP retorna T=30 (floor) por quirk de float do Excel
    32: (4.6,  4.15, 4.6),  33: (4.5,  4.12, 4.6),
    34: (4.45, 4.05, 4.5),  35: (4.4,  3.97, 4.4),
    36: (4.3,  3.80, 4.3),  37: (4.2,  3.80, 4.2),
    38: (4.2,  3.70, 4.1),  39: (4.1,  3.70, 4.1),
    40: (4.0,  3.60, 4.0),  41: (3.9,  3.50, 3.9),
}

# Catalogo de modelos  { nome: (cap_frio, cap_medio, cap_quente, pot_kw_nominal) }
# Capacidades em BTU/h — conforme aba MAQUINAS linhas 3-6
MODELOS_CATALOGO = {
    # TH10 usa formula E*0.5*0.9: 19225.6*0.5*0.9=8651.52, 22067.2*0.5*0.9=9930.24, 22645.2*0.5*0.9=10190.34
    "TH10":              (8651.52,      9930.24,       10190.34,      0.8),
    "SD/TH25/INVERTER":  (19225.6,      22067.2,       22645.2,       1.5),
    "SD/TH40/INVERTER":  (30446.62144,  34946.72128,   35862.07098,   1.7),
    "SD/TH60/INVERTER":  (43257.6,      49651.2,       50951.7,       2.8),
    "SD/TH80/INVERTER":  (51668.8,      59305.6,       60858.975,     3.5),
    "SD105":             (73779.048,    77751.387,     84513.681,     4.75),
    "SD130":             (96041.16,     111030.06,     113067.0,      6.2),
    "SD160":             (106029.24,    122577.186,    124826.0,      7.5),
    "SD180":             (137966.72,    145393.09,     158040.58,     9.1),
    "2SD105":            (147558.096,   155502.774,    169027.362,    9.5),
    "SD105+SD130":       (169820.208,   188781.447,    197580.681,   10.95),
    "2SD130":            (192082.32,    222060.12,     226134.0,     12.4),
    "3SD105":            (221337.144,   233254.161,    253541.043,   14.25),
    "SD130+SD160":       (206488.494,   238714.629,    243094.05,    13.7),
    "2SD160":            (212058.48,    245154.372,    249652.0,     15.0),
    "SD160+SD180":       (243996.2604,  267972.27993,  282866.55147, 16.6),
    "2SD180":            (275933.63952, 290790.18738,  316081.16694, 18.2),
    "4SD105":            (295116.192,   311005.548,    338054.724,   19.0),
    "3SD130":            (288123.48,    333090.18,     339201.0,     18.6),
    "3SD160":            (318087.72,    367731.558,    374478.0,     22.5),
    "5SD105":            (368895.24,    388756.935,    422568.405,   23.75),
    "3SD180":            (413900.46,    436185.28,     474121.75,    27.3),
    "4SD160":            (424116.96,    490308.744,    499304.0,     30.0),
    "4SD180":            (551867.28,    581580.37,     632162.33,    36.4),
    "5SD160":            (530146.2,     612885.93,     624130.0,     37.5),
    "5SD180":            (689834.10,    726975.47,     790202.92,    45.5),
    "6SD160":            (636175.44,    735463.116,    748956.0,     45.0),
    "6SD180":            (827800.92,    872370.56,     948243.50,    54.6),
    "7SD160":            (742203.68,    858040.302,    873782.0,     52.5),
    "7SD180":            (965767.74,    1017765.66,    1106284.08,   63.7),
    "8SD160":            (848231.92,    980617.488,    998608.0,     60.0),
    "9SD160":            (954260.16,    1103194.674,   1123434.0,    67.5),
    "8SD180":            (1103734.56,   1163160.75,    1264324.67,   72.8),
    "10SD160":           (1060288.4,    1225771.86,    1248260.0,    75.0),
    "9SD180":            (1241701.38,   1308555.84,    1422365.25,   81.9),
    "11SD160":           (1166316.64,   1348349.046,   1373086.0,    82.5),
    "10SD180":           (1379668.20,   1453950.94,    1580405.83,   91.0),
    "12SD160":           (1272344.88,   1470926.232,   1497912.0,    90.0),
    "11SD180":           (1517635.02,   1599346.03,    1738446.42,  100.1),
    "13SD160":           (1378372.12,   1593503.418,   1622738.0,    97.5),
    "12SD180":           (1655601.84,   1744741.12,    1896487.00,  109.2),
    "14SD160":           (1484401.36,   1716080.604,   1747564.0,   105.0),
    "13SD180":           (1793568.66,   1890136.22,    2054527.59,  118.3),
    "15SD160":           (1590429.6,    1838657.79,    1872390.0,   112.5),
    "14SD180":           (1931535.48,   2035531.31,    2212568.17,  127.4),
    "16SD160":           (1696457.84,   1961234.976,   1997216.0,   120.0),
    "17SD160":           (1802486.08,   2083812.162,   2122042.0,   127.5),
    "18SD160":           (1908514.32,   2206389.348,   2246868.0,   135.0),
    "19SD160":           (2014542.56,   2328966.534,   2371694.0,   142.5),
    "20SD160":           (2120570.8,    2451543.72,    2496520.0,   150.0),
    "21SD160":           (2226599.04,   2574120.906,   2621346.0,   157.5),
    "22SD160":           (2332627.28,   2696698.092,   2746172.0,   165.0),
    "23SD160":           (2438655.52,   2819275.278,   2870998.0,   172.5),
    "24SD160":           (2544683.76,   2941852.464,   2995824.0,   180.0),
    "25SD160":           (2650712.0,    3064429.65,    3120650.0,   187.5),
    "26SD160":           (2756740.24,   3187006.836,   3245476.0,   195.0),
    "27SD160":           (2862768.48,   3309584.022,   3370302.0,   202.5),
    "28SD160":           (2968796.72,   3432161.208,   3495128.0,   210.0),
    "29SD160":           (3074824.96,   3554738.394,   3619954.0,   217.5),
    "30SD160":           (3180853.2,    3677315.58,    3744780.0,   225.0),
}

ORDEM_MODELOS = list(MODELOS_CATALOGO.keys())

# Capacidade NOMINAL e potência elétrica nominal por modelo (aba DIMENSIONAMENTO Q4:S69)
# Usados APENAS para exibição (D34, D35, D39, D42). Calculos usam MODELOS_CATALOGO.
# { nome: (nominal_btu_h, nominal_kw_eletrico) }
NOMINAL_CATALOGO = {
    "TH10":              (11800,   0.8),
    "SD/TH25/INVERTER":  (25500,   1.5),
    "SD/TH40/INVERTER":  (40000,   1.7),
    "SD/TH60/INVERTER":  (60000,   2.8),
    "SD/TH80/INVERTER":  (81000,   3.5),
    "SD105":             (110000,  4.75),
    "SD130":             (137000,  6.2),
    "SD160":             (168000,  7.5),
    "SD180":             (188000,  9.1),
    # Combinacoes: soma das nominais
    "2SD105":            (220000,  9.5),
    "SD105+SD130":       (247000,  10.95),
    "2SD130":            (274000,  12.4),
    "3SD105":            (330000,  14.25),
    "SD130+SD160":       (305000,  13.7),
    "2SD160":            (336000,  15.0),
    "SD160+SD180":       (356000,  16.6),
    "2SD180":            (376000,  18.2),
}


# ─────────────────────────────────────────────────────────────────────────────
# 2. FUNCOES AUXILIARES
# ─────────────────────────────────────────────────────────────────────────────

def _interpolar(tabela: dict, chave: float):
    keys = sorted(tabela.keys())
    if chave <= keys[0]:
        return tabela[keys[0]]
    if chave >= keys[-1]:
        return tabela[keys[-1]]
    for i in range(len(keys) - 1):
        k0, k1 = keys[i], keys[i + 1]
        if k0 <= chave <= k1:
            t = (chave - k0) / (k1 - k0)
            v0, v1 = tabela[k0], tabela[k1]
            if isinstance(v0, tuple):
                return tuple(v0[j] + t * (v1[j] - v0[j]) for j in range(len(v0)))
            return v0 + t * (v1 - v0)
    return tabela[keys[-1]]


# ─────────────────────────────────────────────────────────────────────────────
# 3. CALCULO DE ENERGIA DISSIPADA  (replica aba FATOR)
# ─────────────────────────────────────────────────────────────────────────────

def _fator_vento(velocidade_kmh: float, ambiente: str) -> float:
    """FATOR!E45 — fator multiplicador pela velocidade do vento."""
    if ambiente == "F":
        return FATOR_VENTO[0.1]
    return _interpolar(FATOR_VENTO, velocidade_kmh)


def _fator_solar(incidencia_pct: float, ambiente: str) -> float:
    """FATOR!J62 — formula atualizada 12/09/2018: 1.234 - incidencia/100 x 0.234."""
    if ambiente == "F":
        return 1.234
    return 1.234 - (max(0.0, min(100.0, incidencia_pct)) / 100.0) * 0.234


def _fator_capa(horas: int) -> float:
    """FATOR!O57 — fator de reducao de perdas com uso de capa."""
    return FATOR_CAPA.get(max(0, min(16, int(round(horas)))), 1.002)


def calcular_energia_dissipada(
    largura: float, comprimento: float, temp_agua: float,
    regiao: int, ambiente: str,
    incidencia_solar: float, velocidade_vento: float, horas_capa: int,
) -> dict:
    """
    Replica FATOR!E37 = E34 x E35 x F36 x J168

    Cadeia:
        E28 (BTU/m2) = perda_base(temp, regiao)
        E30 (BTU/m2) = E28 x fator_capa
        E32 (BTU/m2) = fator_vento x E30
        E34 (BTU/m2) = fator_solar x E32
        E35 (m2)     = area
        F36 = J168   = 1
        E37 (BTU/h)  = E34 x E35
    """
    idx = {1: 2, 2: 1, 3: 0}[regiao]   # quente=2, frio=1, medio=0
    raw = _interpolar(FATOR_PERDA_BASE, temp_agua)
    perda_base = raw[idx] if isinstance(raw, tuple) else raw

    fc = _fator_capa(horas_capa)
    fv = _fator_vento(velocidade_vento, ambiente)
    fs = _fator_solar(incidencia_solar, ambiente)

    energia_btu_h = perda_base * fc * fv * fs * (largura * comprimento)

    return {
        "area_m2":           largura * comprimento,
        "perda_base_btu_m2": perda_base,
        "fator_capa":        fc,
        "fator_vento":       fv,
        "fator_solar":       fs,
        "energia_btu_h":     energia_btu_h,
        "energia_kcal_h":    energia_btu_h / 3.97,
        "energia_kw":        energia_btu_h / 3412.0,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 4. SELECAO DO MODELO  (replica aba MAQUINAS)
# ─────────────────────────────────────────────────────────────────────────────

def selecionar_modelo(energia_btu_h: float, regiao: int) -> tuple:
    """
    Menor modelo tal que:
      (a) capacidade >= energia necessaria
      (b) horas/dia no inverno <= 17  (MAQUINAS!F74)
    Returns: (nome, capacidade_btu_h, potencia_kw_nominal)
    """
    col = {1: 2, 2: 0, 3: 1}[regiao]
    for nome in ORDEM_MODELOS:
        cap = MODELOS_CATALOGO[nome][col]
        if cap >= energia_btu_h and (energia_btu_h * 24.0 / cap) <= 17.0:
            return (nome, cap, MODELOS_CATALOGO[nome][3])
    return (None, 0.0, 0.0)


def _cop(temp_agua: float, regiao: int) -> float:
    """
    COP real por regiao x temperatura (MAQUINAS linhas 19-25).
    Replica HLOOKUP(A25, C18:S24, 7) com approximate match (floor, <=).
    T=31 foi removido da tabela: o HLOOKUP da planilha retorna COP de T=30
    para T=31 por imprecisao de ponto flutuante no Excel.
    Para T=30 o match exato e encontrado e retorna COP=4.7 corretamente.
    """
    col = {1: 0, 2: 1, 3: 2}[regiao]
    keys = sorted(COP_TABLE.keys())
    cop_key = next((k for k in reversed(keys) if k <= temp_agua), keys[0])
    r = COP_TABLE[cop_key]
    return r[col] if isinstance(r, tuple) else r


# ─────────────────────────────────────────────────────────────────────────────
# 5. DIMENSIONAMENTO COMPLETO  (replica aba DIMENSIONAMENTO)
# ─────────────────────────────────────────────────────────────────────────────

def calcular_dimensionamento(inputs: dict) -> dict:
    """
    Executa todo o fluxo da planilha e retorna os resultados calculados.
    """
    larg  = inputs["largura"]
    comp  = inputs["comprimento"]
    prof  = inputs["profundidade"]
    t_agu = inputs["temp_agua"]
    reg   = inputs["regiao"]
    amb   = inputs["ambiente"]
    sol   = inputs["incidencia_solar"]
    vent  = inputs["velocidade_vento"]
    capa  = inputs["horas_capa"]
    kwh   = inputs["custo_kwh"]
    gn    = inputs["custo_gn_m3"]
    modo  = inputs.get("modo", "A")
    mdl_m = inputs.get("modelo_manual", None)

    # Geometria
    volume_l = larg * comp * prof * 1000
    area_m2  = larg * comp

    # Clima da regiao
    nome_reg, f_ab, f_fec, t_inv, t_ver = REGIOES[reg]

    # Energia dissipada  (aba FATOR)
    fator   = calcular_energia_dissipada(larg, comp, t_agu, reg, amb, sol, vent, capa)
    e_h     = fator["energia_btu_h"]     # BTU/h    D53
    e_mes   = e_h * 24 * 31              # BTU/mes  D54
    # D55 = D54/3.97  —  energia mensal em kcal
    # OBRIGATORIO usar e_mes_kcal nos calculos de Gas Natural
    e_mes_kcal = e_mes / 3.97            # kcal/mes D55

    # Selecao do modelo
    if modo == "A":
        nome, cap_h, pot_nom = selecionar_modelo(e_h, reg)
    else:
        nome = mdl_m
        if nome and nome in MODELOS_CATALOGO:
            col   = {1: 2, 2: 0, 3: 1}[reg]
            cap_h   = MODELOS_CATALOGO[nome][col]
            pot_nom = MODELOS_CATALOGO[nome][3]
        else:
            nome, cap_h, pot_nom = None, 0.0, 0.0

    if not nome or cap_h == 0:
        return {
            "erro": "Nenhum modelo do catalogo atende a demanda calculada. "
                    "Verifique os parametros de entrada.",
            "energia_btu_h": e_h,
        }

    # Capacidades do modelo  (D33..D38 na planilha)
    cap_kcal_h = cap_h / 3.97       # D38 = D33/3.97
    cap_kw     = (cap_h / 3.97) / 860  # D36 = D38/860 (planilha usa 3.97 e 860 separados)

    # COP e consumo eletrico real  (D41, D40)
    cop     = _cop(t_agu, reg)
    cons_kw = cap_kw / cop           # D40 = D36/D41

    # Horas de funcionamento  (D60, D61)
    h_inv = e_mes / cap_h / 31      # D60 = D54/D33/31
    # D61 = D60 * I27 — planilha hardcodeia referencia a linha 27 (FRIO=0.4375)
    # independente da regiao selecionada (comportamento fiel ao Excel)
    h_ver = h_inv * 0.4375          # D61 = D60 * I27 (fixo)

    atende = h_inv <= 17.0

    # Velocidade e tempos de aquecimento  (D58, D59, D50)
    vel_aq = 0.43 * cap_kw * 1000 / volume_l if volume_l > 0 else 0.0
    t_1c   = 1.0 / vel_aq if vel_aq > 0 else 0.0

    delta = t_agu - t_ver
    if capa == 0:
        # D50 sem capa: 2.33 x D28/1000 x (D11-D26) / D36
        t_ini = 2.33 * (volume_l / 1000) * delta / cap_kw if cap_kw > 0 else 0.0
    else:
        # D50 com capa: 2.33 x 0.75 x D28/1000 x (D11-D26) / D36
        t_ini = 2.33 * 0.75 * (volume_l / 1000) * delta / cap_kw if cap_kw > 0 else 0.0

    # Potencia e custo do 1 aquecimento  (D51, D52)
    pot_1aq   = t_ini * cons_kw
    custo_1aq = pot_1aq * kwh

    # ── CUSTOS MENSAIS ────────────────────────────────────────────────────────

    # D43 — Resistencia eletrica: usa cap_kw (D36), nao a dissipacao
    # D43 = D36 x D60 x 30 x D12 / 0.8
    custo_resist = cap_kw * h_inv * 30 * kwh / 0.8

    # D46 — Bomba de calor inverno: D40 x D60 x D12 x 31
    custo_inv = cons_kw * h_inv * kwh * 31

    # D49 — Bomba de calor verao: D61 x 31 x D40 x D12
    custo_ver = cons_kw * h_ver * kwh * 31

    # D45 — Media mensal: AVERAGE(D46, D49)
    custo_med = (custo_inv + custo_ver) / 2

    # D44 — Gas Natural: D55/9400 x 1.18 x D13
    #        D55 esta em kcal — NUNCA usar BTU aqui
    custo_gn_mes = (e_mes_kcal / 9400) * 1.18 * gn

    # D48 — Economia Sodramar: D44 - D46
    economia = custo_gn_mes - custo_inv

    # D47 — Consumo m3 GN: D55/10294 x 1.18
    #        D55 esta em kcal — NUNCA usar BTU aqui
    cons_m3_gn = (e_mes_kcal / 10294) * 1.18

    # Capacidades NOMINAIS (exibicao) — D34, D35, D39, D42
    nom = NOMINAL_CATALOGO.get(nome, (None, None))
    nom_btu     = nom[0]                                   # D34
    nom_kcal_h  = nom_btu / 3.97   if nom_btu else None   # D35
    nom_kw_nom  = nom[1]                                   # D39
    nom_kw_calc = nom_btu / 3412.0 if nom_btu else None   # D37
    nom_cop     = (nom_kw_calc / nom_kw_nom
                   if nom_btu and nom_kw_nom else None)    # D42

    return {
        "nome_regiao":         nome_reg,
        "t_inverno_c":         t_inv,
        "t_verao_c":           t_ver,
        "volume_litros":       volume_l,
        "area_m2":             area_m2,
        "energia_btu_h":       e_h,
        "energia_kcal_h":      fator["energia_kcal_h"],
        "energia_kw":          fator["energia_kw"],
        "energia_mes_btu":     e_mes,
        "energia_mes_kcal":    e_mes_kcal,
        "fator_capa":          fator["fator_capa"],
        "fator_vento":         fator["fator_vento"],
        "fator_solar":         fator["fator_solar"],
        "modelo":              nome,
        "capacidade_btu_h":    cap_h,
        "capacidade_kcal_h":   cap_kcal_h,
        "capacidade_kw":       cap_kw,
        "potencia_nominal_kw": pot_nom,
        "cop":                 cop,
        "consumo_eletrico_kw": cons_kw,
        "horas_inverno":       h_inv,
        "horas_verao":         h_ver,
        "equipamento_atende":  atende,
        "velocidade_aq_c_h":   vel_aq,
        "tempo_1grau_h":       t_1c,
        "tempo_aq_inicial_h":  t_ini,
        "potencia_1aq_kw":     pot_1aq,
        "custo_1aq":           custo_1aq,
        "custo_resistencia":   custo_resist,
        "custo_bomba_inverno": custo_inv,
        "custo_bomba_verao":   custo_ver,
        "custo_medio_mensal":  custo_med,
        "custo_gn_mes":        custo_gn_mes,
        "consumo_gn_m3":       cons_m3_gn,
        "economia_mensal":     economia,
        # Valores nominais (apenas exibicao — D34, D35, D39, D42 da planilha)
        "nominal_btu_h":       nom_btu,
        "nominal_kcal_h":      nom_kcal_h,
        "nominal_kw_eletrico": nom_kw_nom,
        "nominal_cop":         nom_cop,
        "erro":                None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 6. GERACAO DE PDF
# ─────────────────────────────────────────────────────────────────────────────

def _gerar_pdf(res: dict, inputs: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()

    AZUL  = colors.HexColor("#1a4e8a")
    CINZA = colors.HexColor("#f2f4f7")

    s_titulo = ParagraphStyle("titulo",  parent=styles["Title"],
                              textColor=AZUL, fontSize=15, spaceAfter=4)
    s_sub    = ParagraphStyle("sub",     parent=styles["Heading2"],
                              textColor=AZUL, fontSize=10, spaceBefore=10, spaceAfter=4)
    s_normal = ParagraphStyle("normal",  parent=styles["Normal"], fontSize=9)
    s_small  = ParagraphStyle("small",   parent=styles["Normal"], fontSize=8,
                              textColor=colors.grey)

    def _tabela(dados, col_widths=None):
        t = Table(dados, colWidths=col_widths, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  AZUL),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, CINZA]),
            ("GRID",          (0, 0), (-1, -1), 0.4, colors.lightgrey),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        return t

    story = []

    # Cabecalho
    story.append(Paragraph("Dimensionamento de Aquecimento - Sodramar", s_titulo))
    story.append(Paragraph(
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}   |   "
        f"Modelo: <b>{res['modelo']}</b>",
        s_small,
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=AZUL, spaceAfter=8))

    # Status
    if res["equipamento_atende"]:
        status = f"<font color='#1e7c3a'><b>Equipamento Dimensionado: {res['modelo']}</b></font>"
    else:
        status = (
            f"<font color='#b30000'><b>ATENCAO: modelo opera "
            f"{res['horas_inverno']:.1f}h/dia no inverno (limite: 17h). "
            f"Considere um modelo maior.</b></font>"
        )
    story.append(Paragraph(status, s_normal))
    story.append(Spacer(1, 8))

    # Dados de entrada
    story.append(Paragraph("Dados de Entrada", s_sub))
    story.append(_tabela(
        [
            ["Parametro", "Valor", "Unidade"],
            ["Dimensoes",
             f"{inputs['largura']:.1f} x {inputs['comprimento']:.1f} x {inputs['profundidade']:.1f}",
             "m"],
            ["Volume",                  f"{res['volume_litros']:,.0f}",      "L"],
            ["Area",                    f"{res['area_m2']:,.1f}",             "m2"],
            ["Temperatura desejada",    f"{inputs['temp_agua']}",             "graus C"],
            ["Regiao",                  f"{inputs['regiao']} - {res['nome_regiao']}", ""],
            ["Ambiente",                "Aberto" if inputs['ambiente']=="A" else "Fechado", ""],
            ["Incidencia solar",        f"{inputs['incidencia_solar']}",      "%"],
            ["Velocidade do vento",     f"{inputs['velocidade_vento']}",      "km/h"],
            ["Horas com capa",          f"{inputs['horas_capa']}",            "h/dia"],
            ["Custo kWh",               f"R$ {inputs['custo_kwh']:.4f}",      ""],
            ["Custo Gas Natural",       f"R$ {inputs['custo_gn_m3']:.2f}",    "R$/m3"],
        ],
        col_widths=[8 * cm, 6 * cm, 3 * cm],
    ))
    story.append(Spacer(1, 6))

    # Energia dissipada
    story.append(Paragraph("Energia Dissipada pela Piscina", s_sub))
    story.append(_tabela(
        [
            ["Parametro", "Valor"],
            ["Energia dissipada",       f"{res['energia_btu_h']:,.0f} BTU/h"],
            ["Energia dissipada",       f"{res['energia_kcal_h']:,.0f} kcal/h"],
            ["Energia dissipada",       f"{res['energia_kw']:.2f} kW"],
            ["Energia mensal (BTU)",    f"{res['energia_mes_btu']:,.0f} BTU"],
            ["Energia mensal (kcal)",   f"{res['energia_mes_kcal']:,.0f} kcal"],
            ["Fator de capa",           f"{res['fator_capa']:.4f}"],
            ["Fator de vento",          f"{res['fator_vento']:.4f}"],
            ["Fator solar",             f"{res['fator_solar']:.4f}"],
        ],
        col_widths=[9 * cm, 8 * cm],
    ))
    story.append(Spacer(1, 6))

    # Equipamento
    story.append(Paragraph("Equipamento Selecionado", s_sub))
    nom_btu_pdf = res.get("nominal_btu_h")
    nom_cop_pdf = res.get("nominal_cop")
    nom_kw_pdf  = res.get("nominal_kw_eletrico")
    equip_rows = [["Parametro", "Valor"]]
    equip_rows.append(["Modelo", res["modelo"]])
    if nom_btu_pdf:
        equip_rows.append(["Capacidade nominal (catalogo)", f"{nom_btu_pdf:,.0f} BTU/h"])
        equip_rows.append(["Capacidade nominal (catalogo)", f"{nom_btu_pdf/3.97:,.0f} kcal/h"])
        equip_rows.append(["Potencia eletrica nominal",     f"{nom_kw_pdf:.2f} kW"])
        equip_rows.append(["COP nominal (D42)",             f"{nom_cop_pdf:.1f}"])
    equip_rows.append(["Capacidade real (regiao)",   f"{res['capacidade_btu_h']:,.0f} BTU/h"])
    equip_rows.append(["Capacidade real (regiao)",   f"{res['capacidade_kcal_h']:,.0f} kcal/h"])
    equip_rows.append(["COP real (MAQUINAS!B24)",    f"{res['cop']:.2f}"])
    equip_rows.append(["Consumo eletrico real",      f"{res['consumo_eletrico_kw']:.2f} kW"])
    equip_rows.append(["Horas/dia - inverno",        f"{res['horas_inverno']:.1f} h"])
    equip_rows.append(["Horas/dia - verao",          f"{res['horas_verao']:.1f} h"])
    story.append(_tabela(equip_rows, col_widths=[9 * cm, 8 * cm]))
    story.append(Spacer(1, 6))

    # Aquecimento
    story.append(Paragraph("Tempos de Aquecimento", s_sub))
    story.append(_tabela(
        [
            ["Parametro", "Valor"],
            ["Velocidade de aquecimento",    f"{res['velocidade_aq_c_h']:.4f} graus C/h"],
            ["Tempo para aquecer 1 grau C",  f"{res['tempo_1grau_h']:.2f} h"],
            ["Tempo 1o aquecimento (verao)", f"{res['tempo_aq_inicial_h']:.1f} h"],
            ["Potencia no 1o aquecimento",   f"{res['potencia_1aq_kw']:.2f} kW"],
            ["Custo do 1o aquecimento",      f"R$ {res['custo_1aq']:,.2f}"],
        ],
        col_widths=[9 * cm, 8 * cm],
    ))
    story.append(Spacer(1, 6))

    # Custos
    story.append(Paragraph("Analise de Custos Mensais", s_sub))
    story.append(_tabela(
        [
            ["Referencia", "Custo Mensal"],
            ["Bomba de calor (inverno)",     f"R$ {res['custo_bomba_inverno']:,.2f}"],
            ["Bomba de calor (verao)",       f"R$ {res['custo_bomba_verao']:,.2f}"],
            ["Media mensal (bomba)",         f"R$ {res['custo_medio_mensal']:,.2f}"],
            ["Resistencia eletrica (80%)",   f"R$ {res['custo_resistencia']:,.2f}"],
            ["Gas natural",                  f"R$ {res['custo_gn_mes']:,.2f}"],
            ["Consumo gas natural",          f"{res['consumo_gn_m3']:.2f} m3/mes"],
            ["Economia vs. gas natural",     f"R$ {res['economia_mensal']:,.2f}"],
        ],
        col_widths=[9 * cm, 8 * cm],
    ))

    # Rodape
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    story.append(Paragraph(
        "Bombas de calor Sodramar: temperatura ambiente minima 7 graus C, "
        "umidade relativa minima 30%, temperatura maxima da agua 40 graus C.",
        s_small,
    ))

    doc.build(story)
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# 7. INTERFACE STREAMLIT
# ─────────────────────────────────────────────────────────────────────────────

def run():
    st.title("💧 Aquecimento")
    st.caption("Dimensionamento de bomba de calor — Sodramar 2022 (Rev. Nov/2023)")

    # ── Entradas ──────────────────────────────────────────────────────────────
    with st.expander("Dados da Piscina e do Cliente", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            largura      = st.number_input("Largura (m)",               min_value=1.0,  max_value=50.0,  value=6.0,  step=1.0)
            comprimento  = st.number_input("Comprimento (m)",           min_value=1.0,  max_value=200.0, value=12.0, step=1.0)
            profundidade = st.number_input("Profundidade media (m)",    min_value=1.0,  max_value=5.0,   value=1.0,  step=1.0)
            temp_agua    = st.number_input("Temperatura desejada (C)",  min_value=25,   max_value=41,    value=30,   step=1)
        with c2:
            regiao = st.selectbox(
                "Regiao climatica",
                options=[1, 2, 3],
                format_func=lambda x: {1: "1 - Quente", 2: "2 - Frio", 3: "3 - Medio"}[x],
                index=2,
            )
            ambiente = st.radio(
                "Ambiente", ["A", "F"],
                format_func=lambda x: "Aberto" if x == "A" else "Fechado",
                horizontal=True,
            )
            custo_kwh = st.number_input("Custo kWh (R$)",            min_value=0.0, max_value=10.0,  value=1.0, step=1.0, format="%.4f")
            custo_gn  = st.number_input("Custo Gas Natural (R$/m3)", min_value=0.0, max_value=50.0,  value=1.0, step=1.0, format="%.2f")

    with st.expander("Condicoes Ambientais", expanded=True):
        c3, c4 = st.columns(2)
        with c3:
            incidencia = st.select_slider(
                "Incidencia solar (%)",
                options=list(range(0, 105, 5)),
                value=100,
            )
            velocidade_vento = st.select_slider(
                "Velocidade do vento",
                options=[0.1, 1.5, 3.0, 4.5],
                format_func=lambda x: {
                    0.1: "Sem vento (0,1 km/h)",
                    1.5: "Fraco (1,5 km/h)",
                    3.0: "Medio (3,0 km/h)",
                    4.5: "Forte (4,5 km/h)",
                }[x],
                value=1.5,
            )
            if ambiente == "F":
                st.info("ℹ️ Ambiente fechado: vento e incidencia solar sao desconsiderados.")
        with c4:
            horas_capa = st.slider("Horas diarias com capa termica", 0, 16, 0)
            fc = _fator_capa(horas_capa)
            st.caption(f"Fator com capa: **{fc:.4f}** ({(1 - fc) * 100:.1f}% de reducao de perdas)")

    with st.expander("Selecao do Modelo", expanded=False):
        modo = st.radio(
            "Modo de selecao", ["A", "M"],
            format_func=lambda x: "Automatica" if x == "A" else "Manual",
            horizontal=True,
        )
        modelo_manual = None
        if modo == "M":
            modelo_manual = st.selectbox("Modelo", ORDEM_MODELOS)

    # ── Botao calcular ─────────────────────────────────────────────────────────
    if st.button("Calcular Dimensionamento", type="primary", use_container_width=True):
        inputs = dict(
            largura=largura, comprimento=comprimento, profundidade=profundidade,
            temp_agua=float(temp_agua), regiao=regiao, ambiente=ambiente,
            incidencia_solar=float(incidencia), velocidade_vento=velocidade_vento,
            horas_capa=horas_capa, custo_kwh=custo_kwh, custo_gn_m3=custo_gn,
            modo=modo, modelo_manual=modelo_manual,
        )
        st.session_state["aq_resultado"] = calcular_dimensionamento(inputs)
        st.session_state["aq_inputs"]    = inputs

    # ── Resultados ────────────────────────────────────────────────────────────
    if "aq_resultado" in st.session_state:
        _exibir_resultados(
            st.session_state["aq_resultado"],
            st.session_state["aq_inputs"],
        )


def _exibir_resultados(res: dict, inputs: dict):
    if res.get("erro"):
        st.error(f"⚠️ {res['erro']}")
        if "energia_btu_h" in res:
            st.metric("Energia necessaria", f"{res['energia_btu_h']:,.0f} BTU/h")
        return

    st.divider()

    # Banner de status
    if res["equipamento_atende"]:
        st.success(f"✅ Equipamento Dimensionado — **{res['modelo']}**")
    else:
        st.error(
            f"⚠️ O modelo **{res['modelo']}** opera {res['horas_inverno']:.1f}h/dia no inverno "
            f"(limite recomendado: 17h). Considere um modelo maior."
        )

    # Equipamento
    st.subheader("Equipamento Selecionado")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Modelo", res["modelo"])
    # Exibe capacidade NOMINAL (D34) se disponivel, caso contrario real (D33)
    nom_btu = res.get("nominal_btu_h")
    nom_cop = res.get("nominal_cop")
    nom_kw  = res.get("nominal_kw_eletrico")
    c2.metric(
        "Capacidade nominal",
        f"{nom_btu:,.0f} BTU/h" if nom_btu else f"{res['capacidade_btu_h']:,.0f} BTU/h",
    )
    c3.metric("Pot. eletrica nominal", f"{nom_kw:.2f} kW" if nom_kw else f"{res['potencia_nominal_kw']:.2f} kW")
    c4.metric(
        "COP nominal",
        f"{nom_cop:.1f}" if nom_cop else f"{res['cop']:.2f}",
    )

    with st.expander("Detalhes tecnicos do equipamento"):
        t1, t2, t3, t4 = st.columns(4)
        t1.metric("Capacidade real (regiao)", f"{res['capacidade_btu_h']:,.0f} BTU/h")
        t2.metric("Capacidade real", f"{res['capacidade_kcal_h']:,.0f} kcal/h")
        t3.metric("COP real (MAQUINAS!B24)", f"{res['cop']:.2f}")
        t4.metric("Consumo eletrico real", f"{res['consumo_eletrico_kw']:.2f} kW")

    with st.expander("Dados da piscina e regiao"):
        ca, cb, cc = st.columns(3)
        ca.metric("Volume",  f"{res['volume_litros']:,.0f} L")
        cb.metric("Area",    f"{res['area_m2']:,.1f} m2")
        cc.metric(
            f"Regiao {res['nome_regiao']}",
            f"Inv: {res['t_inverno_c']}C  |  Ver: {res['t_verao_c']}C",
        )

    # Energia dissipada
    st.subheader("Energia Dissipada")
    d1, d2, d3 = st.columns(3)
    d1.metric("BTU/h",  f"{res['energia_btu_h']:,.0f}")
    d2.metric("kcal/h", f"{res['energia_kcal_h']:,.0f}")
    d3.metric("kW",     f"{res['energia_kw']:.2f}")

    with st.expander("Fatores de correcao"):
        e1, e2, e3 = st.columns(3)
        e1.metric("Fator de capa",  f"{res['fator_capa']:.4f}")
        e2.metric("Fator de vento", f"{res['fator_vento']:.4f}")
        e3.metric("Fator solar",    f"{res['fator_solar']:.4f}")

    # Funcionamento
    st.subheader("Funcionamento do Equipamento")
    f1, f2, f3 = st.columns(3)
    f1.metric("Consumo eletrico real", f"{res['consumo_eletrico_kw']:.2f} kW")
    # Planilha exibe horas arredondadas para inteiro (internamente usa float)
    f2.metric("Horas/dia (inverno)",   f"{round(res['horas_inverno'])} h")
    f3.metric("Horas/dia (verao)",     f"{round(res['horas_verao'])} h")

    with st.expander("Tempos de aquecimento"):
        g1, g2, g3 = st.columns(3)
        g1.metric("Velocidade de aquecimento",  f"{res['velocidade_aq_c_h']:.4f} C/h")
        g2.metric("Tempo p/ aquecer 1 grau C",  f"{res['tempo_1grau_h']:.2f} h")
        g3.metric("Tempo 1o aquecimento",        f"{res['tempo_aq_inicial_h']:.1f} h")
        h1, h2, _ = st.columns(3)
        h1.metric("Potencia 1o aquecimento", f"{res['potencia_1aq_kw']:.2f} kW")
        h2.metric("Custo 1o aquecimento",    f"R$ {res['custo_1aq']:,.2f}")

    # Custos
    st.subheader("Analise de Custos Mensais")
    i1, i2, i3 = st.columns(3)
    i1.metric("Bomba de calor (inverno)", f"R$ {res['custo_bomba_inverno']:,.2f}")
    i2.metric("Bomba de calor (verao)",   f"R$ {res['custo_bomba_verao']:,.2f}")
    i3.metric("Media mensal",             f"R$ {res['custo_medio_mensal']:,.2f}")

    j1, j2, j3 = st.columns(3)
    j1.metric("Resistencia eletrica (80%)", f"R$ {res['custo_resistencia']:,.2f}")
    j2.metric("Gas natural",                f"R$ {res['custo_gn_mes']:,.2f}")
    j3.metric("Consumo GN",                 f"{res['consumo_gn_m3']:.2f} m3/mes")

    eco = res["economia_mensal"]
    st.metric(
        "Economia mensal (bomba vs. gas natural)",
        f"R$ {eco:,.2f}",
        delta=f"R$ {eco:,.2f}" if eco > 0 else None,
        delta_color="normal",
    )

    # Exportar PDF
    st.divider()
    col_pdf, _ = st.columns([2, 5])
    if col_pdf.button("Gerar relatorio PDF", use_container_width=True):
        pdf_bytes = _gerar_pdf(res, inputs)
        nome = f"Aquecimento_Sodramar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        col_pdf.download_button(
            label="Baixar PDF",
            data=pdf_bytes,
            file_name=nome,
            mime="application/pdf",
            use_container_width=True,
        )