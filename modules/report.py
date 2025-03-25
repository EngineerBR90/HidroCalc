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

        # Inicializar filtros na sessão
        if 'filtro_modulo' not in st.session_state:
            st.session_state.filtro_modulo = "Todos"
        if 'filtro_usuario' not in st.session_state:
            st.session_state.filtro_usuario = "Todos"

        # Seção de filtros (usando session_state para manter o estado)
        with st.expander("🔍 Filtros", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                # Lista de módulos com contagem
                modulos = df['module'].value_counts().reset_index()
                modulo_options = ["Todos"] + modulos['module'].tolist()
                novo_modulo = st.selectbox(
                    "Selecionar Módulo:",
                    modulo_options,
                    index=modulo_options.index(st.session_state.filtro_modulo)
                )
                st.session_state.filtro_modulo = novo_modulo

            with col2:
                # Lista de usuários com contagem
                usuarios = df['username'].value_counts().reset_index()
                usuario_options = ["Todos"] + usuarios['username'].tolist()
                novo_usuario = st.selectbox(
                    "Selecionar Usuário:",
                    usuario_options,
                    index=usuario_options.index(st.session_state.filtro_usuario)
                )
                st.session_state.filtro_usuario = novo_usuario

        # Aplicar filtros
        df_filtrado = df.copy()
        if st.session_state.filtro_modulo != "Todos":
            df_filtrado = df_filtrado[df_filtrado['module'] == st.session_state.filtro_modulo]
        if st.session_state.filtro_usuario != "Todos":
            df_filtrado = df_filtrado[df_filtrado['username'] == st.session_state.filtro_usuario]

        # Seção de visualização
        with st.container():
            st.subheader("Visão Consolidada")

            # Formatar data corretamente
            df_filtrado['data'] = pd.to_datetime(df_filtrado['created_at']).dt.strftime('%d/%m/%Y %H:%M')

            # Tabela principal
            st.dataframe(
                df_filtrado[['data', 'username', 'module']],
                column_config={
                    "data": "Data/Hora",
                    "username": "Usuário",
                    "module": "Módulo"
                },
                use_container_width=True,
                height=400,
                hide_index=True
            )

        # Seção de exportação
        with st.container():
            st.subheader("Exportação de Dados")

            col1, col2 = st.columns(2)

            with col1:
                # CSV Bruto formatado para Excel
                st.write("**Exportar Dados Brutos**")
                csv_bruto = df_filtrado[['created_at', 'username', 'module']].to_csv(
                    index=False,
                    sep=";",
                    date_format='%Y-%m-%d %H:%M:%S'
                )
                st.download_button(
                    label="Baixar CSV Bruto",
                    data=csv_bruto,
                    file_name="acessos_brutos.csv",
                    mime="text/csv",
                    help="Formato ideal para importar no Excel"
                )

            with col2:
                # CSV Estruturado
                st.write("**Exportar Dados Agregados**")
                df_pivot = pd.crosstab(
                    index=df_filtrado['username'],
                    columns=df_filtrado['module'],
                    margins=True,
                    margins_name='TOTAL'
                )
                csv_estruturado = df_pivot.to_csv(sep=";", decimal=",")
                st.download_button(
                    label="Baixar CSV Estruturado",
                    data=csv_estruturado,
                    file_name="acessos_agregados.csv",
                    mime="text/csv",
                    help="Visão consolidada por usuário e módulo"
                )

    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")


if __name__ == "__main__":
    run()