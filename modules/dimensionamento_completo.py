# dimensionamento_completo.py
"""
Módulo de Dimensionamento Completo — Integração SketchUp → HidroCalc

Importa JSON exportado pela extensão HidroAnnotator do SketchUp e
alimenta automaticamente os módulos existentes de filtragem, transbordo,
hidromassagem e aquecimento, exibindo resultados consolidados.

NÃO modifica os módulos existentes — atua como adaptador.
"""

import json
import math
import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
from tracking import track_access
from modules.data import BANCO_FILTROS, BANCO_BOMBAS
from modules.aquecimento import calcular_dimensionamento as calc_aquecimento


# ─────────────────────────────────────────────────────────────────────────────
# 1. VALIDAÇÃO E PARSING DO JSON
# ─────────────────────────────────────────────────────────────────────────────

def parse_json(raw_data: bytes) -> Tuple[Optional[dict], List[str]]:
    """
    Valida e parseia o JSON exportado pelo SketchUp.

    Returns:
        (parsed_dict, errors) — se errors não estiver vazio, parsed_dict é None
    """
    errors = []

    try:
        data = json.loads(raw_data)
    except json.JSONDecodeError as e:
        return None, [f"JSON inválido: {e}"]

    # Validar estrutura mínima
    if "meta" not in data:
        errors.append("Campo 'meta' ausente no JSON.")
    if "tanks" not in data:
        errors.append("Campo 'tanks' ausente no JSON.")
    elif not isinstance(data["tanks"], list) or len(data["tanks"]) == 0:
        errors.append("'tanks' deve ser uma lista com pelo menos 1 tanque.")

    if errors:
        return None, errors

    # Validar cada tanque
    for i, tank in enumerate(data["tanks"]):
        tank_id = tank.get("id", f"tanque_{i}")
        if "regions" not in tank:
            errors.append(f"Tanque '{tank_id}': campo 'regions' ausente.")
            continue
        for j, region in enumerate(tank.get("regions", [])):
            if "label" not in region:
                errors.append(f"Tanque '{tank_id}', região {j}: campo 'label' ausente.")
            if "area_m2" not in region:
                errors.append(f"Tanque '{tank_id}', região {j}: campo 'area_m2' ausente.")

    if errors:
        return None, errors

    return data, []


# ─────────────────────────────────────────────────────────────────────────────
# 2. DIMENSIONAMENTO — FILTRAGEM
# ─────────────────────────────────────────────────────────────────────────────

def _dimensionar_filtragem(parsed: dict) -> dict:
    """
    Soma total_volume_m3 de todos os tanques e seleciona filtro.
    Replica lógica de filtragem.py (linhas 42-46).
    """
    volume_total = sum(
        tank.get("total_volume_m3", 0.0) for tank in parsed["tanks"]
    )

    filtro_selecionado = None
    for filtro in sorted(BANCO_FILTROS, key=lambda x: x["volume_6h"]):
        if filtro["volume_6h"] >= volume_total:
            filtro_selecionado = filtro
            break

    return {
        "volume_total_m3": round(volume_total, 2),
        "filtro": filtro_selecionado,
        "erro": None if filtro_selecionado else
                "Nenhum filtro da linha FM atende a este volume. "
                "Considerar associação em paralelo ou linha FVP."
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. DIMENSIONAMENTO — TRANSBORDO
# ─────────────────────────────────────────────────────────────────────────────

def _dimensionar_transbordo(
    parsed: dict,
    altura_lamina_mm: float,
    pressao_mca: int
) -> Optional[dict]:
    """
    Busca edges com label 'borda_infinita' e calcula vazão necessária.
    Replica lógica de transbordo.py (linhas 74-85).
    """
    # Coletar borda infinita de todos os tanques
    comprimento_total = 0.0
    area_piscina_total = 0.0
    tem_borda = False

    for tank in parsed["tanks"]:
        for edge in tank.get("edges", []):
            if edge.get("label") == "borda_infinita":
                comprimento_total += edge.get("length_m", 0.0)
                tem_borda = True
        area_piscina_total += tank.get("total_area_m2", 0.0)

    if not tem_borda:
        return None  # Sem borda infinita, não dimensionar transbordo

    # Fórmula de transbordo (replicada de transbordo.py)
    h = altura_lamina_mm / 1000.0
    vazao_necessaria = 1608 * h * comprimento_total * math.sqrt(2 * 9.81 * h)
    volume_cocho_litros = area_piscina_total * h * 3 * 1000
    area_lamina_m2 = h * comprimento_total

    # Seleção de bomba
    bomba_selecionada = None
    for bomba in BANCO_BOMBAS:
        key = f"vazao_{pressao_mca}_mca"
        vazao_pump = bomba.get(key)
        if vazao_pump is not None and vazao_pump >= vazao_necessaria:
            bomba_selecionada = bomba
            break

    return {
        "comprimento_borda_m": round(comprimento_total, 2),
        "altura_lamina_mm": altura_lamina_mm,
        "vazao_necessaria_m3h": round(vazao_necessaria, 2),
        "volume_cocho_litros": round(volume_cocho_litros, 2),
        "area_lamina_m2": round(area_lamina_m2, 4),
        "pressao_mca": pressao_mca,
        "bomba": bomba_selecionada,
        "erro": None if bomba_selecionada else
                "Nenhuma motobomba adequada encontrada para transbordo."
    }


# ─────────────────────────────────────────────────────────────────────────────
# 4. DIMENSIONAMENTO — HIDROMASSAGEM
# ─────────────────────────────────────────────────────────────────────────────

def _dimensionar_hidromassagem(
    parsed: dict,
    tipo_dispositivo: str,
    quantidade: int,
    pressao_mca: int
) -> Optional[dict]:
    """
    Identifica tanques com regiões 'banco' ou 'piso_spa' e dimensiona
    hidromassagem. Replica lógica de hidromassagem.py (linhas 95-106).
    """
    # Verificar se há regiões de spa
    tem_spa = False
    for tank in parsed["tanks"]:
        for region in tank.get("regions", []):
            label_base = region.get("label", "").split("_")[0] if "_" in region.get("label", "") else region.get("label", "")
            if label_base in ("banco", "piso_spa") or region.get("label", "").startswith("banco") or region.get("label", "").startswith("piso_spa"):
                tem_spa = True
                break
        if tem_spa:
            break

    if not tem_spa:
        return None  # Sem spa, não dimensionar hidromassagem

    # Cálculo (replicado de hidromassagem.py)
    vazao_por_dispositivo = 4.5 if tipo_dispositivo == "SODRAMAR" else 3.3
    vazao_necessaria = quantidade * vazao_por_dispositivo

    # Seleção de bomba
    bomba_selecionada = None
    for bomba in sorted(BANCO_BOMBAS, key=lambda x: x['potencia_cv']):
        chave_vazao = f'vazao_{pressao_mca}_mca'
        vazao_bomba = bomba.get(chave_vazao)
        if vazao_bomba and vazao_bomba >= vazao_necessaria:
            bomba_selecionada = bomba
            break

    return {
        "tipo_dispositivo": tipo_dispositivo,
        "quantidade": quantidade,
        "vazao_necessaria_m3h": round(vazao_necessaria, 1),
        "pressao_mca": pressao_mca,
        "bomba": bomba_selecionada,
        "erro": None if bomba_selecionada else
                "Nenhuma motobomba adequada encontrada para hidromassagem."
    }


# ─────────────────────────────────────────────────────────────────────────────
# 5. DIMENSIONAMENTO — AQUECIMENTO
# ─────────────────────────────────────────────────────────────────────────────

def _dimensionar_aquecimento(parsed: dict, inputs_manual: dict) -> dict:
    """
    Calcula dimensões a partir do JSON e passa para
    aquecimento.calcular_dimensionamento() com os inputs manuais.
    """
    # Calcular área e volume totais (todos os tanques)
    area_total = sum(t.get("total_area_m2", 0.0) for t in parsed["tanks"])
    volume_total = sum(t.get("total_volume_m3", 0.0) for t in parsed["tanks"])

    # Estimar largura e comprimento a partir da área (quadrado equivalente)
    # A função de aquecimento espera largura × comprimento
    lado = math.sqrt(area_total) if area_total > 0 else 1.0

    # Estimar profundidade média a partir do volume e área
    prof_media = volume_total / area_total if area_total > 0 else 1.0

    inputs = {
        "largura":           lado,
        "comprimento":       lado,
        "profundidade":      prof_media,
        "temp_agua":         float(inputs_manual.get("temp_agua", 30)),
        "regiao":            inputs_manual.get("regiao", 3),
        "ambiente":          inputs_manual.get("ambiente", "A"),
        "incidencia_solar":  float(inputs_manual.get("incidencia_solar", 100)),
        "velocidade_vento":  inputs_manual.get("velocidade_vento", 1.5),
        "horas_capa":        inputs_manual.get("horas_capa", 0),
        "custo_kwh":         inputs_manual.get("custo_kwh", 1.0),
        "custo_gn_m3":       inputs_manual.get("custo_gn_m3", 1.0),
        "modo":              "A",
    }

    resultado = calc_aquecimento(inputs)
    resultado["area_total_m2"] = round(area_total, 2)
    resultado["volume_total_m3"] = round(volume_total, 2)
    resultado["profundidade_media_m"] = round(prof_media, 2)

    return resultado


# ─────────────────────────────────────────────────────────────────────────────
# 6. TABELA RESUMO
# ─────────────────────────────────────────────────────────────────────────────

def _build_summary_table(parsed: dict) -> pd.DataFrame:
    """
    Constrói DataFrame com A, h, V por região de cada tanque.
    """
    rows = []
    for tank in parsed["tanks"]:
        for region in tank.get("regions", []):
            rows.append({
                "Tanque": tank.get("id", "—"),
                "Região": region.get("label", "—"),
                "Área (m²)": region.get("area_m2", 0.0),
                "Prof. (m)": region.get("depth_m", 0.0),
                "Volume (m³)": region.get("volume_m3", 0.0),
            })

        # Totais do tanque
        rows.append({
            "Tanque": tank.get("id", "—"),
            "Região": "**TOTAL**",
            "Área (m²)": tank.get("total_area_m2", 0.0),
            "Prof. (m)": "—",
            "Volume (m³)": tank.get("total_volume_m3", 0.0),
        })

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# 7. RENDERIZAÇÃO DE RESULTADOS
# ─────────────────────────────────────────────────────────────────────────────

def _render_filtragem(result: dict):
    """Exibe resultados de filtragem."""
    st.subheader("🔵 Filtragem")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Volume total", f"{result['volume_total_m3']:.2f} m³")

    if result["erro"]:
        st.error(result["erro"])
        return

    filtro = result["filtro"]
    with col1:
        st.metric("Filtro Selecionado", filtro["modelo"])
        st.metric("Vazão do conjunto", f"{filtro['volume_6h'] / 6:.2f} m³/h")
        st.metric("Motobomba", filtro["modelo_motobomba"])

    with col2:
        with st.expander("🔍 Detalhes Técnicos do Filtro"):
            st.write(f"**Capacidade:** 6h: {filtro['volume_6h']} m³ | 8h: {filtro['volume_8h']} m³")
            st.write(f"**Dimensões:** Ø{filtro['diametro_mm']}mm × {filtro['altura_mm']}mm")
            st.write(f"**Carga de areia:** {filtro['carga_areia_kg']} kg ({filtro['quant_sacos_25kg']} sacos de 25kg)")
            st.write(f"**Peso bruto:** c/ areia: {filtro['peso_bruto_com_areia_kg']} kg | s/ areia: {filtro['peso_bruto_sem_areia_kg']} kg")


def _render_transbordo(result: Optional[dict]):
    """Exibe resultados de transbordo."""
    if result is None:
        return

    st.subheader("🔷 Transbordo (Borda Infinita)")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Comprimento da borda", f"{result['comprimento_borda_m']:.2f} m")
        st.metric("Altura da lâmina", f"{result['altura_lamina_mm']:.1f} mm")
        st.metric("Vazão necessária", f"{result['vazao_necessaria_m3h']:.2f} m³/h")
        st.metric("Volume útil mínimo cocho", f"{result['volume_cocho_litros']:.2f} L")

    if result["erro"]:
        st.error(result["erro"])
    else:
        bomba = result["bomba"]
        with col1:
            st.success(f"**Motobomba:** {bomba['modelo']}")
            st.metric("Potência", f"{bomba['potencia_cv']} CV")

        with col2:
            with st.expander("🔍 Detalhes da Motobomba de Transbordo"):
                st.write(f"**Modelo:** {bomba['modelo']}")
                st.write(f"**Potência:** {bomba['potencia_cv']} CV")
                key = f"vazao_{result['pressao_mca']}_mca"
                st.write(f"**Vazão em {result['pressao_mca']} m.c.a:** {bomba.get(key, '—')} m³/h")


def _render_hidromassagem(result: Optional[dict]):
    """Exibe resultados de hidromassagem."""
    if result is None:
        return

    st.subheader("🟣 Hidromassagem")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Tipo de dispositivo", result["tipo_dispositivo"])
        st.metric("Quantidade", result["quantidade"])
        st.metric("Vazão total", f"{result['vazao_necessaria_m3h']:.1f} m³/h")
        st.metric("Pressão", f"{result['pressao_mca']} m.c.a")

    if result["erro"]:
        st.error(result["erro"])
    else:
        bomba = result["bomba"]
        with col1:
            st.success(f"**Motobomba:** {bomba['modelo']}")
            st.metric("Potência", f"{bomba['potencia_cv']} CV")


def _render_aquecimento(result: dict):
    """Exibe resultados de aquecimento."""
    st.subheader("🟠 Aquecimento")

    if result.get("erro"):
        st.error(f"⚠️ {result['erro']}")
        if "energia_btu_h" in result:
            st.metric("Energia necessária", f"{result['energia_btu_h']:,.0f} BTU/h")
        return

    # Banner de status
    if result.get("equipamento_atende"):
        st.success(f"✅ Equipamento Dimensionado — **{result['modelo']}**")
    else:
        st.error(
            f"⚠️ O modelo **{result['modelo']}** opera {result['horas_inverno']:.1f}h/dia "
            f"no inverno (limite: 17h). Considere um modelo maior."
        )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Modelo", result["modelo"])
    col2.metric("Capacidade", f"{result['capacidade_btu_h']:,.0f} BTU/h")
    col3.metric("Potência nominal", f"{result['potencia_nominal_kw']:.2f} kW")
    col4.metric("COP", f"{result['cop']:.2f}")

    with st.expander("🔍 Detalhes do Aquecimento"):
        d1, d2, d3 = st.columns(3)
        d1.metric("Área total", f"{result.get('area_total_m2', 0):.1f} m²")
        d2.metric("Volume total", f"{result.get('volume_total_m3', 0):.1f} m³")
        d3.metric("Prof. média", f"{result.get('profundidade_media_m', 0):.2f} m")

        e1, e2, e3 = st.columns(3)
        e1.metric("Energia (BTU/h)", f"{result['energia_btu_h']:,.0f}")
        e2.metric("Energia (kcal/h)", f"{result['energia_kcal_h']:,.0f}")
        e3.metric("Energia (kW)", f"{result['energia_kw']:.2f}")

        f1, f2, f3 = st.columns(3)
        f1.metric("Consumo elétrico", f"{result['consumo_eletrico_kw']:.2f} kW")
        f2.metric("Horas/dia (inverno)", f"{round(result['horas_inverno'])} h")
        f3.metric("Horas/dia (verão)", f"{round(result['horas_verao'])} h")

        g1, g2 = st.columns(2)
        g1.metric("Custo médio mensal", f"R$ {result['custo_medio_mensal']:,.2f}")
        g2.metric("Economia vs gás", f"R$ {result['economia_mensal']:,.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# 8. INTERFACE PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def _has_borda_infinita(parsed: dict) -> bool:
    """Verifica se existe borda infinita no JSON."""
    for tank in parsed.get("tanks", []):
        for edge in tank.get("edges", []):
            if edge.get("label") == "borda_infinita":
                return True
    return False


def _has_spa(parsed: dict) -> bool:
    """Verifica se existem regiões de spa (banco/piso_spa) no JSON."""
    for tank in parsed.get("tanks", []):
        for region in tank.get("regions", []):
            label = region.get("label", "")
            if label.startswith("banco") or label.startswith("piso_spa"):
                return True
    return False


@track_access("dimensionamento_completo")
def run() -> None:
    """
    Função principal do módulo de Dimensionamento Completo.
    Chamada pelo main_app.py.
    """
    st.title("💧 Dimensionamento Completo")
    st.caption("Importação de JSON do SketchUp → Dimensionamento automático de todos os sistemas")
    st.markdown("---")

    # ─── Upload do JSON ─────────────────────────────────────────────────────
    uploaded = st.file_uploader(
        "Importar JSON do SketchUp",
        type=["json"],
        help="Arquivo exportado pela extensão HidroAnnotator do SketchUp"
    )

    if not uploaded:
        st.info(
            "📁 Faça upload do arquivo JSON exportado pelo HidroAnnotator no SketchUp.\n\n"
            "O JSON deve conter a estrutura de tanques com regiões anotadas "
            "(fundo, prainha, cocho, etc.) e arestas classificadas."
        )
        return

    # ─── Parsing e validação ────────────────────────────────────────────────
    parsed, errors = parse_json(uploaded.read())

    if errors:
        st.error("❌ Erros de validação no JSON:")
        for err in errors:
            st.write(f"- {err}")
        return

    # ─── Preview / Tabela resumo ────────────────────────────────────────────
    meta = parsed.get("meta", {})
    st.success(
        f"✅ JSON carregado: **{meta.get('model_name', '—')}** "
        f"({meta.get('export_date', '—')})"
    )

    with st.expander("📊 Tabela Resumo — Regiões e Volumes", expanded=True):
        df = _build_summary_table(parsed)
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ─── Inputs manuais complementares ──────────────────────────────────────
    st.subheader("⚙️ Parâmetros complementares")
    st.caption("Dados que não vêm do modelo 3D e precisam ser informados manualmente.")

    with st.expander("Transbordo", expanded=_has_borda_infinita(parsed)):
        if _has_borda_infinita(parsed):
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                altura_lamina_mm = st.number_input(
                    "Altura da lâmina (mm)",
                    min_value=1.0, value=3.0, step=0.5, format="%.1f",
                    key="dc_lamina"
                )
            with col_t2:
                pressao_transbordo = st.selectbox(
                    "Pressão dimensionada (m.c.a)",
                    options=sorted({2, 4, 6, 8, 10, 12, 14, 16, 18}),
                    index=2, key="dc_press_transb"
                )
        else:
            st.info("ℹ️ Nenhuma borda infinita detectada no JSON.")
            altura_lamina_mm = 3.0
            pressao_transbordo = 6

    with st.expander("Hidromassagem", expanded=_has_spa(parsed)):
        if _has_spa(parsed):
            col_h1, col_h2, col_h3 = st.columns(3)
            with col_h1:
                tipo_dispositivo = st.selectbox(
                    "Tipo de dispositivo",
                    ["SODRAMAR", "ALBACETE"],
                    key="dc_tipo_hidro"
                )
            with col_h2:
                qtd_dispositivos = st.number_input(
                    "Quantidade de dispositivos",
                    min_value=1, max_value=99, value=4, step=1,
                    key="dc_qtd_hidro"
                )
            with col_h3:
                pressao_hidro = st.number_input(
                    "Pressão (m.c.a)",
                    min_value=4, max_value=18, value=8, step=2,
                    key="dc_press_hidro"
                )
        else:
            st.info("ℹ️ Nenhuma região de spa (banco/piso_spa) detectada no JSON.")
            tipo_dispositivo = "SODRAMAR"
            qtd_dispositivos = 1
            pressao_hidro = 8

    with st.expander("Aquecimento — Região Climática", expanded=True):
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            temp_agua = st.number_input(
                "Temperatura desejada (°C)",
                min_value=25, max_value=41, value=30, step=1,
                key="dc_temp"
            )
            regiao_climatica = st.selectbox(
                "Região climática",
                options=[1, 2, 3],
                format_func=lambda x: {1: "1 - Quente", 2: "2 - Frio", 3: "3 - Médio"}[x],
                index=2, key="dc_regiao"
            )
            ambiente = st.radio(
                "Ambiente", ["A", "F"],
                format_func=lambda x: "Aberto" if x == "A" else "Fechado",
                horizontal=True, key="dc_ambiente"
            )
        with col_a2:
            incidencia_solar = st.select_slider(
                "Incidência solar (%)",
                options=list(range(0, 105, 5)),
                value=100, key="dc_solar"
            )
            velocidade_vento = st.select_slider(
                "Velocidade do vento",
                options=[0.1, 1.5, 3.0, 4.5],
                format_func=lambda x: {
                    0.1: "Sem vento (0,1 km/h)", 1.5: "Fraco (1,5 km/h)",
                    3.0: "Médio (3,0 km/h)", 4.5: "Forte (4,5 km/h)"
                }[x],
                value=1.5, key="dc_vento"
            )
            horas_capa = st.slider(
                "Horas com capa térmica",
                0, 16, 0, key="dc_capa"
            )
            custo_kwh = st.number_input(
                "Custo kWh (R$)",
                min_value=0.0, max_value=10.0, value=1.0, step=1.0,
                format="%.4f", key="dc_kwh"
            )
            custo_gn = st.number_input(
                "Custo Gás Natural (R$/m³)",
                min_value=0.0, max_value=50.0, value=1.0, step=1.0,
                format="%.2f", key="dc_gn"
            )

    st.markdown("---")

    # ─── Botão calcular ─────────────────────────────────────────────────────
    if st.button("🚀 Calcular Dimensionamento Completo", type="primary", use_container_width=True):
        with st.spinner("Calculando todos os sistemas..."):

            # Filtragem
            res_filtragem = _dimensionar_filtragem(parsed)

            # Transbordo
            res_transbordo = _dimensionar_transbordo(
                parsed, altura_lamina_mm, pressao_transbordo
            )

            # Hidromassagem
            res_hidromassagem = _dimensionar_hidromassagem(
                parsed, tipo_dispositivo, qtd_dispositivos, pressao_hidro
            )

            # Aquecimento
            inputs_aq = {
                "temp_agua": temp_agua,
                "regiao": regiao_climatica,
                "ambiente": ambiente,
                "incidencia_solar": incidencia_solar,
                "velocidade_vento": velocidade_vento,
                "horas_capa": horas_capa,
                "custo_kwh": custo_kwh,
                "custo_gn_m3": custo_gn,
            }
            res_aquecimento = _dimensionar_aquecimento(parsed, inputs_aq)

            # Armazenar no session_state
            st.session_state["dc_resultados"] = {
                "filtragem": res_filtragem,
                "transbordo": res_transbordo,
                "hidromassagem": res_hidromassagem,
                "aquecimento": res_aquecimento,
            }

    # ─── Exibir resultados ──────────────────────────────────────────────────
    if "dc_resultados" in st.session_state:
        results = st.session_state["dc_resultados"]

        st.markdown("---")
        st.header("📋 Resultados do Dimensionamento")

        _render_filtragem(results["filtragem"])
        st.markdown("---")

        _render_transbordo(results["transbordo"])
        if results["transbordo"]:
            st.markdown("---")

        _render_hidromassagem(results["hidromassagem"])
        if results["hidromassagem"]:
            st.markdown("---")

        _render_aquecimento(results["aquecimento"])


# Para compatibilidade com main_app.py
if __name__ == "__main__":
    run()
