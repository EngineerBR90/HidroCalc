# modules/hidromassagem.py
import streamlit as st
import math
import plotly.graph_objects as go
import numpy as np

# Constantes hidráulicas
VISCOSIDADE_CINEMATICA_AGUA = 1.004e-6  # m²/s (20°C)
RUGOSIDADE_PVC = 0.0015  # mm (rugosidade absoluta)
GRAVIDADE = 9.81  # m/s²

BANCO_BOMBAS = [
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
        "vazao_4_mca": 19.38,
        "vazao_6_mca": 19.88,
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
    },
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


def calcular_fator_atrito(re, diametro_mm):
    """Calcula o fator de atrito usando o método de Swamee-Jain"""
    diametro_m = diametro_mm / 1000
    rugosidade_relativa = RUGOSIDADE_PVC / diametro_m

    if re < 2000:
        return 64 / re if re > 0 else 0.02

    return 0.25 / (math.log10(rugosidade_relativa / 3.7 + 5.74 / re ** 0.9)) ** 2


def calcular_perda_carga(comprimento, diametro, vazao_m3h):
    """Calcula a perda de carga total com margem de segurança"""
    try:
        # Conversão de unidades
        diametro_m = diametro / 1000
        vazao_m3s = vazao_m3h / 3600
        area = math.pi * (diametro_m ** 2) / 4
        velocidade = vazao_m3s / area

        # Cálculo do número de Reynolds
        re = velocidade * diametro_m / VISCOSIDADE_CINEMATICA_AGUA

        # Fator de atrito
        f = calcular_fator_atrito(re, diametro)

        # Perda de carga distribuída
        hf = f * (comprimento / diametro_m) * (velocidade ** 2) / (2 * GRAVIDADE)

        # Margem de segurança de 15% para perdas localizadas
        return hf * 1.15

    except Exception as e:
        st.error(f"Erro no cálculo: {str(e)}")
        return 0


def run():
    st.title("💧 Módulo de Hidromassagem")
    st.markdown("---")

    # Inicialização do estado
    if 'tipo_dispositivo' not in st.session_state:
        st.session_state.tipo_dispositivo = "SODRAMAR"

    # Container principal
    with st.container():
        col1, col2 = st.columns(2)

        # Coluna SODRAMAR
        with col1:
        # Interface de seleção mantida igual...
        # ... (código existente)

        # Coluna ALBACETE
        with col2:
    # Interface de seleção mantida igual...
    # ... (código existente)

    # Cálculos principais
    if st.button("Calcular", type="primary"):
        with st.spinner("Processando..."):
            # Cálculos iniciais mantidos...
            # ... (código existente até a seleção da bomba)

            # Exibição dos resultados
            st.success("**Resultados do Dimensionamento**")
            cols = st.columns(2)
            with cols[0]:
                st.metric("Vazão Total Necessária", f"{vazao_necessaria:.1f} m³/h")
                st.metric("Pressão Selecionada", f"{pressao_selecionada} m.c.a")

            with cols[1]:
                if bomba_selecionada:
                    st.success("**Motobomba Selecionada**")
                    st.metric("Modelo", bomba_selecionada['modelo'])
                    st.metric("Potência", f"{bomba_selecionada['potencia_cv']} CV")

                    # Nova seção de verificação hidráulica
                    with st.expander("🔍 Verificação Hidráulica Detalhada", expanded=False):
                        st.markdown("### Parâmetros da Tubulação")

                        col3, col4 = st.columns(2)
                        with col3:
                            diametro = st.selectbox(
                                "Diâmetro interno (mm):",
                                options=[25, 32, 40, 50, 60, 75, 85, 110],
                                index=2
                            )
                            comprimento = st.number_input(
                                "Comprimento total (m):",
                                min_value=1.0,
                                value=10.0,
                                step=0.5
                            )

                        with col4:
                            altura_estatica = st.number_input(
                                "Altura estática (m):",
                                min_value=0.0,
                                value=2.0,
                                step=0.1
                            )
                            temp_agua = st.number_input(
                                "Temperatura da água (°C):",
                                min_value=0.0,
                                max_value=40.0,
                                value=20.0,
                                step=0.5
                            )

                        if st.button("Calcular Perdas", key="btn_perdas"):
                            resultados = {
                                'perda_carga': calcular_perda_carga(comprimento, diametro, vazao_necessaria),
                                'altura_estatica': altura_estatica
                            }

                            st.markdown("### Resultados da Verificação")
                            cols_res = st.columns(2)
                            with cols_res[0]:
                                st.metric("Perda de carga calculada", f"{resultados['perda_carga']:.2f} mca")
                                st.metric("Altura estática", f"{resultados['altura_estatica']:.2f} m")

                            with cols_res[1]:
                                pressao_total = resultados['perda_carga'] + resultados['altura_estatica']
                                st.metric("Pressão total requerida", f"{pressao_total:.2f} mca")
                                st.metric("Margem de segurança",
                                          f"{(pressao_selecionada - pressao_total):.2f} mca",
                                          delta_color="inverse" if pressao_total > pressao_selecionada else "normal")

                            if pressao_total > pressao_selecionada:
                                st.error("Atenção: Pressão requerida excede a capacidade da bomba!")
                                st.markdown("""
                                **Ações recomendadas:**
                                - Aumente o diâmetro da tubulação
                                - Reduza o comprimento da tubulação
                                - Considere uma bomba mais potente
                                """)
                            else:
                                st.success("Sistema dimensionado corretamente!")

                    # Seção original de detalhes da bomba mantida...
                    # ... (código existente do expander da bomba)

                else:
            # Mensagem de erro mantida...
            # ... (código existente)

    # Integração com Projeto Completo mantida...
    # ... (código existente)


if __name__ == "__main__":
    run()