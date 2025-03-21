# transbordo.py
import math
import streamlit as st
import plotly.graph_objects as go
import numpy as np

# noinspection PyInterpreter
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
    st.title("💧 Módulo Transbordo")
    st.markdown("---")
    
    # Container principal
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            # Inputs do usuário
            altura_lamina_mm = st.number_input(
                "Altura da lâmina (mm)",
                min_value=1.0,
                step=0.5,
                format="%.1f"

            )
            comprimento_borda_m = st.number_input(
                "Comprimento total da borda infinita (m)",
                min_value=1.0,
                step=1.0,
                format="%.1f"
            )
            area_piscina_m2 = st.number_input(
                "Área da piscina (m²)",
                min_value=1.0,
                step=1.0,
                format="%.1f"
            )
            
        with col2:
            # Seleção de pressão
            possible_pressures = sorted({2,4,6,8,10,12,14,16,18})
            pressao_mca = st.selectbox(
                "Pressão dimensionada (m.c.a)",
                options=possible_pressures,
                index=2  # Valor padrão 6 m.c.a
            )
    
    # Cálculos e resultados
    if st.button("Calcular", type="primary"):
        with st.spinner("Calculando..."):
            # Realiza cálculos
            volume_cocho_litros = area_piscina_m2 * (altura_lamina_mm / 1000) * 3 * 1000
            area_lamina_m2 = (altura_lamina_mm / 1000) * comprimento_borda_m
            vazao_necessaria = (1608 * (altura_lamina_mm / 1000) * comprimento_borda_m) * math.sqrt(2 * 9.81 * (altura_lamina_mm / 1000))
            
            # Seleção da bomba
            selected_pump = None
            for bomba in BANCO_BOMBAS:
                key = f"vazao_{pressao_mca}_mca"
                vazao_pump = bomba.get(key)
                
                if vazao_pump is not None and vazao_pump >= vazao_necessaria:
                    selected_pump = bomba
                    break
            
            # Exibe resultados
            st.success("**Resultados do Dimensionamento**")
            
            # Layout em colunas
            res_col1, res_col2 = st.columns([1, 2])
            
            with res_col1:
                st.metric("Vazão necessária para o efeito", f"{vazao_necessaria:.2f} m³/h")
                st.metric("Volume útil mínimo para o cocho", f"{volume_cocho_litros:.2f} L")
                st.metric("Área da lâmina", f"{area_lamina_m2:.4f} m²")
                
                if selected_pump:
                    st.success(f"**Motobomba Selecionada:** {selected_pump['modelo']}")
                    st.metric("Potência", f"{selected_pump['potencia_cv']} CV")
                else:
                    st.error("Nenhuma motobomba adequada encontrada!")
                
            with res_col2:
                if selected_pump:
                    with st.expander("🔍 Detalhes da Motobomba"):
                        st.write(f"**Especificações Técnicas:**")
                        st.write(f"- Modelo: {selected_pump['modelo']}")
                        st.write(f"- Potência: {selected_pump['potencia_cv']} CV")
                        st.write(f"- Vazão em {pressao_mca} m.c.a: {selected_pump[f'vazao_{pressao_mca}_mca']} m³/h")

                        st.write("**Curva da Motobomba:**")
                        # Preparar dados para o gráfico
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
                        if len(pressoes) >= 2 and len(vazoes) >= 2:
                            try:
                                from scipy.interpolate import PchipInterpolator

                                # Ordenar os dados por vazão
                                sorted_pairs = sorted(zip(vazoes, pressoes), key=lambda x: x[0])
                                x_sorted = np.array([p[0] for p in sorted_pairs])
                                y_sorted = np.array([p[1] for p in sorted_pairs])

                                # Criar interpolação PCHIP
                                pchip = PchipInterpolator(x_sorted, y_sorted)
                                x_smooth = np.linspace(min(x_sorted), max(x_sorted), 100)
                                y_smooth = pchip(x_smooth)

                                # Configurar gráfico
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(
                                    x=x_smooth,
                                    y=y_smooth,
                                    mode='lines',
                                    name='Curva Característica',
                                    line=dict(color='#1f77b4', width=3),
                                    hoverinfo='skip'
                                ))
                                fig.add_trace(go.Scatter(
                                    x=x_sorted,
                                    y=y_sorted,
                                    mode='markers+text',
                                    name='Dados do Fabricante',
                                    marker=dict(color='red', size=10),
                                    text=[f'({x}, {y})' for x, y in zip(x_sorted, y_sorted)],
                                    textposition='top center'
                                ))
                                fig.update_layout(
                                    title=f'Curva da Motobomba {bomba_selecionada["modelo"]}',
                                    xaxis_title='Vazão (m³/h)',
                                    yaxis_title='Pressão (m.c.a)',
                                    template='plotly_white',
                                    height=500,
                                    showlegend=True
                                )
                                st.plotly_chart(fig, use_container_width=True)

                            except Exception as e:
                                st.error(f"Erro ao gerar curva: {str(e)}")
                                # Fallback para interpolação linear
                                x_smooth = np.linspace(min(x_sorted), max(x_sorted), 100)
                                y_smooth = np.interp(x_smooth, x_sorted, y_sorted)
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(x=x_smooth, y=y_smooth, mode='lines', name='Interpolação Linear'))
                                fig.add_trace(go.Scatter(x=x_sorted, y=y_sorted, mode='markers', name='Dados do Fabricante'))
                                st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("Dados insuficientes para plotar a curva")


                else:
                    st.warning("""
                    **Recomendações:**
                    - Verificar se a pressão selecionada condiz com a perda de carga da linha
                    - Considerar associação de múltiplas bombas para atingir a vazão necessária
                    - Consultar outros modelos de motobombas (linha BMS por exemplo)
                    """)
            
            st.markdown("---")
    
    #if st.button("Voltar ao Menu Principal"):
    #    st.session_state.current_page = "Menu Principal"
    #    st.rerun()

# Para testar individualmente
if __name__ == "__main__":
    run()
