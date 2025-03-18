# modules/perda_carga.py
import math
import streamlit as st


def calcular_perda_carga_streamlit():
    st.title("📉 Cálculo de Perda de Carga")
    st.markdown("---")

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
            D_mm = st.number_input(
                "Diâmetro interno (mm):",
                min_value=5.0,
                value=50.0,
                step=5.0,
                format="%.1f"
            )

            temperatura = st.number_input(
                "Temperatura da água (°C):",
                min_value=0.0,
                max_value=40.0,
                value=20.0,
                step=0.5
            )

        calcular = st.form_submit_button("Calcular Perda de Carga", type="primary")

    if calcular:
        try:
            # Constantes atualizadas
            VISCOSIDADE_AGUA = 1.004e-6  # m²/s (20°C)
            RUGOSIDADE_PVC = 0.0000015  # m

            # Conversão de unidades
            Q = Q_m3h / 3600  # m³/s
            D = D_mm / 1000  # m

            # Cálculo da área e velocidade
            A = math.pi * (D ** 2) / 4
            V = Q / A if A > 0 else 0

            # Número de Reynolds
            Re = V * D / VISCOSIDADE_AGUA if D > 0 else 0

            # Cálculo do fator de atrito
            if Re < 2000:
                f = 64 / Re if Re > 0 else 0
                regime = "Laminar"
            else:
                # Newton-Raphson para Colebrook-White
                x1 = 4.0
                tol = 1e-6
                max_iter = 100
                convergiu = False

                for i in range(max_iter):
                    termo1 = RUGOSIDADE_PVC / (3.7 * D)
                    termo2 = 2.51 / (Re * math.sqrt(x1))
                    f = 0.25 / (math.log10(termo1 + termo2)) ** 2

                    if abs(f - x1) < tol:
                        convergiu = True
                        break
                    x1 = f

                regime = "Turbulento" if convergiu else "Não convergiu"
                if not convergiu:
                    st.warning("Cálculo não convergiu após 100 iterações!")

            # Cálculo da perda de carga
            g = 9.81
            hf = f * (L / D) * (V ** 2 / (2 * g)) if D > 0 else 0

            # Cálculos adicionais
            perda_percentual_100m = (hf / L) * 100 if L != 0 else 0
            hf_mais_5porcento = hf * 1.05

            # Exibição dos resultados
            st.success("**Resultados do Cálculo**")

            cols = st.columns(2)
            with cols[0]:
                st.metric("Velocidade do Fluido", f"{V:.4f} m/s")
                st.metric("Número de Reynolds", f"{Re:.0f}")
                st.metric("Regime de Escoamento", regime)

            with cols[1]:
                st.metric("Fator de Atrito (f)", f"{f:.6f}")
                st.metric("Perda de Carga Unitária", f"{perda_percentual_100m:.2f}% por 100m")
                st.metric("Perda Total com Margem 5%", f"{hf_mais_5porcento:.4f} mca")

            with st.expander("Detalhes Técnicos"):
                st.write(f"**Parâmetros Utilizados:**")
                st.write(f"- Viscosidade cinemática: {VISCOSIDADE_AGUA:.3e} m²/s")
                st.write(f"- Rugosidade do PVC: {RUGOSIDADE_PVC} m")
                st.write(f"- Número de iterações: {i + 1 if 'i' in locals() else 0}")

        except Exception as e:
            st.error(f"Erro nos cálculos: {str(e)}")
            st.stop()


def run():
    calcular_perda_carga_streamlit()


if __name__ == "__main__":
    run()