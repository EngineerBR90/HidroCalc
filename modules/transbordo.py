# transbordo.py
import math
import streamlit as st
import plotly.graph_objects as go
import numpy as np
from typing import Optional, Dict, Any, List
from tracking import track_access
from modules.data import BANCO_BOMBAS
from modules.calc_utils import ajustar_curva_pchip

def calcular_parametros_transbordo(altura_lamina_mm: float, comprimento_borda_m: float, area_piscina_m2: float) -> Dict[str, float]:
    """
    Calcula os parâmetros técnicos para o sistema de transbordo.
    """
    volume_cocho_litros: float = area_piscina_m2 * (altura_lamina_mm / 1000) * 3 * 1000
    area_lamina_m2: float = (altura_lamina_mm / 1000) * comprimento_borda_m
    vazao_necessaria: float = (1608 * (altura_lamina_mm / 1000) * comprimento_borda_m) * math.sqrt(2 * 9.81 * (altura_lamina_mm / 1000))
    
    return {
        "volume_cocho_litros": volume_cocho_litros,
        "area_lamina_m2": area_lamina_m2,
        "vazao_necessaria": vazao_necessaria
    }


def selecionar_bomba_transbordo(vazao_necessaria: float, pressao_mca: int) -> Optional[Dict[str, Any]]:
    """
    Seleciona a motobomba adequada para a vazão e pressão informadas.
    """
    selected_pump = None
    for bomba in BANCO_BOMBAS:
        key = f"vazao_{pressao_mca}_mca"
        vazao_pump = bomba.get(key)
        
        if vazao_pump is not None and vazao_pump >= vazao_necessaria:
            selected_pump = bomba
            break
    return selected_pump


@track_access("transbordo")
def run() -> None:
    """
    Executa o módulo de dimensionamento de transbordo (borda infinita).
    
    Calcula a vazão necessária para o efeito de borda infinita, volume do cocho,
    e selecio   na a motobomba adequada baseada na pressão selecionada.
    Exibe resultados e curva característica da bomba.
    """
    st.title("💧 Módulo Transbordo")
    st.markdown("---")
    
    # Container principal
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            # Inputs do usuário
            altura_lamina_mm: float = st.number_input(
                "Altura da lâmina (mm)",
                min_value=1.0,
                step=0.5,
                format="%.1f"
            )
            comprimento_borda_m: float = st.number_input(
                "Comprimento total da borda infinita (m)",
                min_value=1.0,
                step=1.0,
                format="%.1f"
            )
            area_piscina_m2: float = st.number_input(
                "Área da piscina (m²)",
                min_value=1.0,
                step=1.0,
                format="%.1f"
            )
            
        with col2:
            # Seleção de pressão
            possible_pressures: List[int] = sorted({2,4,6,8,10,12,14,16,18})
            pressao_mca: int = st.selectbox(
                "Pressão dimensionada (m.c.a)",
                options=possible_pressures,
                index=2  # Valor padrão 6 m.c.a
            )
    
    # Cálculos e resultados
    if st.button("Calcular", type="primary"):
        with st.spinner("Calculando..."):
            # Realiza cálculos usando a função extraída
            params = calcular_parametros_transbordo(altura_lamina_mm, comprimento_borda_m, area_piscina_m2)
            vazao_necessaria = params["vazao_necessaria"]
            volume_cocho_litros = params["volume_cocho_litros"]
            area_lamina_m2 = params["area_lamina_m2"]
            
            # Seleção da bomba usando a função extraída
            selected_pump = selecionar_bomba_transbordo(vazao_necessaria, pressao_mca)
            
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
                        pressoes: List[int] = []
                        vazoes: List[float] = []
                        for press in possible_pressures:
                            key = f'vazao_{press}_mca'
                            if selected_pump.get(key) is not None:
                                pressoes.append(press)
                                vazoes.append(selected_pump[key])

                        # Criar gráfico com Plotly
                        if pressoes and vazoes:
                            try:
                                # Converte para arrays numpy e ordena
                                x = np.array(vazoes)
                                y = np.array(pressoes)
                                sort_idx = np.argsort(x)
                                x_sorted = x[sort_idx]
                                y_sorted = y[sort_idx]

                                # Criar interpolação PCHIP
                                x_smooth, y_smooth, _ = ajustar_curva_pchip(x_sorted, y_sorted)

                                # Criar figura com Plotly
                                fig = go.Figure()

                                # Adicionar curva ajustada (suave)
                                fig.add_trace(go.Scatter(
                                    x=x_smooth,
                                    y=y_smooth,
                                    mode='lines',
                                    name='Curva Ajustada (PCHIP)',
                                    line=dict(color='#1f77b4', width=3)
                                ))

                                # Adicionar os pontos originais dos dados
                                fig.add_trace(go.Scatter(
                                    x=x_sorted,
                                    y=y_sorted,
                                    mode='markers',
                                    name='Dados do Fabricante',
                                    marker=dict(color='red', size=8)
                                ))

                                fig.update_layout(
                                    title=f'Curva da Motobomba {selected_pump["modelo"]}',
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
