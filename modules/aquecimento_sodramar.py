"""
Módulo de Dimensionamento de Aquecimento Sodramar
Replica fielmente a lógica da Planilha de Dimensionamento Sodramar 2022 (Rev. Nov/2023)
"""

import streamlit as st
import math

# ─────────────────────────────────────────────────────────────────────────────
# 1. TABELAS DE DADOS (hardcoded conforme a planilha)
# ─────────────────────────────────────────────────────────────────────────────

# Dados climáticos por região (aba DIMENSIONAMENTO linhas 26-28 / aba REGIÃO)
# Estrutura: { codigo: (nome, fator_aberta, fator_fechada, t_inverno, t_verao) }
REGIOES = {
    1: ("QUENTE", 3/11,        0.374,        19.0, 24.0),
    2: ("FRIO",   0.4375,      11/15,         11.0, 20.0),
    3: ("MÉDIO",  11/26.733,   11/14,         15.6, 22.0),
}
# Nota: fator_aberta região 3 = 0.411764... = 11/26.733 (extraído da planilha)
REGIOES[3] = ("MÉDIO", 0.411764705882353, 11/14, 15.6, 22.0)

# Tabela de perda de calor base por m² (aba FATOR linhas 3-19)
# Estrutura: { temp_agua: (medio, frio, quente) }  — BTU/m²
FATOR_PERDA_BASE = {
    25: (650,        994.44,       343),
    26: (770.83,     1119.44,      458),
    27: (902.80,     1251.39,      579),
    28: (961.11,     1319.44,      642),
    29: (1095.83,    1461.11,      772),
    30: (1238.89,    1611.11,      908),
    31: (1388.89,    1768.06,      1053),
    32: (1545.83,    1933.33,      1206),
    33: (1629.17,    2019.44,      1283),
    34: (1800.00,    2198.61,      1449),
    35: (1980.56,    2387.50,      1622),
    36: (2102.0833,  2505.4167,    1806.7917),
    37: (2297.4583,  2710.0833,    2000.9167),
    38: (2399.3333,  2816.8333,    2102.1667),
    39: (2611.9167,  3039.5833,    2313.375),
    40: (2837.00,    3275.4583,    2537.00),
    41: (3075.4583,  3525.25,      2773.9167),
}

# Fator de velocidade do vento (aba FATOR linhas 40-43)
# Estrutura: { velocidade_km_h: fator }
FATOR_VENTO = {
    0.1: 0.70,
    1.5: 1.00,
    3.0: 1.27167630057803,
    4.5: 1.51878612716763,
}

# Fator de incidência solar (aba FATOR linhas 40-60, colunas H-J)
# Estrutura: { incidencia_%: fator }
FATOR_SOLAR = {
    100: 1.0,
    95:  1.08899566473988,
    90:  1.0742774566474,
    85:  1.14073699421965,
    80:  1.0985549132948,
    75:  1.08395953757225,
    70:  1.06936416184971,
    65:  1.08164739884393,
    60:  1.09393063583815,
    55:  1.07756502890173,
    50:  1.06119942196532,
    45:  1.10068641618497,
    40:  1.14017341040462,
    35:  1.15173410404624,
    30:  1.16329479768786,
    25:  1.17485549132948,
    20:  1.1864161849711,
    15:  1.19869942196532,
    10:  1.21098265895954,
    5:   1.22254335260116,
    0:   1.23410404624277,
}

# Fator de redução com capa (aba FATOR linhas 40-56, colunas M-N)
# Estrutura: { horas_capa: fator_reducao }
FATOR_CAPA = {
    0:  1.002,
    1:  0.9705,
    2:  0.939,
    3:  0.9075,
    4:  0.876,
    5:  0.8445,
    6:  0.813,
    7:  0.7815,
    8:  0.75,
    9:  0.7185,
    10: 0.687,
    11: 0.6555,
    12: 0.624,
    13: 0.5925,
    14: 0.561,
    15: 0.5295,
    16: 0.498,
}

# Tabela COP por região × temperatura da água (aba MÁQUINAS linhas 19-25)
# Estrutura: { temp_agua: (quente, frio, medio) }
COP_TABLE = {
    25: (5.0,  4.64, 5.1),
    26: (5.0,  4.57, 5.0),
    27: (4.9,  4.49, 4.9),
    28: (4.9,  4.45, 4.9),
    29: (4.8,  4.38, 4.8),
    30: (4.7,  4.30, 4.7),
    31: (4.6,  4.23, 4.7),
    32: (4.6,  4.15, 4.6),
    33: (4.5,  4.12, 4.6),
    34: (4.45, 4.05, 4.5),
    35: (4.4,  3.97, 4.4),
    36: (4.3,  3.80, 4.3),
    37: (4.2,  3.80, 4.2),
    38: (4.2,  3.70, 4.1),
    39: (4.1,  3.70, 4.1),
    40: (4.0,  3.60, 4.0),
    41: (3.9,  3.50, 3.9),
}

# Catálogo de modelos: { nome: (capacidade_frio, capacidade_medio, capacidade_quente, potencia_kw) }
# Capacidades em BTU/h. Potência em kW (tabela nominal da planilha)
MODELOS_CATALOGO = {
    "TH10":              (19225.6,      22067.2,      22645.2,      0.8),
    "SD/TH25/INVERTER":  (30446.62144,  34946.72128,  35862.07098,  1.5),
    "SD/TH40/INVERTER":  (43257.6,      49651.2,      50951.7,      1.7),
    "SD/TH60/INVERTER":  (51668.8,      59305.6,      60858.975,    2.8),
    "SD/TH80/INVERTER":  (73779.048,    77751.387,    84513.681,    3.5),
    "SD105":             (73779.048,    77751.387,    84513.681,    4.75),
    "SD130":             (96041.16,     111030.06,    113067.0,     6.2),
    "SD160":             (106029.24,    122577.19,    124826.0,     7.5),   # 110447.334*0.96
    "SD180":             (137966.72,    145393.09,    158040.58,    9.1),   # SD105*1.87
    "2SD105":            (147558.096,   155502.774,   169027.362,   9.5),
    "SD105+SD130":       (169820.208,   188781.447,   197580.681,   10.95),
    "2SD130":            (192082.32,    222060.12,    226134.0,     12.4),
    "3SD105":            (221337.144,   233254.161,   253541.043,   14.25),
    "SD130+SD160":       (206488.494,   238714.629,   243094.05,    13.7),
    "2SD160":            (212058.48,    245154.38,    249652.0,     15.0),
    "SD160+SD180":       (243996.2604,  267972.27993, 282866.55147, 16.6),
    "2SD180":            (275933.63952, 290790.18738, 316081.16694, 18.2),
    "4SD105":            (295116.192,   311005.548,   338054.724,   19.0),
    "3SD130":            (288123.48,    333090.18,    339201.0,     18.6),
    "3SD160":            (318087.72,    367731.57,    374478.0,     22.5),
    "5SD105":            (368895.24,    388756.935,   422568.405,   23.75),
    "3SD180":            (413900.45928, 436185.28107, 474121.75041, 27.3),
    "4SD160":            (424116.96,    490308.76,    499304.0,     30.0),
    "4SD180":            (551867.27904, 581580.37476, 632162.33388, 36.4),
    "5SD160":            (530146.2,     612885.95,    624130.0,     37.5),
    "5SD180":            (689834.0988,  726975.46845, 790202.91735, 45.5),
    "6SD160":            (636174.44,    735463.14,    748956.0,     45.0),
    "6SD180":            (827800.91856, 872370.56214, 948243.50082, 54.6),
    "7SD160":            (742202.68,    857040.33,    873782.0,     52.5),
    "7SD180":            (965767.73832, 1017765.65583,1106284.08429,63.7),
    "8SD160":            (848230.92,    978617.52,    998608.0,     60.0),
    "9SD160":            (954259.16,    1100194.71,   1123434.0,    67.5),
    "8SD180":            (1103734.55808,1163160.74952,1264324.66776,72.8),
    "10SD160":           (1060287.4,    1221771.9,    1248260.0,    75.0),
    "9SD180":            (1241701.37784,1308555.84321,1422365.25123,81.9),
    "11SD160":           (1166315.64,   1343349.09,   1373086.0,    82.5),
    "10SD180":           (1379668.1976, 1453950.9369, 1580405.8347, 91.0),
    "12SD160":           (1272343.88,   1464926.28,   1497912.0,    90.0),
    "11SD180":           (1517635.01736,1599346.03059,1738446.41817,100.1),
    "13SD160":           (1378372.12,   1586503.47,   1622738.0,    97.5),
    "12SD180":           (1655601.83712,1744741.12428,1896487.00164,109.2),
    "14SD160":           (1484400.36,   1708080.66,   1747564.0,    105.0),
    "13SD180":           (1793568.65688,1890136.21797,2054527.58511,118.3),
    "15SD160":           (1590428.6,    1829657.85,   1872390.0,    112.5),
    "14SD180":           (1931535.47664,2035531.31166,2212568.16858,127.4),
    "16SD160":           (1696456.84,   1951235.04,   1997216.0,    120.0),
    "17SD160":           (1802485.08,   2072812.23,   2122042.0,    127.5),
    "18SD160":           (1908513.32,   2194389.42,   2246868.0,    135.0),
    "19SD160":           (2014541.56,   2315966.61,   2371694.0,    142.5),
    "20SD160":           (2120569.8,    2437543.8,    2496520.0,    150.0),
    "21SD160":           (2226598.04,   2559120.99,   2621346.0,    157.5),
    "22SD160":           (2332626.28,   2680698.18,   2746172.0,    165.0),
    "23SD160":           (2438654.52,   2802275.37,   2870998.0,    172.5),
    "24SD160":           (2544682.76,   2923852.56,   2995824.0,    180.0),
    "25SD160":           (2650711.0,    3045429.75,   3120650.0,    187.5),
    "26SD160":           (2756739.24,   3167006.94,   3245476.0,    195.0),
    "27SD160":           (2862767.48,   3288584.13,   3370302.0,    202.5),
    "28SD160":           (2968795.72,   3410161.32,   3495128.0,    210.0),
    "29SD160":           (3074823.96,   3531738.51,   3619954.0,    217.5),
    "30SD160":           (3180852.2,    3653315.7,    3744780.0,    225.0),
}

# Ordem de preferência dos modelos (do menor para o maior)
ORDEM_MODELOS = [
    "TH10", "SD/TH25/INVERTER", "SD/TH40/INVERTER", "SD/TH60/INVERTER",
    "SD/TH80/INVERTER", "SD105", "SD130", "SD160", "SD180",
    "2SD105", "SD105+SD130", "2SD130", "3SD105", "SD130+SD160",
    "2SD160", "SD160+SD180", "2SD180", "4SD105", "3SD130", "3SD160",
    "5SD105", "3SD180", "4SD160", "4SD180", "5SD160", "5SD180",
    "6SD160", "6SD180", "7SD160", "7SD180", "8SD160", "9SD160",
    "8SD180", "10SD160", "9SD180", "11SD160", "10SD180", "12SD160",
    "11SD180", "13SD160", "12SD180", "14SD160", "13SD180", "15SD160",
    "14SD180", "16SD160", "17SD160", "18SD160", "19SD160", "20SD160",
    "21SD160", "22SD160", "23SD160", "24SD160", "25SD160", "26SD160",
    "27SD160", "28SD160", "29SD160", "30SD160",
]


# ─────────────────────────────────────────────────────────────────────────────
# 2. FUNÇÕES DE CÁLCULO
# ─────────────────────────────────────────────────────────────────────────────

def _interpolar(tabela: dict, chave: float) -> float:
    """Interpolação linear entre dois pontos de uma tabela dict."""
    keys = sorted(tabela.keys())
    if chave <= keys[0]:
        return tabela[keys[0]]
    if chave >= keys[-1]:
        return tabela[keys[-1]]
    for i in range(len(keys) - 1):
        k0, k1 = keys[i], keys[i + 1]
        if k0 <= chave <= k1:
            t = (chave - k0) / (k1 - k0)
            v0 = tabela[k0] if not isinstance(tabela[k0], tuple) else tabela[k0]
            v1 = tabela[k1] if not isinstance(tabela[k1], tuple) else tabela[k1]
            if isinstance(v0, tuple):
                return tuple(v0[j] + t * (v1[j] - v0[j]) for j in range(len(v0)))
            return v0 + t * (v1 - v0)
    return tabela[keys[-1]]


def calcular_fator_vento(velocidade_kmh: float, ambiente: str) -> float:
    """Retorna o fator multiplicador pela velocidade do vento (FATOR!E45)."""
    if ambiente == "F":
        return FATOR_VENTO[0.1]  # fechado → sem vento
    return _interpolar(FATOR_VENTO, velocidade_kmh)


def calcular_fator_solar(incidencia_pct: float, ambiente: str) -> float:
    """Retorna o fator de incidência solar (FATOR!J62).
    Fórmula atualizada em 12/09/2018: 1.234 - incidencia/100 * 0.234
    Para ambiente fechado retorna 1.234 (sem influência solar).
    """
    if ambiente == "F":
        return 1.234
    incidencia = max(0.0, min(100.0, incidencia_pct))
    return 1.234 - (incidencia / 100.0) * 0.234


def calcular_perda_base(temp_agua: float, regiao: int) -> float:
    """Retorna a perda de calor base (BTU/m²) por lookup na tabela FATOR."""
    idx_regiao = {1: 2, 2: 1, 3: 0}  # quente=col2, frio=col1, medio=col0
    col = idx_regiao[regiao]
    resultado = _interpolar(FATOR_PERDA_BASE, temp_agua)
    return resultado[col] if isinstance(resultado, tuple) else resultado


def calcular_fator_capa(horas_capa: int) -> float:
    """Retorna o fator de redução com uso de capa (FATOR!O57)."""
    horas = max(0, min(16, int(round(horas_capa))))
    return FATOR_CAPA.get(horas, 1.002)


def calcular_energia_dissipada(
    largura: float,
    comprimento: float,
    temp_agua: float,
    regiao: int,
    ambiente: str,
    incidencia_solar: float,
    velocidade_vento: float,
    horas_capa: int,
) -> dict:
    """
    Replica a lógica da aba FATOR — calcula a energia dissipada pela piscina (BTU/h).

    Fórmula principal (FATOR!E37):
        E37 = E34 * E35 * F36 * J168
        onde:
            E34 = fator_incidencia * E32  (FATOR INCIDÊNCIA)
            E32 = fator_vento * E30       (FATOR VELOCIDADE)
            E30 = perda_sem_capa * fator_capa  (COM CAPA)
            E35 = área da piscina
            F36 = L31 = fator aberta/fechada (1 se aberto, 1 se fechado)
            J168 = J161 * J162 = (região válida?) * (ambiente válido?) = 1
    """
    area = largura * comprimento

    # Perda base sem capa (BTU/m²) — FATOR!E28 = SUM(D23:F23)
    perda_base = calcular_perda_base(temp_agua, regiao)

    # Fator capa → perda com capa (FATOR!E30 = E28 * O57)
    fator_capa = calcular_fator_capa(horas_capa)
    perda_com_capa = perda_base * fator_capa

    # Fator velocidade do vento (FATOR!E45 → E32 = E45 * E30)
    fator_vento = calcular_fator_vento(velocidade_vento, ambiente)
    perda_pos_vento = fator_vento * perda_com_capa

    # Fator incidência solar (FATOR!J62 → E34 = J62 * E32)
    fator_solar = calcular_fator_solar(incidencia_solar, ambiente)
    perda_pos_solar = fator_solar * perda_pos_vento

    # F36 (aberta/fechada): L31 = J31 + K31
    # J31 = 1 se aberto, K31 = 1 se fechado → L31 = 1 sempre
    fator_ambiente = 1.0

    # J168 = J161 * J162 — validação de entrada (sempre 1 com inputs corretos)
    j168 = 1.0

    energia_dissipada_btu_h = perda_pos_solar * area * fator_ambiente * j168

    return {
        "area_m2": area,
        "perda_base_btu_m2": perda_base,
        "fator_capa": fator_capa,
        "fator_vento": fator_vento,
        "fator_solar": fator_solar,
        "energia_dissipada_btu_h": energia_dissipada_btu_h,
        "energia_dissipada_kcal_h": energia_dissipada_btu_h / 3.97,
        "energia_dissipada_kw": energia_dissipada_btu_h / 3412.0,
    }


def selecionar_modelo_automatico(energia_necessaria_btu_h: float, regiao: int) -> tuple:
    """
    Percorre os modelos em ordem crescente e retorna o menor que:
      1) Tem capacidade >= energia necessária (cobre a demanda)
      2) Opera <= 17 horas/dia no inverno (MÁQUINAS!F74: se >17h = não atende)

    Replica a lógica de cascata das linhas 10-13 + validação F74 da aba MÁQUINAS.

    Returns: (nome_modelo, capacidade_btu_h, potencia_kw) ou (None, 0, 0)
    """
    idx_regiao = {1: 2, 2: 0, 3: 1}  # quente=2, frio=0, medio=1
    col = idx_regiao[regiao]

    for nome in ORDEM_MODELOS:
        if nome not in MODELOS_CATALOGO:
            continue
        caps = MODELOS_CATALOGO[nome]
        capacidade = caps[col]
        if capacidade < energia_necessaria_btu_h:
            continue
        # Verifica critério de horas: horas_dia = energia_hora * 24 / capacidade <= 17
        horas_dia = energia_necessaria_btu_h * 24.0 / capacidade
        if horas_dia <= 17.0:
            return (nome, capacidade, caps[3])
    return (None, 0, 0)


def calcular_cop(temp_agua: float, regiao: int) -> float:
    """Retorna o COP real por lookup na tabela da aba MÁQUINAS (linhas 19-25)."""
    idx_regiao = {1: 0, 2: 1, 3: 2}  # quente=0, frio=1, medio=2
    col = idx_regiao[regiao]
    resultado = _interpolar(COP_TABLE, temp_agua)
    return resultado[col] if isinstance(resultado, tuple) else resultado


def calcular_dimensionamento(inputs: dict) -> dict:
    """
    Função principal — replica todo o fluxo da aba DIMENSIONAMENTO.
    Recebe um dict com os inputs e retorna todos os resultados calculados.
    """
    largura         = inputs["largura"]
    comprimento     = inputs["comprimento"]
    profundidade    = inputs["profundidade"]
    temp_agua       = inputs["temp_agua"]
    regiao          = inputs["regiao"]
    ambiente        = inputs["ambiente"]
    incidencia      = inputs["incidencia_solar"]
    velocidade_vento = inputs["velocidade_vento"]
    horas_capa      = inputs["horas_capa"]
    custo_kwh       = inputs["custo_kwh"]
    custo_gn_m3     = inputs["custo_gn_m3"]
    modo            = inputs.get("modo", "A")  # A=automático, M=manual
    modelo_manual   = inputs.get("modelo_manual", None)

    # ── Geometria ──────────────────────────────────────────────────────────
    volume_litros = largura * comprimento * profundidade * 1000
    area_m2 = largura * comprimento

    # ── Dados climáticos da região ─────────────────────────────────────────
    nome_regiao, f_aberta, f_fechada, t_inverno, t_verao = REGIOES[regiao]

    # ── Energia dissipada ──────────────────────────────────────────────────
    fator_result = calcular_energia_dissipada(
        largura, comprimento, temp_agua, regiao,
        ambiente, incidencia, velocidade_vento, horas_capa,
    )
    energia_btu_h  = fator_result["energia_dissipada_btu_h"]
    energia_kcal_h = fator_result["energia_dissipada_kcal_h"]
    energia_kw     = fator_result["energia_dissipada_kw"]

    # Energia dissipada por mês (BTU) — DIMENSIONAMENTO!D54
    energia_mes_btu = energia_btu_h * 24 * 31

    # ── Seleção do modelo ──────────────────────────────────────────────────
    if modo == "A":
        nome_modelo, cap_btu_h, pot_kw_nominal = selecionar_modelo_automatico(energia_btu_h, regiao)
    else:
        nome_modelo = modelo_manual
        if nome_modelo and nome_modelo in MODELOS_CATALOGO:
            idx = {1: 2, 2: 0, 3: 1}[regiao]
            cap_btu_h = MODELOS_CATALOGO[nome_modelo][idx]
            pot_kw_nominal = MODELOS_CATALOGO[nome_modelo][3]
        else:
            nome_modelo, cap_btu_h, pot_kw_nominal = None, 0, 0

    # Validação de dimensionamento
    if nome_modelo is None or cap_btu_h == 0:
        return {
            "erro": "Nenhum modelo do catálogo atende a demanda calculada. "
                    "Verifique os parâmetros de entrada.",
            "energia_btu_h": energia_btu_h,
            "energia_kw": energia_kw,
        }

    # ── COP e consumo elétrico real ─────────────────────────────────────────
    cop_real = calcular_cop(temp_agua, regiao)
    consumo_eletrico_kw = cap_btu_h / cop_real / 3412.0   # kW real com COP

    # Potência em kcal/h (DIMENSIONAMENTO!D37 = D34/3.97)
    cap_kcal_h = cap_btu_h / 3.97

    # ── Horas de funcionamento ─────────────────────────────────────────────
    # Inverno: D60 = D54 / D33 / 31  (energia_mes / cap_kcal_h / 31)
    cap_kcal_mes = cap_kcal_h  # capacidade horária
    horas_inverno = energia_mes_btu / (cap_btu_h * 31) if cap_btu_h > 0 else 0

    # Verão: fator de verão da região
    fator_verao = f_aberta if ambiente == "A" else f_fechada
    horas_verao = horas_inverno * fator_verao

    # ── Verificação de sanidade (MÁQUINAS!C74) ─────────────────────────────
    equipamento_atende = horas_inverno <= 17.0

    # ── Velocidade e tempo de aquecimento ──────────────────────────────────
    # Velocidade: 0.43 × potência_kW × 1000 / volume_litros  (°C/h)
    velocidade_aq = 0.43 * (cap_btu_h / 3412.0) * 1000 / volume_litros if volume_litros > 0 else 0
    tempo_1grau = 1.0 / velocidade_aq if velocidade_aq > 0 else 0

    # Tempo aquecimento inicial verão (DIMENSIONAMENTO!D50)
    delta_t = temp_agua - t_verao
    if horas_capa == 0:
        tempo_aq_inicial = 2.33 * (volume_litros / 1000) * delta_t / (cap_btu_h / 3412.0) if cap_btu_h > 0 else 0
    else:
        tempo_aq_inicial = 2.33 * 0.75 * (volume_litros / 1000) * delta_t / (cap_btu_h / 3412.0) if cap_btu_h > 0 else 0

    # Potência do 1° aquecimento (kW)
    pot_1aq_kw = tempo_aq_inicial * consumo_eletrico_kw if tempo_aq_inicial > 0 else 0

    # ── Custos mensais ──────────────────────────────────────────────────────
    # Resistência elétrica convencional (concorrência, rendimento 80%)
    custo_resistencia = energia_kw * horas_inverno * 30 * custo_kwh / 0.8

    # Bomba de calor — inverno
    custo_inv = consumo_eletrico_kw * horas_inverno * custo_kwh * 31
    # Bomba de calor — verão
    custo_ver = consumo_eletrico_kw * horas_verao * custo_kwh * 31
    # Média mensal
    custo_medio = (custo_inv + custo_ver) / 2

    # Economia
    economia = custo_resistencia - custo_inv

    # Gás natural
    custo_gn = (energia_mes_btu / 9400) * 1.18 * custo_gn_m3
    consumo_m3_gn = (energia_mes_btu / 10294) * 1.18

    # Custo 1° aquecimento
    custo_1aq = pot_1aq_kw * custo_kwh if pot_1aq_kw > 0 else 0

    return {
        # Dados gerais
        "nome_regiao": nome_regiao,
        "t_inverno_c": t_inverno,
        "t_verao_c": t_verao,
        "volume_litros": volume_litros,
        "area_m2": area_m2,
        # Energia dissipada
        "energia_btu_h": energia_btu_h,
        "energia_kcal_h": energia_kcal_h,
        "energia_kw": energia_kw,
        "energia_mes_btu": energia_mes_btu,
        "fator_capa": fator_result["fator_capa"],
        "fator_vento": fator_result["fator_vento"],
        "fator_solar": fator_result["fator_solar"],
        # Modelo selecionado
        "modelo": nome_modelo,
        "capacidade_btu_h": cap_btu_h,
        "capacidade_kcal_h": cap_kcal_h,
        "capacidade_kw": cap_btu_h / 3412.0,
        "potencia_nominal_kw": pot_kw_nominal,
        # Performance
        "cop_real": cop_real,
        "consumo_eletrico_kw": consumo_eletrico_kw,
        "horas_inverno": horas_inverno,
        "horas_verao": horas_verao,
        "equipamento_atende": equipamento_atende,
        # Aquecimento
        "velocidade_aquecimento_c_h": velocidade_aq,
        "tempo_1grau_h": tempo_1grau,
        "tempo_aq_inicial_h": tempo_aq_inicial,
        "potencia_1aq_kw": pot_1aq_kw,
        # Custos
        "custo_resistencia_mes": custo_resistencia,
        "custo_bomba_inverno": custo_inv,
        "custo_bomba_verao": custo_ver,
        "custo_medio_mensal": custo_medio,
        "economia_mensal": economia,
        "custo_gn_mes": custo_gn,
        "consumo_gn_m3": consumo_m3_gn,
        "custo_1aq": custo_1aq,
        "erro": None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. INTERFACE STREAMLIT
# ─────────────────────────────────────────────────────────────────────────────

def run():
    st.title("🌡️ Dimensionamento de Aquecimento Sodramar")
    st.markdown(
        "Replica fielmente a **Planilha de Dimensionamento Sodramar 2022** (Rev. Nov/2023)."
    )

    # ── Entradas do usuário ────────────────────────────────────────────────
    st.subheader("📋 Dados da Piscina e do Cliente")

    col1, col2 = st.columns(2)
    with col1:
        largura     = st.number_input("Largura da piscina (m)", min_value=0.5, max_value=50.0, value=6.0, step=0.1)
        comprimento = st.number_input("Comprimento da piscina (m)", min_value=0.5, max_value=200.0, value=12.0, step=0.1)
        profundidade = st.number_input("Profundidade média (m)", min_value=0.3, max_value=5.0, value=1.3, step=0.1)
        temp_agua   = st.number_input("Temperatura desejada da água (°C)", min_value=25, max_value=41, value=30, step=1)
    with col2:
        regiao      = st.selectbox("Região climática", options=[1, 2, 3],
                                   format_func=lambda x: {1: "1 – Quente", 2: "2 – Frio", 3: "3 – Médio"}[x],
                                   index=2)
        ambiente    = st.radio("Ambiente", options=["A", "F"],
                               format_func=lambda x: "Aberto" if x == "A" else "Fechado",
                               horizontal=True)
        custo_kwh   = st.number_input("Custo do kW/hora (R$)", min_value=0.01, max_value=5.0, value=0.28, step=0.01, format="%.4f")
        custo_gn    = st.number_input("Custo do m³ de gás natural (R$)", min_value=0.0, max_value=20.0, value=3.40, step=0.1)

    st.subheader("☀️ Condições Ambientais")
    col3, col4 = st.columns(2)
    with col3:
        incidencia  = st.select_slider(
            "Incidência solar (%)",
            options=list(range(0, 105, 5)),
            value=100,
        )
        velocidade_vento = st.select_slider(
            "Velocidade do vento",
            options=[0.1, 1.5, 3.0, 4.5],
            format_func=lambda x: {0.1: "Sem vento (0.1 km/h)", 1.5: "Fraco (1.5 km/h)",
                                   3.0: "Médio (3.0 km/h)", 4.5: "Forte (4.5 km/h)"}[x],
            value=1.5,
        )
        if ambiente == "F":
            st.info("ℹ️ Em ambiente fechado, vento e incidência solar são desconsiderados.")
    with col4:
        horas_capa  = st.slider("Horas diárias com capa térmica", min_value=0, max_value=16, value=0)
        st.caption(f"Fator de redução com capa: **{calcular_fator_capa(horas_capa):.4f}**")

    st.subheader("⚙️ Forma de Dimensionamento")
    modo = st.radio("Seleção do modelo", options=["A", "M"],
                    format_func=lambda x: "Automática (recomendado)" if x == "A" else "Manual",
                    horizontal=True)

    modelo_manual = None
    if modo == "M":
        modelo_manual = st.selectbox("Modelo escolhido", options=ORDEM_MODELOS)

    # ── Cálculo ────────────────────────────────────────────────────────────
    if st.button("🔢 Calcular Dimensionamento", type="primary", use_container_width=True):
        inputs = {
            "largura": largura,
            "comprimento": comprimento,
            "profundidade": profundidade,
            "temp_agua": float(temp_agua),
            "regiao": regiao,
            "ambiente": ambiente,
            "incidencia_solar": float(incidencia),
            "velocidade_vento": velocidade_vento,
            "horas_capa": horas_capa,
            "custo_kwh": custo_kwh,
            "custo_gn_m3": custo_gn,
            "modo": modo,
            "modelo_manual": modelo_manual,
        }
        res = calcular_dimensionamento(inputs)
        _exibir_resultados(res, inputs)


def _exibir_resultados(res: dict, inputs: dict):
    """Renderiza os resultados do dimensionamento."""

    if res.get("erro"):
        st.error(f"⚠️ {res['erro']}")
        if "energia_btu_h" in res:
            st.metric("Energia necessária", f"{res['energia_btu_h']:,.0f} BTU/h")
        return

    # ── Banner de validação ────────────────────────────────────────────────
    if res["equipamento_atende"]:
        st.success(f"✅ **Equipamento Dimensionado** — Modelo: **{res['modelo']}**")
    else:
        st.error(
            f"⚠️ **ATENÇÃO** — O modelo **{res['modelo']}** opera por mais de 17h/dia no inverno "
            f"({res['horas_inverno']:.1f}h/dia). Considere um modelo maior."
        )

    # ── Modelo e capacidade ────────────────────────────────────────────────
    st.subheader("🏭 Equipamento Selecionado")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Modelo", res["modelo"])
    c2.metric("Capacidade", f"{res['capacidade_btu_h']:,.0f} BTU/h")
    c3.metric("Potência elétrica nominal", f"{res['potencia_nominal_kw']:.2f} kW")
    c4.metric("COP real", f"{res['cop_real']:.2f}")

    # ── Dados da piscina ───────────────────────────────────────────────────
    st.subheader("🏊 Dados da Piscina")
    ca, cb, cc = st.columns(3)
    ca.metric("Volume", f"{res['volume_litros']:,.0f} L")
    cb.metric("Área", f"{res['area_m2']:,.1f} m²")
    cc.metric(f"Região: {res['nome_regiao']}",
              f"Inv: {res['t_inverno_c']}°C  |  Ver: {res['t_verao_c']}°C")

    # ── Energia dissipada ──────────────────────────────────────────────────
    st.subheader("⚡ Energia Dissipada pela Piscina")
    d1, d2, d3 = st.columns(3)
    d1.metric("BTU/h", f"{res['energia_btu_h']:,.0f}")
    d2.metric("kcal/h", f"{res['energia_kcal_h']:,.0f}")
    d3.metric("kW", f"{res['energia_kw']:.2f}")

    with st.expander("🔍 Detalhes dos fatores de correção"):
        e1, e2, e3 = st.columns(3)
        e1.metric("Fator de capa", f"{res['fator_capa']:.4f}")
        e2.metric("Fator de vento", f"{res['fator_vento']:.4f}")
        e3.metric("Fator solar", f"{res['fator_solar']:.4f}")

    # ── Funcionamento ──────────────────────────────────────────────────────
    st.subheader("⏱️ Funcionamento do Equipamento")
    f1, f2, f3 = st.columns(3)
    f1.metric("Consumo elétrico real", f"{res['consumo_eletrico_kw']:.2f} kW")
    f2.metric("Horas/dia no inverno", f"{res['horas_inverno']:.1f} h")
    f3.metric("Horas/dia no verão", f"{res['horas_verao']:.1f} h")

    g1, g2, g3 = st.columns(3)
    g1.metric("Velocidade de aquecimento", f"{res['velocidade_aquecimento_c_h']:.4f} °C/h")
    g2.metric("Tempo p/ aquecer 1°C", f"{res['tempo_1grau_h']:.2f} h")
    g3.metric("Tempo 1° aquecimento (verão)", f"{res['tempo_aq_inicial_h']:.1f} h")

    # ── Análise de custos ──────────────────────────────────────────────────
    st.subheader("💰 Análise de Custos Mensais")
    h1, h2, h3 = st.columns(3)
    h1.metric("Bomba de calor (inverno)", f"R$ {res['custo_bomba_inverno']:,.2f}")
    h2.metric("Bomba de calor (verão)",   f"R$ {res['custo_bomba_verao']:,.2f}")
    h3.metric("Média mensal",             f"R$ {res['custo_medio_mensal']:,.2f}")

    i1, i2, i3 = st.columns(3)
    i1.metric("Resistência elétrica (80%)", f"R$ {res['custo_resistencia_mes']:,.2f}")
    i2.metric("Gás natural (mensal)",       f"R$ {res['custo_gn_mes']:,.2f}")
    i3.metric("Economia Sodramar vs. resistência",
              f"R$ {res['economia_mensal']:,.2f}",
              delta=f"{res['economia_mensal']:,.2f}" if res['economia_mensal'] > 0 else None,
              delta_color="normal")

    with st.expander("ℹ️ Memória de cálculo resumida"):
        st.markdown(f"""
| Parâmetro | Valor |
|---|---|
| Energia dissipada | `{res['energia_btu_h']:,.0f} BTU/h` |
| Energia dissipada (mês) | `{res['energia_mes_btu']:,.0f} BTU` |
| Capacidade do modelo | `{res['capacidade_btu_h']:,.0f} BTU/h` |
| Capacidade do modelo (kcal/h) | `{res['capacidade_kcal_h']:,.0f} kcal/h` |
| COP real | `{res['cop_real']:.2f}` |
| Consumo elétrico real | `{res['consumo_eletrico_kw']:.2f} kW` |
| Volume da piscina | `{res['volume_litros']:,.0f} L` |
| Custo 1° aquecimento | `R$ {res['custo_1aq']:,.2f}` |
| Consumo de GN (m³/mês) | `{res['consumo_gn_m3']:.2f} m³` |

**Fórmulas aplicadas:**
- Energia dissipada: `perda_base × fator_capa × fator_vento × fator_solar × área`
- Horas/dia inverno: `energia_BTU_mês ÷ capacidade_BTU_h ÷ 31`
- Velocidade aquecimento: `0.43 × potência_kW × 1000 ÷ volume_L` (°C/h)
- Custo resistência: `energia_kW × horas × 30 × R$/kWh ÷ 0,8`
- Custo bomba: `consumo_real_kW × horas × R$/kWh × 31`
        """)