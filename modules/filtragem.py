# filtragem.py
import streamlit as st
from typing import Optional, Dict, Any
from tracking import track_access
from modules.data import BANCO_FILTROS


def selecionar_filtro(volume: float) -> Optional[Dict[str, Any]]:
    """
    Seleciona o filtro adequado da linha FM baseado no volume da piscina.
    """
    filtro_selecionado = None
    # Itera sobre os filtros ordenados por capacidade (volume_6h)
    for filtro in sorted(BANCO_FILTROS, key=lambda x: x["volume_6h"]):
        if filtro["volume_6h"] >= volume:
            filtro_selecionado = filtro
            break
    return filtro_selecionado


@track_access("filtragem")
def run() -> None:
    """
    Executa o módulo de dimensionamento de filtros.
    
    Permite ao usuário inserir o volume da piscina e seleciona o filtro 
    adequado da linha FM da Sodramar, considerando um tempo de recirculação 
    de 6 horas. Exibe as especificações técnicas do filtro e da motobomba recomendada.
    """
    st.title("💧 Módulo Filtragem")
    st.markdown("---")
    
    # Input do volume
    volume: float = st.number_input(
        "Digite o volume total da piscina (m³)",
        min_value=1.0,
        step=1.0,
        format="%.1f"
    )
    
    # Container para resultados
    result_container = st.container()
    
    if st.button("Calcular", type="primary"):
        # Seleção do filtro usando a função extraída
        filtro_selecionado = selecionar_filtro(volume)
        
        if not filtro_selecionado:
            st.error("Nenhum filto da linha FM atende a este volume de piscina. "
                     "Considerar associação entre dois ou mais filtros em paralelo "
                     "ou dimensionar modelo da linha FVP Sodramar")
            return

        # Exibição dos resultados
        with result_container:
            st.success("**Resultados do Dimensionamento**")
            
            # Layout em colunas
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.metric("Filtro Selecionado", filtro_selecionado["modelo"])
                st.metric("Vazão do conjunto MB+Filtro", f"{filtro_selecionado['volume_6h'] / 6:.2f} m³/h")
                st.metric("Motobomba Recomendada", filtro_selecionado["modelo_motobomba"])
            
            with col2:
                with st.expander("🔍 Detalhes Técnicos do Filtro"):
                    st.write(f"**Capacidade de filtragem:**")
                    st.write(f"- 6 horas: {filtro_selecionado['volume_6h']} m³")
                    st.write(f"- 8 horas: {filtro_selecionado['volume_8h']} m³")
                    
                    st.write(f"**Dimensões do filtro:**")
                    st.write(f"- Diâmetro: {filtro_selecionado['diametro_mm']} mm")
                    st.write(f"- Altura: {filtro_selecionado['altura_mm']} mm")
                    
                    st.write(f"**Carga de Areia:**")
                    st.write(f"- Total: {filtro_selecionado['carga_areia_kg']} kg")
                    st.write(f"- Sacos de 25kg: {filtro_selecionado['quant_sacos_25kg']}")
                    
                    st.write(f"**Peso bruto:**")
                    st.write(f"- Com areia: {filtro_selecionado['peso_bruto_com_areia_kg']} kg")
                    st.write(f"- Sem areia: {filtro_selecionado['peso_bruto_sem_areia_kg']} kg")
            
            st.markdown("---")
    
    #if st.button("Voltar ao Menu Principal"):
    #    st.session_state.current_page = "Menu Principal"
    #   st.rerun()

# Para testar individualmente
if __name__ == "__main__":
    run()
