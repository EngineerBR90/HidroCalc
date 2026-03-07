import streamlit as st
import pandas as pd
import numpy as np          # corrigido
import bcrypt
from tracking import track_access
from modules import (
    filtragem,
    transbordo,
    hidromassagem,
    perda_carga,
    memoria,
    database_equipamentos,
    aquecimento,
    dimensionamento_completo
)

def main():
    # 1️⃣ Primeiro comando Streamlit: configuração da página
    st.set_page_config(
        page_title="💧 HidroCalc Piscinas",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 2️⃣ Verificação de autenticação (agora após a configuração)
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        st.warning("🔒 Você precisa fazer login para acessar o aplicativo.")
        if st.button("Ir para a tela de login"):
            import login
            login.login()
        st.stop()
        return

    # Sidebar Navigation
    with st.sidebar:
        st.title("Navegação")
        page = st.radio(
            "Selecione o módulo:",
            [
                "Menu Principal",
                "Dimensionamento Completo",
                "Filtragem",
                "Transbordo",
                "Hidromassagem",
                "Cascatas",
                "Aquecimento",
                "Perda de carga",
                "Memória de cálculo",
                "Database equipamentos"
            ]
        )

        if st.session_state.get("username") == "kiara":
            st.markdown("---")
            if st.button("🔒 Relatórios Kiara"):
                from modules import report
                report.run()
                st.stop()

        st.write("")
        st.write("")
        st.write("")

        st.markdown(
            """
            <style>
            .bottom-div {
                position: fixed;
                bottom: 0;
                width: 14.5rem;
                text-align: center;
                padding: 10px 0;
                background: #f0f2f6;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown('<div class="bottom-div">', unsafe_allow_html=True)
        st.write(f"Login: {st.session_state['username'].capitalize()}")

        if st.button("Logout"):
            st.session_state.clear()
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
    elif st.session_state.current_page == "Dimensionamento Completo":
        dimensionamento_completo.run()
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
        aquecimento.run()
    elif st.session_state.current_page == "Memória de cálculo":
        memoria.run()
    elif st.session_state.current_page == "Database equipamentos":
        database_equipamentos.run()

def show_home():
    st.title("💧 HidroCalc Piscinas")
    st.markdown("""
    ### Ferramentas para dimensionamento de sistemas hidráulicos para piscinas

    **Recursos Disponíveis:**
    - Dimensionamento Completo — importação de JSON do SketchUp para dimensionamento automático de todos os sistemas
    - Sistema de filtragem com seleção automática de conjunto Filtro+MB
    - Cálculo de vazão necessária para sistemas de transbordo (borda infinita)
    - Dimensionamento de motobombas para sistema de Hidromassagem
    - Banco de dados técnicos sobre equipamentos (Sodramar database)
    - Determinação da perda de carga com base na fórmula de Darcy com interações pelo método Newton-Raphson para Colebrook-White
    - Memória de cálculo listando todas as equações, fórmulas, verificações e constantes são utilizados nas funções do módulo perda de carga

    **Módulos em desenvolvimento:**
    - Cascatas 
    - Aquecimento por trocador de calor elétrico
    """)

def run():
    main()

if __name__ == "__main__":
    run()