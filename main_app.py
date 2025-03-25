import streamlit as st
import pandas as pd
import numpy as npe
import bcrypt
from tracking import track_access
from modules import filtragem, transbordo, hidromassagem, perda_carga, memoria, database_equipamentos

# Verifica se o usuário está autenticado
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🔒 Você precisa fazer login para acessar o aplicativo.")
    if st.button("Ir para a tela de login"):
        import login  # Certifique-se de que login.py está na raiz do projeto
        login.login()  # Chama a função de login para exibir a tela de autenticação
    st.stop()  # Interrompe a execução do main_app.py


def main():
    st.set_page_config(
        page_title="💧 HidroCalc Piscinas",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Sidebar Navigation
    with st.sidebar:
        # Título e navegação no topo da sidebar
        st.title("Navegação")
        page = st.radio("Selecione o módulo:",
                        ["Menu Principal", "Filtragem", "Transbordo", "Hidromassagem", "Cascatas", "Aquecimento", "Perda de carga", "Memória de cálculo", "Database equipamentos"])

        if st.session_state.get("username") == "kiara":
            st.markdown("---")
            if st.button("📊 Relatórios Admin"):
                from modules import report
                report.run()
                st.stop()

        # Espaço para empurrar o conteúdo para o final
        st.write("")  # Quebra de linha
        st.write("")  # Quebra de linha
        st.write("")  # Você pode repetir para ajustar o espaçamento ou usar CSS

        # Insere um CSS customizado para posicionar o container fixado na parte inferior
        st.markdown(
            """
            <style>
            .bottom-div {
                position: fixed;
                bottom: 0;
                width: 14.5rem;  /* Ajuste para caber na sidebar; pode ser necessário ajustar conforme o tamanho da sidebar */
                text-align: center;
                padding: 10px 0;
                background: #f0f2f6;
            }
            </style>
            """, unsafe_allow_html=True
        )

        # Container fixado na parte inferior da sidebar
        st.markdown('<div class="bottom-div">', unsafe_allow_html=True)
        st.write(f"Login: {st.session_state['username'].capitalize()}")
        if st.button("Logout"):
            del st.session_state["authenticated"]
            del st.session_state["username"]
            st.experimental_set_query_params(page="login")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Page Routing
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Menu Principal"

    if page != st.session_state.current_page:
        st.session_state.current_page = page
        st.rerun()

    # Page Content
    if st.session_state.current_page == "Menu Principal":
        show_home()
    elif st.session_state.current_page == "Filtragem":
        filtragem.run()
    elif st.session_state.current_page == "Transbordo":
        transbordo.run()
    elif st.session_state.current_page == "Hidromassagem":
        hidromassagem.run()
    elif st.session_state.current_page == "Perda de carga":
        perda_carga.main()
    elif st.session_state.current_page == "Cascatas":
        st.warning("Módulo em desenvolvimento! 🚧")
    elif st.session_state.current_page == "Aquecimento":
        st.warning("Módulo em desenvolvimento! 🚧")
    elif st.session_state.current_page == "Memória de cálculo":
        memoria.run()
    elif st.session_state.current_page == "Database equipamentos":
        database_equipamentos.run()


def show_home():
    st.title("💧 HidroCalc Piscinas")
    st.markdown("""
    ### Ferramentas para dimensionamento de sistemas hidráulicos para piscinas

    **Recursos Disponíveis:**
    - Sistema de filtragem com seleção automática de conjunto Filtro+MB
    - Cálculo de vazão necessária para sistemas de transbordo (borda infinita)
    - Dimensionamento de motobombas para sistema de Hidromassagem
    - Banco de dados técnicos sobre equipamentos (Sodramar database)
    - Determinação da perda de carga com base na fórmula de Darcy com interações pelo método Newton-Raphson para Colebrook-White
    - Memória de cálculo listando todas as equações, fórmulas, verificações e constantes são utilizados nas funções do módulo perda de carga

    **Módulos em desenvolvimento:**
    - Cascatas 
    - Aquecimento por trocador de calor elétrico (engenharia reversa da PLANILHA DE DIMENSIONAMENTO SODRAMAR)
    - Verificação de suscetibilidade à cavitação (desenvolvimento impossibilitado por falta de info NPSHr do fornecedor Sodramar)
    """)

    # st.image("assets/logo_fx2.png", use_container_width=True)


def run():
    main()


if __name__ == "__main__":
    run()
