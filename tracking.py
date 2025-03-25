# tracking.py
import time
from supabase import create_client
import streamlit as st


def get_supabase():
    """Retorna o cliente Supabase com verificações de segurança"""
    try:
        # Verifica se os segredos existem
        if "supabase" not in st.secrets:
            st.error("Configuração do Supabase não encontrada nos segredos")
            return None

        return create_client(
            st.secrets.supabase.url,
            st.secrets.supabase.key
        )
    except Exception as e:
        st.error(f"Erro na conexão com Supabase: {str(e)}")
        return None


def track_access(module_name):
    """Decorador para registrar acesso aos módulos com tratamento de erros"""

    def decorador(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)

            try:
                if 'username' in st.session_state:
                    duration = round(time.time() - start_time, 2)

                    # Conexão segura
                    supabase = get_supabase()
                    if supabase:
                        supabase.table('access_logs').insert({
                            "username": st.session_state.username,
                            "module": module_name,
                            "duration": duration
                        }).execute()

            except Exception as e:
                st.toast(f"⚠️ Erro no registro de uso: {str(e)}", icon="⚠️")

            return result

        return wrapper

    return decorador