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
    def decorador(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)

            try:
                if 'username' in st.session_state:
                    duration = time.time() - start_time

                    supabase = get_supabase()
                    if supabase:
                        # Converter para float e garantir precisão
                        response = supabase.table('access_logs').insert({
                            "username": str(st.session_state.username),  # Garante string
                            "module": str(module_name),
                            "duration": float(round(duration, 2))
                        }).execute()

                        # Debug (opcional)
                        if hasattr(response, 'error') and response.error:
                            st.toast(f"Erro: {response.error.message}", icon="⚠️")

            except Exception as e:
                st.toast(f"⚠️ Falha no registro: {str(e)}", icon="⚠️")

            return result

        return wrapper

    return decorador