import streamlit as st
import bcrypt

# Senhas hasheadas
USERS = {
    "karine": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "reinaldo": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "kiara": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "acucena": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "sabrina": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "leonardo": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "daniel": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "marcos": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "projetos": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "juliana": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "guilherme": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "fernando": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "felipy": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "adriano": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
}


def verify_password(input_password, stored_hashed_password):
    """Verifica se a senha inserida corresponde ao hash armazenado."""
    try:
        return bcrypt.checkpw(input_password.encode(), stored_hashed_password.encode())
    except Exception:
        # Em caso de qualquer problema com o hash, não autentica
        return False


def login():
    st.title("💧 Login HidroCalc Piscinas")
    st.write("Desenvolvido por Engº Reinaldo Farias")
    st.write("Segundo critérios de dimensionamento da norma ABNT NBR 10.339:2018")

    # Inputs
    username = st.text_input("Usuário", key="login_username").lower()
    password = st.text_input("Senha", type="password", key="login_password")

    if st.button("Entrar", key="login_button"):
        if username and username in USERS and verify_password(password, USERS[username]):
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.success(f"Bem-vindo, {username.capitalize()}!")
            # Não usamos query params; apenas reiniciamos para que o main.py detecte a autenticação
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos!")


# Se não estiver autenticado, exibe a tela de login
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login()
else:
    # Após autenticação, redireciona para `main_app.py`
    import main_app

    main_app.run()
