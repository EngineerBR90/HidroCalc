import streamlit as st
import bcrypt
# Senhas hasheadas
USERS = {
    "karine": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "reinaldo": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "kiara": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "acucena": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "sabrina": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "beatriz": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "daniel": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "marcos": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "projetos": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "juliana": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "guilherme": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
}

def verify_password(input_password, stored_hashed_password):
    """Verifica se a senha inserida corresponde ao hash armazenado."""
    return bcrypt.checkpw(input_password.encode(), stored_hashed_password.encode())

def login():
    st.title("Login HidroCalc Piscinas")
    st.write("Desenvolvido por Engº Reinaldo Farias")
    st.write("Segundo critérios de dimensionamento da norma ABNT NBR 10.339:2018")



    username = st.text_input("Usuário", key="login_username").lower()
    password = st.text_input("Senha", type="password", key="login_password")

    if st.button("Entrar", key="login_button"):
        if username in USERS and verify_password(password, USERS[username]):
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.success(f"Bem-vindo, {username.capitalize()}!")
            st.experimental_set_query_params(page="main")  # Atualiza a URL
            st.rerun()  # Atualiza a tela para carregar o main_app.py
        else:
            st.error("Usuário ou senha incorretos!")


# Se não estiver autenticado, exibe a tela de login
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login()
else:
    # Após autenticação, redireciona para `main_app.py`
    import main_app
    main_app.run()
