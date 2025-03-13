# filtragem.py
import streamlit as st

BANCO_FILTROS = [
    {
        "modelo": "FM-25",
        "volume_6h": 14,
        "volume_8h": 19,
        "carga_areia_kg": 18,
        "quant_sacos_25kg": 1,
        "diametro_mm": 325,
        "altura_mm": 735,
        "peso_bruto_com_areia_kg": 23.4,
        "peso_bruto_sem_areia_kg": 5.4,
        "modelo_motobomba": "BMC-25 M"
    },
    {
        "modelo": "FM-30",
        "volume_6h": 21,
        "volume_8h": 28,
        "carga_areia_kg": 25,
        "quant_sacos_25kg": 1,
        "diametro_mm": 335,
        "altura_mm": 583,
        "peso_bruto_com_areia_kg": 34.13,
        "peso_bruto_sem_areia_kg": 9.13,
        "modelo_motobomba": "BMC-25 M"
    },
    {
        "modelo": "FM-36",
        "volume_6h": 30,
        "volume_8h": 40,
        "carga_areia_kg": 40,
        "quant_sacos_25kg": 2,
        "diametro_mm": 380,
        "altura_mm": 772,
        "peso_bruto_com_areia_kg": 50.7,
        "peso_bruto_sem_areia_kg": 10.7,
        "modelo_motobomba": "BMC-33 M"
    },
    {
        "modelo": "FM-40",
        "volume_6h": 37,
        "volume_8h": 50,
        "carga_areia_kg": 125,
        "quant_sacos_25kg": 5,
        "diametro_mm": 430,
        "altura_mm": 835,
        "peso_bruto_com_areia_kg": 142.98,
        "peso_bruto_sem_areia_kg": 17.98,
        "modelo_motobomba": "BMC-50 M"
    },
    {
        "modelo": "FM-50",
        "volume_6h": 59,
        "volume_8h": 78,
        "carga_areia_kg": 65,
        "quant_sacos_25kg": 3,
        "diametro_mm": 525,
        "altura_mm": 950,
        "peso_bruto_com_areia_kg": 77.55,
        "peso_bruto_sem_areia_kg": 12.55,
        "modelo_motobomba": "BMC-75 M"
    },
    {
        "modelo": "FM-60",
        "volume_6h": 85,
        "volume_8h": 113,
        "carga_areia_kg": 200,
        "quant_sacos_25kg": 8,
        "diametro_mm": 645,
        "altura_mm": 1000,
        "peso_bruto_com_areia_kg": 221.42,
        "peso_bruto_sem_areia_kg": 21.42,
        "modelo_motobomba": "BMC-100 M"
    },
    {
        "modelo": "FM-75",
        "volume_6h": 132,
        "volume_8h": 176,
        "carga_areia_kg": 300,
        "quant_sacos_25kg": 12,
        "diametro_mm": 770,
        "altura_mm": 1140,
        "peso_bruto_com_areia_kg": 335.74,
        "peso_bruto_sem_areia_kg": 35.74,
        "modelo_motobomba": "BM-150 T"
    },
    {
        "modelo": "FM-100",
        "volume_6h": 234,
        "volume_8h": 312,
        "carga_areia_kg": 525,
        "quant_sacos_25kg": 21,
        "diametro_mm": 1120,
        "altura_mm": 1215,
        "peso_bruto_com_areia_kg": 579.8,
        "peso_bruto_sem_areia_kg": 54.8,
        "modelo_motobomba": "BM-300 T"
    }
]

def run():
    st.title("Módulo Filtragem")
    st.markdown("---")
    
    # Input do volume
    volume = st.number_input(
        "Digite o volume total da piscina (m³)",
        min_value=1.0,
        step=0.5,
        format="%.1f"
    )
    
    # Container para resultados
    result_container = st.container()
    
    if st.button("Calcular", type="primary"):
        # Seleção do filtro
        filtro_selecionado = None
        for filtro in sorted(BANCO_FILTROS, key=lambda x: x["volume_6h"]):
            if filtro["volume_6h"] >= volume:
                filtro_selecionado = filtro

                break
        
        if not filtro_selecionado:
            st.error("Nenhum filto da linha FM atende a este volume de piscina. Considerar associação entre dois ou mais filtros em paralelo ou dimensionar modelo da linha FVP Sodramar")
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
    
    if st.button("Voltar ao Menu Principal"):
        st.session_state.current_page = "Menu Principal"
        st.rerun()

# Para testar individualmente
if __name__ == "__main__":
    run()
