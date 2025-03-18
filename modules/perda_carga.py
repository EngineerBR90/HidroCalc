# modules/perda_carga.py
import math
import streamlit as st

# Dicionário para conversão de diâmetro externo para interno (valores em mm)
DIAMETROS = {
    20: 17.0,
    25: 21.6,
    32: 27.8,
    40: 35.2,
    50: 44.0,
    60: 53.4,
    75: 66.6,
    85: 75.6,
    110: 97.8
}

# Estrutura de dados para comprimento equivalente das conexões para PVC.
# Cada conexão possui um dicionário que relaciona o diâmetro externo à
# um valor de comprimento equivalente (em metros).
CONEXOES_EQUIV = {
    "joelho 90º": {
        25: 1.2,
        32: 1.5,
        40: 2.0,
        50: 3.2,
        60: 3.4,
        75: 3.7,
        85: 3.9,
        110: 4.3
    },
    "joelho 45º": {
        25: 0.8,
        32: 1.0,
        40: 1.3,
        50: 2.0,
        60: 2.2,
        75: 2.5,
        85: 2.7,
        110: 3.0
    },
    "união": {
        25: 0.5,
        32: 0.6,
        40: 0.8,
        50: 1.0,
        60: 1.2,
        75: 1.4,
        85: 1.5,
        110: 1.8
    },
    "Tê de passagem direta": {
        25: 1.0,
        32: 1.2,
        40: 1.5,
        50: 2.0,
        60: 2.3,
        75: 2.5,
        85: 2.8,
        110: 3.2
    },
    "Tê de saída lateral": {
        25: 1.1,
        32: 1.3,
        40: 1.6,
        50: 2.1,
        60: 2.4,
        75: 2.7,
        85: 2.9,
        110: 3.3
    },
    "registro esfera aberto": {
        25: 0.3,
        32: 0.4,
        40: 0.5,
        50: 0.7,
        60: 0.8,
        75: 1.0,
        85: 1.1,
        110: 1.3
    },
    "curva 90º": {
        25: 1.2,
        32: 1.5,
        40: 2.0,
        50: 3.2,
        60: 3.4,
        75: 3.7,
        85: 3.9,
        110: 4.3
    },
    "curva 45º": {
        25: 0.8,
        32: 1.0,
        40: 1.3,
        50: 2.0,
        60: 2.2,
        75: 2.5,
        85: 2.7,
        110: 3.0
    }
}


def calcular_perda_carga_streamlit():
    st.title("📉 Cálculo de Perda de Carga")
    st.markdown("---")

    # Seção para seleção de material (única opção: PVC)
    material = st.selectbox("Selecione o Material da Tubulação:", options=["PVC"])

    # Formulário de entrada de dados
    with st.form(key='form_perda_carga'):
        col1, col2 = st.columns(2)
        with col1:
            Q_m3h = st.number_input(
                "Vazão (m³/h):",
                min_value=0.1,
                value=10.0,
                step=0.1,
                format="%.2f"
            )
            L = st.number_input(
                "Comprimento da tubulação (m):",
                min_value=0.1,
                value=50.0,
                step=1.0,
                format="%.1f"
            )
        with col2:
            diam_ext = st.selectbox(
                "Selecione o diâmetro EXTERNO da tubulação (mm):",
                options=list(DIAMETROS.keys()),
                index=3  # Exemplo: 40 mm
            )

        st.markdown("#### Conexões – Linha de Sucção")
        conexoes_suc = {}
        with st.expander("Conexões para Sucção", expanded=True):
            for conexao in CONEXOES_EQUIV:
                conexoes_suc[conexao] = st.number_input(
                    f"Quantidade de {conexao}",
                    min_value=0,
                    value=0,
                    step=1,
                    key=f"suc_{conexao}"
                )

        st.markdown("#### Conexões – Linha de Recalque")
        conexoes_rec = {}
        with st.expander("Conexões para Recalque", expanded=True):
            for conexao in CONEXOES_EQUIV:
                conexoes_rec[conexao] = st.number_input(
                    f"Quantidade de {conexao}",
                    min_value=0,
                    value=0,
                    step=1,
                    key=f"rec_{conexao}"
                )

        calcular = st.form_submit_button("Calcular Perda de Carga", type="primary")

    if calcular:
        try:
            # Constantes (baseado em 20°C)
            VISCOSIDADE_AGUA = 1.004e-6  # m²/s
            RUGOSIDADE_PVC = 0.0000015  # m
            g = 9.81  # m/s²

            # Conversões e ajustes
            Q = Q_m3h / 3600  # m³/s
            # Diâmetro interno em metros (convertido a partir do diâmetro externo)
            D_int = DIAMETROS[diam_ext] / 1000

            # Cálculo da área e velocidade do fluxo
            A = math.pi * (D_int ** 2) / 4
            V = Q / A if A > 0 else 0

            # Número de Reynolds
            Re = V * D_int / VISCOSIDADE_AGUA if D_int > 0 else 0

            # Cálculo do fator de atrito
            if Re < 2000:
                f = 64 / Re if Re > 0 else 0
                regime = "Laminar"
            else:
                x1 = 4.0
                tol = 1e-6
                max_iter = 100
                convergiu = False
                for i in range(max_iter):
                    termo1 = RUGOSIDADE_PVC / (3.7 * D_int)
                    termo2 = 2.51 / (Re * math.sqrt(x1))
                    f_calc = 0.25 / (math.log10(termo1 + termo2)) ** 2
                    if abs(f_calc - x1) < tol:
                        f = f_calc
                        convergiu = True
                        break
                    x1 = f_calc
                regime = "Turbulento" if convergiu else "Não convergiu"
                if not convergiu:
                    st.warning("Cálculo do fator de atrito não convergiu após 100 iterações!")

            # Cálculo da perda de carga distribuída (hf)
            hf = f * (L / D_int) * (V ** 2 / (2 * g)) if D_int > 0 else 0

            # Cálculo do comprimento equivalente adicional para cada linha, somando as conexões.
            # Para cada conexão, obtemos o comprimento equivalente com base no diâmetro externo selecionado.
            le_total_suc = 0
            for conexao, quant in conexoes_suc.items():
                # Se o diâmetro não estiver definido para a conexão, considera 0
                le = CONEXOES_EQUIV.get(conexao, {}).get(diam_ext, 0)
                le_total_suc += quant * le

            le_total_rec = 0
            for conexao, quant in conexoes_rec.items():
                le = CONEXOES_EQUIV.get(conexao, {}).get(diam_ext, 0)
                le_total_rec += quant * le

            # Comprimento efetivo para cada linha: tubulação distribuída + conexões
            L_eff_suc = L + le_total_suc
            L_eff_rec = L + le_total_rec

            # Cálculo da perda de carga total para cada linha
            hf_total_suc = f * (L_eff_suc / D_int) * (V ** 2 / (2 * g)) * 1.05
            hf_total_rec = f * (L_eff_rec / D_int) * (V ** 2 / (2 * g)) * 1.05

            # Perda unitária (% por 100m) considerando apenas a perda distribuída
            perda_percentual_100m = (hf / L) * 100 if L != 0 else 0

            # Verificações de velocidade conforme NBR 10.339:2018:
            # Sucção: alerta se > 1,8 m/s; Recalque: alerta se > 3,0 m/s
            alerta_suc = V > 1.8
            alerta_rec = V > 3.0

            # Exibição dos resultados
            st.success("**Resultados do Cálculo**")
            cols1 = st.columns(2)
            with cols1[0]:
                st.metric("Velocidade do Fluido (m/s)", f"{V:.4f}")
                st.metric("Número de Reynolds", f"{Re:.0f}")
                st.metric("Regime de Escoamento", regime)
            with cols1[1]:
                st.metric("Fator de Atrito (f)", f"{f:.6f}")
                st.metric("Perda Distribuída", f"{hf:.4f} mca")
                st.metric("Perda Unitária", f"{perda_percentual_100m:.2f}% por 100m")

            st.markdown("### Comprimentos Equivalentes e Perdas Totais")
            cols2 = st.columns(2)
            with cols2[0]:
                st.metric("Comprimento Equiv. Adicional (Sucção)", f"{le_total_suc:.2f} m")
                st.metric("Perda Total Sucção (c/ 5% margem)", f"{hf_total_suc:.4f} mca")
            with cols2[1]:
                st.metric("Comprimento Equiv. Adicional (Recalque)", f"{le_total_rec:.2f} m")
                st.metric("Perda Total Recalque (c/ 5% margem)", f"{hf_total_rec:.4f} mca")

            st.markdown("### Velocidades e Alertas")
            st.write(f"**Velocidade de Sucção:** {V:.4f} m/s")
            st.write(f"**Velocidade de Recalque:** {V:.4f} m/s")
            if alerta_suc:
                st.error("Atenção: A velocidade na linha de sucção ultrapassa 1,8 m/s!")
            if alerta_rec:
                st.error("Atenção: A velocidade na linha de recalque ultrapassa 3,0 m/s!")

            with st.expander("Detalhes Técnicos"):
                st.write("**Parâmetros Utilizados:**")
                st.write(f"- Material: {material}")
                st.write(f"- Viscosidade da água (20°C): {VISCOSIDADE_AGUA:.3e} m²/s")
                st.write(f"- Rugosidade do PVC: {RUGOSIDADE_PVC} m")
                st.write(f"- Diâmetro Interno: {D_int * 1000:.1f} mm (convertido do externo de {diam_ext} mm)")
                st.write(f"- Comprimento de tubulação (distribuída): {L:.2f} m")
                st.write(f"- Comprimento Equiv. Sucção: {le_total_suc:.2f} m")
                st.write(f"- Comprimento Equiv. Recalque: {le_total_rec:.2f} m")

        except Exception as e:
            st.error(f"Erro nos cálculos: {str(e)}")
            st.stop()


def run():
    calcular_perda_carga_streamlit()


if __name__ == "__main__":
    run()
