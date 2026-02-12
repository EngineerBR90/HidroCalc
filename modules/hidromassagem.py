# modules/hidromassagem.py
import math
import streamlit as st
import plotly.graph_objects as go
import numpy as np
from typing import Optional, Dict, Any, List
from tracking import track_access
from modules.data import BANCO_BOMBAS
from modules.calc_utils import ajustar_curva_pchip

@track_access("hidromassagem")  # ← Decorador aplicado
def run() -> None:
    """
    Executa o módulo de dimensionamento de Hidromassagem.
    
    Permite selecionar o tipo de dispositivo (SODRAMAR ou ALBACETE), 
    quantidade de dispositivos e pressão desejada. 
    Calcula a vazão total e seleciona a motobomba adequada.
    Exibe resultados e curvas de desempenho.
    """
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
            quantidade: int = st.number_input(
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
            pressao_selecionada: int = st.number_input(
                "Pressão de dimensionamento (m.c.a):",
                min_value=4,
                max_value=18,
                value=8,
                step=2,
                format="%d"
            )

    bomba_selecionada: Optional[Dict[str, Any]] = None

    # Cálculos
    if st.button("Calcular", type="primary"):
        with st.spinner("Processando..."):
            # 4. Cálculo corrigido (SODRAMAR maiúsculo)
            vazao_por_dispositivo: float = 4.5 if st.session_state.tipo_dispositivo == "SODRAMAR" else 3.3
            vazao_necessaria: float = quantidade * vazao_por_dispositivo

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

    if bomba_selecionada:
        with st.expander("🔍 Detalhes da Motobomba"):
            st.write(f"**Especificações Técnicas:**")
            st.write(f"- Modelo: {bomba_selecionada['modelo']}")
            st.write(f"- Potência: {bomba_selecionada['potencia_cv']} CV")
            st.write(
                f"- Vazão em {pressao_selecionada} m.c.a: {bomba_selecionada[f'vazao_{pressao_selecionada}_mca']} m³/h")
            st.write("**Curva da Motobomba:**")

            # Preparar dados para o gráfico
            pressoes: List[int] = []
            vazoes: List[float] = []
            possible_pressures = list(range(2, 19, 2))  # De 2 a 18 mca
            for press in possible_pressures:
                key = f'vazao_{press}_mca'
                if bomba_selecionada.get(key) is not None:
                    pressoes.append(press)
                    vazoes.append(bomba_selecionada[key])

            # Criar gráfico com Plotly
            if len(pressoes) >= 2 and len(vazoes) >= 2:
                try:
                    # Ordenar os dados por vazão
                    sorted_pairs = sorted(zip(vazoes, pressoes), key=lambda x: x[0])
                    x_sorted = np.array([p[0] for p in sorted_pairs])
                    y_sorted = np.array([p[1] for p in sorted_pairs])

                    # Criar interpolação PCHIP
                    x_smooth, y_smooth, _ = ajustar_curva_pchip(x_sorted, y_sorted)

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
            else:
                st.warning("Dados insuficientes para plotar a curva")

    # Integração com Projeto Completo
    #if "projeto" in st.session_state and st.button("Salvar no Projeto Completo"):
    #    equipamento = {
    #       "sistema": "Hidromassagem",
    #        "tipo": tipo_dispositivo,
    #        "quantidade": quantidade,
    #        "vazao": vazao_necessaria if 'vazao_necessaria' in locals() else None,
    #        "pressao": pressao_selecionada,
    #        "bomba": bomba_selecionada['modelo'] if bomba_selecionada else None
    #    }
    #    st.session_state.projeto["equipamentos"]["Hidromassagem"] = equipamento
    #    st.success("Configuração salva no projeto!")


if __name__ == "__main__":
    run()