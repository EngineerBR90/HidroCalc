# modules/report.py
import streamlit as st
import pandas as pd
from supabase import create_client
import matplotlib.pyplot as plt


def run():
    st.title("📊 Relatórios de Acesso")

    # Verificar permissões
    if st.session_state.get("username") != "kiara":
        st.error("Acesso restrito à equipe de desenvolvimento")
        return

    try:
        # Inicializar cliente Supabase
        supabase = create_client(
            st.secrets.supabase.url,
            st.secrets.supabase.key
        )

        # Carregar dados
        data = supabase.table('access_logs').select("*").execute().data
        df = pd.DataFrame(data)

        # Armazenar filtros na sessão para evitar recarregamento
        if 'filtro_modulo' not in st.session_state:
            st.session_state.filtro_modulo = "Todos"

        if 'filtro_usuario' not in st.session_state:
            st.session_state.filtro_usuario = "Todos"

        # Seção de filtros
        with st.container():
            st.subheader("Filtros Avançados")
            col1, col2 = st.columns(2)

            with col1:
                novo_filtro_modulo = st.selectbox(
                    "Módulo:",
                    ["Todos"] + sorted(df['module'].unique()),
                    key="select_modulo"
                )
                st.session_state.filtro_modulo = novo_filtro_modulo

            with col2:
                novo_filtro_usuario = st.selectbox(
                    "Usuário:",
                    ["Todos"] + sorted(df['username'].unique()),
                    key="select_usuario"
                )
                st.session_state.filtro_usuario = novo_filtro_usuario

        # Aplicar filtros
        df_filtrado = df.copy()
        if st.session_state.filtro_modulo != "Todos":
            df_filtrado = df_filtrado[df_filtrado['module'] == st.session_state.filtro_modulo]

        if st.session_state.filtro_usuario != "Todos":
            df_filtrado = df_filtrado[df_filtrado['username'] == st.session_state.filtro_usuario]

        # Métricas principais
        with st.container():
            st.subheader("Indicadores Chave")
            col_metrics = st.columns(3)

            with col_metrics[0]:
                st.metric("Acessos Totais", len(df_filtrado))

            with col_metrics[1]:
                st.metric("Módulos Únicos", df_filtrado['module'].nunique())

            with col_metrics[2]:
                st.metric("Usuários Únicos", df_filtrado['username'].nunique())

        # Análise de rankings
        with st.container():
            st.subheader("Análise de Engagement")
            col_rankings = st.columns(2)

            with col_rankings[0]:
                st.write("**Top Módulos**")
                modulos = df_filtrado['module'].value_counts().reset_index()
                modulos.columns = ['Módulo', 'Acessos']
                st.dataframe(
                    modulos.style
                    .bar(color='#5fba7d', subset=['Acessos']),
                    use_container_width=True,
                    hide_index=True
                )

            with col_rankings[1]:
                st.write("**Top Usuários**")
                usuarios = df_filtrado['username'].value_counts().reset_index()
                usuarios.columns = ['Usuário', 'Acessos']
                st.dataframe(
                    usuarios.style
                    .bar(color='#5f99ba', subset=['Acessos']),
                    use_container_width=True,
                    hide_index=True
                )

        # Visualização temporal
        with st.container():
            st.subheader("Distribuição Temporal")
            df_temp = df_filtrado.copy()
            df_temp['data'] = pd.to_datetime(df_temp['created_at']).dt.date

            if not df_temp.empty:
                fig, ax = plt.subplots()
                df_temp.groupby('data').size().plot(
                    kind='line',
                    ax=ax,
                    marker='o',
                    color='#5fba7d'
                )
                ax.set_title("Acessos Diários")
                ax.set_xlabel("Data")
                ax.set_ylabel("Número de Acessos")
                st.pyplot(fig)
            else:
                st.warning("Sem dados para o período selecionado")

        # Exportação de dados
        with st.container():
            st.subheader("Exportação de Dados")

            # Criar versão pivotada
            df_pivot = pd.crosstab(
                index=df_filtrado['username'],
                columns=df_filtrado['module'],
                margins=True,
                margins_name='TOTAL'
            ).reset_index()

            col_export = st.columns([2, 1, 1])

            with col_export[0]:
                st.write("**Visualização Prévia**")
                st.dataframe(
                    df_pivot.style
                    .background_gradient(cmap='Blues', subset=df_pivot.columns[1:-1])
                    .format(precision=0),
                    height=300,
                    use_container_width=True
                )

            with col_export[1]:
                st.write("**Exportar Bruto**")
                st.download_button(
                    label="CSV Simples",
                    data=df_filtrado.to_csv(index=False, sep=';').encode('utf-8'),
                    file_name="acessos_brutos.csv",
                    mime="text/csv"
                )

            with col_export[2]:
                st.write("**Exportar Consolidado**")
                st.download_button(
                    label="CSX Estruturado",
                    data=df_pivot.to_csv(index=False, sep=';').encode('utf-8'),
                    file_name="acessos_estruturados.csv",
                    mime="text/csv"
                )

    except Exception as e:
        st.error(f"Erro na conexão com o banco de dados: {str(e)}")


if __name__ == "__main__":
    run()