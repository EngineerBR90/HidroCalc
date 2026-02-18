# modules/perda_carga.py
import math
import streamlit as st
from typing import Dict, Any, List
from tracking import track_access
from modules.data import DIAMETROS_TUBULACAO as DIAMETROS, CONEXOES_EQUIV
from modules.calc_utils import calcular_fator_atrito

# Constantes de projeto
VISCOSIDADE_AGUA = 0.896e-6  # m²/s (água a 20°C)
MARGEM_SEGURANCA = 1.05       # 5% (aplicada internamente)
G = 9.81                      # m/s²


def calcular_linha(Q_m3h: float, diam_ext: str, L_real: float, conexoes: Dict[str, int]) -> Dict[str, float]:
    """
    Calcula propriedades hidráulicas de um trecho com vazão constante.
    Retorna dicionário com D_int (mm), V (m/s), Re, f, L_eq (m) e hf_total (mca) – sem margem.
    """
    D_int = DIAMETROS[diam_ext] / 1000  # m
    Q = Q_m3h / 3600                     # m³/s
    A = math.pi * (D_int ** 2) / 4
    V = Q / A if A > 0 else 0
    Re = V * D_int / VISCOSIDADE_AGUA if D_int > 0 else 0
    f = calcular_fator_atrito(Re, D_int)

    L_eq = sum(qtd * CONEXOES_EQUIV[conexao].get(diam_ext, 0)
               for conexao, qtd in conexoes.items())

    hf_total = f * ((L_real + L_eq) / D_int) * (V ** 2 / (2 * G))

    return {
        'D_int': D_int * 1000,
        'V': V,
        'Re': Re,
        'f': f,
        'L_eq': L_eq,
        'hf_total': hf_total
    }


def calcular_recalque_multiplos(Q_m3h: float, diam_prim: str, diam_sec: str,
                                L_prim: float, L_sec: float, num_retornos: int,
                                conex_p: Dict[str, int], conex_s: Dict[str, int]) -> Dict[str, Any]:
    """
    Calcula perda de carga no recalque com múltiplos retornos.
    - Ramal primário: vazão total, diâmetro `diam_prim`.
    - Ramal secundário: vazão reduzida progressivamente, diâmetro `diam_sec`.
    Retorna dicionário com:
        D_int_prim (mm), D_int_sec (mm), V_max (m/s), hf_total (mca),
        hf_prim, hf_sec, segmentos (lista), L_eq_total.
    """
    # Ramal Primário
    prim = calcular_linha(Q_m3h, diam_prim, L_prim, conex_p)

    # Ramal Secundário
    D_int_sec = DIAMETROS[diam_sec] / 1000
    A_sec = math.pi * (D_int_sec ** 2) / 4
    Q_total = Q_m3h / 3600
    Q_retorno = Q_total / num_retornos

    L_eq_sec = sum(qtd * CONEXOES_EQUIV[c].get(diam_sec, 0) for c, qtd in conex_s.items())
    L_seg = (L_sec + L_eq_sec) / num_retornos

    hf_sec_total = 0.0
    segmentos = []
    velocidades_sec = []

    for i in range(1, num_retornos + 1):
        Q_i = Q_total - (i - 1) * Q_retorno
        V_i = Q_i / A_sec
        Re_i = V_i * D_int_sec / VISCOSIDADE_AGUA
        f_i = calcular_fator_atrito(Re_i, D_int_sec)
        hf_i = f_i * (L_seg / D_int_sec) * (V_i ** 2 / (2 * G))

        hf_sec_total += hf_i
        velocidades_sec.append(V_i)
        segmentos.append({
            'Seg.': i,
            'Vazão (m³/h)': Q_i * 3600,
            'Vel. (m/s)': V_i,
            'Perda (mca)': hf_i
        })

    v_max = max(prim['V'], max(velocidades_sec))

    return {
        'D_int_prim': prim['D_int'],
        'D_int_sec': D_int_sec * 1000,
        'V_max': v_max,
        'hf_total': prim['hf_total'] + hf_sec_total,
        'hf_prim': prim['hf_total'],
        'hf_sec': hf_sec_total,
        'segmentos': segmentos,
        'L_eq_total': prim['L_eq'] + L_eq_sec
    }


def interface_conexoes(label: str) -> Dict[str, int]:
    """Gera interface para entrada de quantidades de conexões."""
    with st.expander(f"Conexões - {label}"):
        conexoes = {}
        cols = st.columns(2)
        for i, conexao in enumerate(CONEXOES_EQUIV.keys()):
            with cols[i % 2]:
                conexoes[conexao] = st.number_input(
                    f"{conexao}:",
                    min_value=0,
                    value=0,
                    step=1,
                    key=f"{label}_{conexao}"
                )
        return conexoes


@track_access("perda_carga")
def main() -> None:
    st.title("💧 Dimensionamento de Perda de Carga")
    st.markdown("""
        **Inclui alerta de velocidade limite de acordo com a ABNT NBR 10.339 (sucção ≤ 1,8 m/s; recalque ≤ 3,0 m/s:**  
              """)

    with st.form(key='form_hidraulica'):
        Q_m3h = st.number_input(
            "Vazão de Projeto (m³/h):",
            min_value=0.1, max_value=500.0, value=9.80, step=0.1
        )

        # --- Sucção ---
        st.subheader("Sucção")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            diam_suc = st.selectbox(
                "Diâmetro Externo (mm):",
                list(DIAMETROS.keys()),
                index=3,
                key='dsuc'
            )
        with col_s2:
            L_suc = st.number_input(
                "Comprimento Real (m):",
                min_value=0.1, max_value=1000.0, value=6.0, step=6.0,
                key='lsuc'
            )
        conexoes_suc = interface_conexoes("Sucção")

        st.divider()

        # --- Recalque (sempre com múltiplos retornos) ---
        st.subheader("Recalque (múltiplos retornos)")

        # Ramal Primário
        st.markdown("**Ramal Primário** (vazão total)")
        col_rp1, col_rp2 = st.columns(2)
        with col_rp1:
            diam_prim = st.selectbox(
                "Diâmetro Externo (mm):",
                list(DIAMETROS.keys()),
                index=3,
                key='dprim'
            )
        with col_rp2:
            L_prim = st.number_input(
                "Comprimento (m):",
                min_value=0.1, max_value=1000.0, value=6.0, step=6.0,
                key='lprim'
            )
        conex_prim = interface_conexoes("Ramal Primário")

        # Ramal Secundário
        st.markdown("**Ramal Secundário** (trechos com retornos)")
        col_rs1, col_rs2 = st.columns(2)
        with col_rs1:
            diam_sec = st.selectbox(
                "Diâmetro Externo (mm):",
                list(DIAMETROS.keys()),
                index=3,
                key='dsec'
            )
        with col_rs2:
            L_sec = st.number_input(
                "Comprimento (m):",
                min_value=0.1, max_value=1000.0, value=12.0, step=6.0,
                key='lsec'
            )

        # Slider centralizado para número de retornos
        col_center1, col_center2, col_center3 = st.columns([1, 2, 1])
        with col_center2:
            num_retornos = st.slider(
                "Nº Retornos:",
                min_value=1, max_value=20, value=4, step=1,
                key='nret'
            )

        conex_sec = interface_conexoes("Ramal Secundário")

        btn = st.form_submit_button("Calcular Perda de Carga", type="primary", use_container_width=True)

    if btn:
        try:
            # Cálculo da sucção
            res_suc = calcular_linha(Q_m3h, diam_suc, L_suc, conexoes_suc)

            # Cálculo do recalque (sempre múltiplos)
            res_rec = calcular_recalque_multiplos(
                Q_m3h, diam_prim, diam_sec, L_prim, L_sec,
                num_retornos, conex_prim, conex_sec
            )

            # Alertas
            alerta_suc = res_suc['V'] > 1.8
            alerta_rec = res_rec['V_max'] > 3.0

            # Perda total com margem
            total_perda = (res_suc['hf_total'] + res_rec['hf_total']) * MARGEM_SEGURANCA

            # --- Exibição dos resultados ---
            st.markdown("---")
            st.subheader("Resultados do Dimensionamento")

            # Destaque para a perda total
            with st.container():
                st.metric(
                    label="💧 Perda de Carga Total (com margem de 5%)",
                    value=f"{total_perda:.2f} mca",
                    delta=None,
                    delta_color="off"
                )

            col_esq, col_dir = st.columns(2)

            with col_esq:
                st.markdown("**Sucção**")
                st.metric("Diâmetro Interno", f"{res_suc['D_int']:.1f} mm")
                st.metric(
                    "Velocidade",
                    f"{res_suc['V']:.2f} m/s",
                    delta="🔴 Acima do limite!" if alerta_suc else "✅ OK",
                    delta_color="inverse" if alerta_suc else "off"
                )
                st.metric("Perda de Carga", f"{res_suc['hf_total']:.2f} mca")

            with col_dir:
                st.markdown("**Recalque**")
                # Dois diâmetros lado a lado
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.metric("Ø Primário", f"{res_rec['D_int_prim']:.1f} mm")
                with col_d2:
                    st.metric("Ø Secundário", f"{res_rec['D_int_sec']:.1f} mm")

                st.metric(
                    "Velocidade Máxima",
                    f"{res_rec['V_max']:.2f} m/s",
                    delta="🔴 Acima do limite!" if alerta_rec else "✅ OK",
                    delta_color="inverse" if alerta_rec else "off"
                )
                st.metric("Perda de Carga", f"{res_rec['hf_total']:.2f} mca")

            # Detalhamento e curva do sistema
            with st.expander("Memória de Cálculo e Curva do Sistema"):
                st.write("**Composição da perda (valores parciais):**")
                st.info(f"""
                    - Sucção: {res_suc['hf_total']:.2f} mca  
                    - Recalque: {res_rec['hf_total']:.2f} mca  
                    - Total (antes da margem): {res_suc['hf_total'] + res_rec['hf_total']:.2f} mca
                    """)

                st.write("**Detalhamento do ramal secundário (segmentos):**")
                st.dataframe(res_rec['segmentos'], use_container_width=True)

                # Curva característica
                K = total_perda / (Q_m3h ** 2) if Q_m3h != 0 else 0
                st.markdown("**Função da curva do sistema (H = K·Q²):**")
                st.latex(f"H_{{sistema}}(Q) = {K:.6f} \\cdot Q^2")
                st.code(f"def curva_instalacao(Q):\n    return {K:.6f} * Q**2", language="python")

        except Exception as e:
            st.error(f"Erro no cálculo: {str(e)}")


if __name__ == "__main__":
    main()