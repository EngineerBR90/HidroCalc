import streamlit as st
import bcrypt
import csv
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+

# Configurar o fuso horário do Brasil
BRASIL_TZ = ZoneInfo("America/Sao_Paulo")

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
    "fernando": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "felipy": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    "adriano": "$2b$12$043BG9wRR2tcwhZhfkNHLOnrG19JiyCKBAbAwYWBNKwbEtjMTSBG2",
    }

def verify_password(input_password, stored_hashed_password):
    """Verifica se a senha inserida corresponde ao hash armazenado."""
    return bcrypt.checkpw(input_password.encode(), stored_hashed_password.encode())


def log_access(username):
    """Registra o acesso do usuário em um arquivo CSV com horário de Brasília"""
    brasil_time = datetime.now(BRASIL_TZ)
    with open('access_log.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([username, brasil_time.strftime("%Y-%m-%d %H:%M:%S")])


def login():
    st.title("💧 Login HidroCalc Piscinas")
    st.write("Desenvolvido por Engº Reinaldo Farias")
    st.write("Segundo critérios de dimensionamento da norma ABNT NBR 10.339:2018")

    username = st.text_input("Usuário", key="login_username").lower()
    password = st.text_input("Senha", type="password", key="login_password")

    if st.button("Entrar", key="login_button"):
        if username in USERS and verify_password(password, USERS[username]):
            st.session_state["authenticated"] = True
            st.session_state["username"] = username

            # Registra o acesso com horário brasileiro
            log_access(username)

            st.success(f"Bem-vindo, {username.capitalize()}!")
            st.experimental_set_query_params(page="main")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos!")


# Controle de autenticação
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login()
else:
    import main_app

    main_app.run()