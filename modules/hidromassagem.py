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
            # Centralização da imagem
            left, center = st.columns([1, 4])
            with center:
                st.image("assets/disp_hidro_sodramar.png", width=200)

            # Botão de seleção
            if st.session_state.tipo_dispositivo == "SODRAMAR":
                btn_style = "primary"
                btn_label = "✔️ SODRAMAR (SELECIONADO)"
            else:
                btn_style = "secondary"
                btn_label = "Selecionar SODRAMAR"

            if st.button(btn_label, key="btn_sod", type=btn_style, use_container_width=True):
                st.session_state.tipo_dispositivo = "SODRAMAR"
                st.rerun()

            # Input quantidade
            quantidade = st.number_input(
                "Quantidade de dispositivos:",
                min_value=1,
                max_value=99,
                value=1,
                step=1
            )

        # Coluna ALBACETE
        with col2:
            # Centralização da imagem
            left, center = st.columns([1, 4])
            with center:
                st.image("assets/disp_hidro_albacete.png", width=200)

            # Botão de seleção
            if st.session_state.tipo_dispositivo == "ALBACETE":
                btn_style = "primary"
                btn_label = "✔️ ALBACETE (SELECIONADO)"
            else:
                btn_style = "secondary"
                btn_label = "Selecionar ALBACETE"

            if st.button(btn_label, key="btn_alb", type=btn_style, use_container_width=True):
                st.session_state.tipo_dispositivo = "ALBACETE"
                st.rerun()

            # Input pressão
            pressao_selecionada = st.number_input(
                "Pressão de dimensionamento (m.c.a):",
                min_value=4,
                max_value=18,
                value=4,
                step=2,
                format="%d"
            )

    # Cálculos
    if st.button("Calcular", type="primary"):
        with st.spinner("Processando..."):
            # 4. Cálculo corrigido (SODRAMAR maiúsculo)
            vazao_por_dispositivo = 4.5 if st.session_state.tipo_dispositivo == "SODRAMAR" else 3.3
            vazao_necessaria = quantidade * vazao_por_dispositivo

            # 5. Seleção da motobomba
            bomba_selecionada = None
            for bomba in sorted(BANCO_BOMBAS, key=lambda x: x['potencia_cv']):
                chave_vazao = f'vazao_{pressao_selecionada}_mca'
                vazao_bomba = bomba.get(chave_vazao)

                if vazao_bomba and vazao_bomba >= vazao_necessaria:
                    bomba_selecionada = bomba
                    break

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
                    with st.expander("🔍 Detalhes da Motobomba"):
                        st.write(f"**Especificações Técnicas:**")
                        st.write(f"- Modelo: {bomba_selecionada['modelo']}")
                        st.write(f"- Potência: {bomba_selecionada['potencia_cv']} CV")
                        st.write(
                            f"- Vazão em {pressao_selecionada} m.c.a: {bomba_selecionada[f'vazao_{pressao_selecionada}_mca']} m³/h")

                        st.write("**Curva da Motobomba:**")
                        # Preparar dados para o gráfico
                        pressoes = []
                        vazoes = []
                        possible_pressures = list(range(2, 19, 2))  # De 2 a 18 mca
                        for press in possible_pressures:
                            key = f'vazao_{press}_mca'
                            if bomba_selecionada.get(key) is not None:
                                pressoes.append(press)
                                vazoes.append(bomba_selecionada[key])

                        # Criar gráfico com Plotly
                        if pressoes and vazoes:
                            try:
                                # Converte para arrays numpy e ordena
                                x = np.array(vazoes)
                                y = np.array(pressoes)
                                sort_idx = np.argsort(x)
                                x_sorted = x[sort_idx]
                                y_sorted = y[sort_idx]

                                # Cria interpolação polinomial de 3º grau
                                coeffs = np.polyfit(x_sorted, y_sorted, 3)
                                poly = np.poly1d(coeffs)

                                # Gera pontos suaves
                                x_smooth = np.linspace(min(x_sorted), max(x_sorted), 100)
                                y_smooth = poly(x_smooth)

                                # Cria figura
                                fig = go.Figure()

                                # Curva suave
                                fig.add_trace(go.Scatter(
                                    x=x_smooth,
                                    y=y_smooth,
                                    mode='lines',
                                    name='Curva Interpolada',
                                    line=dict(color='#1f77b4', width=3)
                                ))

                                # Pontos originais
                                fig.add_trace(go.Scatter(
                                    x=x_sorted,
                                    y=y_sorted,
                                    mode='markers',
                                    name='Dados do Fabricante',
                                    marker=dict(color='red', size=8)
                                ))

                                fig.update_layout(
                                    title=f'Curva da Motobomba {bomba_selecionada["modelo"]}',
                                    xaxis_title='Vazão (m³/h)',
                                    yaxis_title='Pressão (m.c.a)',
                                    template='plotly_white',
                                    height=500
                                )

                                st.plotly_chart(fig, use_container_width=True)

                            except Exception as e:
                                st.error(f"Erro ao gerar curva: {str(e)}")
                        else:
                            st.warning("Dados insuficientes para plotar a curva")
                else:
                    st.error("Nenhuma motobomba adequada encontrada!")
                    st.warning("""
                    **Sugestões:**
                    - Verifique se a pressão selecionada está correta
                    - Considere dividir em dois ou mais sistemas com acionamentos independentes
                    - Considere utilizar múltiplas MBs em paralelo. Para tal é imprescindível dimensionar 
                    linha de sucção e verificar velocidade de fluxo ≤1,80 m/s.
                    - Verifique modelos com maior capacidade
                    """)

            st.markdown("---")

    # Integração com Projeto Completo
    if "projeto" in st.session_state and st.button("Salvar no Projeto Completo"):
        equipamento = {
            "sistema": "Hidromassagem",
            "tipo": st.session_state.tipo_dispositivo,
            "quantidade": quantidade,
            "vazao": vazao_necessaria,
            "pressao": pressao_selecionada,
            "bomba": bomba_selecionada['modelo'] if bomba_selecionada else None
        }
        st.session_state.projeto["equipamentos"]["Hidromassagem"] = equipamento
        st.success("Configuração salva no projeto!")


if __name__ == "__main__":
    run()