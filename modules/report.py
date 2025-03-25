import streamlit as st
import pandas as pd
from tracking import get_supabase  # Importe a função de conexão

def run():
    st.title("📊 Relatórios Administrativos")
    
    # Verificar se é a Kiara (ou outro admin)
    if st.session_state.get("username") != "kiara":
        st.error("Acesso restrito")
        return
    
    try:
        supabase = get_supabase()
        data = supabase.table('access_logs').select("*").execute().data
        df = pd.DataFrame(data)
        
        # Filtros
        st.sidebar.subheader("Filtros")
        module_filter = st.sidebar.selectbox("Módulo", ["Todos"] + list(df['module'].unique()))
        
        if module_filter != "Todos":
            df = df[df['module'] == module_filter]
        
        # Visualização
        st.subheader("Dados de Acesso")
        st.dataframe(df.sort_values('created_at', ascending=False))
        
        # Métricas
        st.subheader("Estatísticas")
        col1, col2 = st.columns(2)
        col1.metric("Total de Acessos", len(df))
        col2.metric("Tempo Médio", f"{df['duration'].mean():.1f} segundos")
        
        # Download
        st.download_button(
            "Exportar para CSV",
            df.to_csv(index=False).encode('utf-8'),
            "acessos_hidrocalc.csv",
            "text/csv"
        )
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")