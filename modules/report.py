# modules/report.py
import streamlit as st
import pandas as pd
from supabase import create_client


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

        ## CORREÇÃO 1: Inicialização correta dos filtros na sessão
        session_keys = {
            'filtro_modulo': "Todos",
            'filtro_usuario': "Todos"
        }

        for key, default in session_keys.items():
            if key not in st.session_state:
                st.session_state[key] = default

        # Seção de filtros
        with st.container():
            st.subheader("Filtros")
            col1, col2 = st.columns(2)

            with col1:
                ## CORREÇÃO 2: Manter estado do filtro de módulo
                novo_modulo = st.selectbox(
                    "Módulo:",
                    ["Todos"] + sorted(df['module'].unique()),
                    index=0 if st.session_state.filtro_modulo == "Todos" else 1,
                    key="filtro_modulo_selector"
                )
                st.session_state.filtro_modulo = novo_modulo

            with col2:
                ## CORREÇÃO 3: Manter estado do filtro de usuário
                novo_usuario = st.selectbox(
                    "Usuário:",
                    ["Todos"] + sorted(df['username'].unique()),
                    index=0 if st.session_state.filtro_usuario == "Todos" else 1,
                    key="filtro_usuario_selector"
                )
                st.session_state.filtro_usuario = novo_usuario

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

            metrics = [
                ("Acessos Totais", len(df_filtrado)),
                ("Módulos Únicos", df_filtrado['module'].nunique()),
                ("Usuários Únicos", df_filtrado['username'].nunique())
            ]

            for (label, value), col in zip(metrics, col_metrics):
                with col:
                    st.metric(label, value)

        # Análise de rankings
        with st.container():
            st.subheader("Rankings")
            col_rankings = st.columns(2)

            with col_rankings[0]:
                st.markdown("**Top 5 Módulos**")
                modulos = df_filtrado['module'].value_counts().nlargest(5)
                st.dataframe(
                    modulos.reset_index().rename(columns={'index': 'Módulo', 'module': 'Acessos'}),
                    hide_index=True,
                    use_container_width=True
                )

            with col_rankings[1]:
                st.markdown("**Top 5 Usuários**")
                usuarios = df_filtrado['username'].value_counts().nlargest(5)
                st.dataframe(
                    usuarios.reset_index().rename(columns={'index': 'Usuário', 'username': 'Acessos'}),
                    hide_index=True,
                    use_container_width=True
                )

        # Exportação de dados
        with st.container():
            st.subheader("Exportação de Dados")
            col1, col2 = st.columns(2)

            ## CORREÇÃO 4: Formatação CSV para Excel
            with col1:
                st.markdown("**Dados Brutos**")
                csv_bruto = df_filtrado[['created_at', 'username', 'module']].rename(columns={
                    'created_at': 'Data_Hora',
                    'username': 'Usuario',
                    'module': 'Modulo'
                }).to_csv(index=False, sep=';', date_format='%Y-%m-%d %H:%M:%S')

                st.download_button(
                    label="Baixar CSV Bruto",
                    data=csv_bruto,
                    file_name="acessos_brutos.csv",
                    mime="text/csv",
                    help="Formato ideal para Excel (colunas separadas)"
                )

            with col2:
                st.markdown("**Dados Agregados**")
                df_pivot = pd.crosstab(
                    index=df_filtrado['username'],
                    columns=df_filtrado['module'],
                    margins=True,
                    margins_name='TOTAL'
                )
                csv_agregado = df_pivot.to_csv(sep=';', decimal=',')

                st.download_button(
                    label="Baixar CSV Agregado",
                    data=csv_agregado,
                    file_name="acessos_agregados.csv",
                    mime="text/csv",
                    help="Visão consolidada por usuário e módulo"
                )

    except Exception as e:
        st.error(f"Erro na conexão com o banco de dados: {str(e)}")


if __name__ == "__main__":
    run()