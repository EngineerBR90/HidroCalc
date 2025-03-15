# modules/hidromassagem.py
import streamlit as st
import math
import streamlit as st
import plotly.graph_objects as go
import numpy as np

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


def run():
    st.title("💧 Módulo de Hidromassagem")
    st.markdown("---")

    # Inicialização do estado
    if 'tipo_dispositivo' not in st.session_state:
        st.session_state.tipo_dispositivo = "SODRAMAR"

    # Container principal
    with st.container():
        # Dispositivo Sodramar
        with st.container():
            cols = st.columns([3, 1])  # Proporção imagem/botão
            with cols[0]:
                st.image("assets/disp_hidro_sodramar.png", use_container_width=True)
            with cols[1]:
                if st.session_state.tipo_dispositivo == "SODRAMAR":
                    btn = st.button("✔️ SELECIONADO", type="primary", use_container_width=True)
                else:
                    btn = st.button("Selecionar", type="secondary", use_container_width=True)
                if btn:
                    st.session_state.tipo_dispositivo = "SODRAMAR"
                    st.rerun()

        # Dispositivo Albacete
        with st.container():
            cols = st.columns([3, 1])  # Mesma proporção
            with cols[0]:
                st.image("assets/disp_hidro_albacete.png", use_container_width=True)
            with cols[1]:
                if st.session_state.tipo_dispositivo == "ALBACETE":
                    btn = st.button("✔️ SELECIONADO", type="primary", use_container_width=True)
                else:
                    btn = st.button("Selecionar", type="secondary", use_container_width=True)
                if btn:
                    st.session_state.tipo_dispositivo = "ALBACETE"
                    st.rerun()

        # Inputs
        col1, col2 = st.columns(2)
        with col1:
            quantidade = st.number_input(
                "Quantidade de dispositivos:",
                min_value=1,
                max_value=99,
                value=1,
                step=1
            )
        with col2:
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
            "tipo": tipo_dispositivo,
            "quantidade": quantidade,
            "vazao": vazao_necessaria if 'vazao_necessaria' in locals() else None,
            "pressao": pressao_selecionada,
            "bomba": bomba_selecionada['modelo'] if bomba_selecionada else None
        }
        st.session_state.projeto["equipamentos"]["Hidromassagem"] = equipamento
        st.success("Configuração salva no projeto!")


if __name__ == "__main__":
    run()