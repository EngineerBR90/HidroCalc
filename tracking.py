# tracking.py
import time
from supabase import create_client
import streamlit as st

# FLAG GLOBAL PARA ATIVAR / DESATIVAR O TRACKING
ENABLE_TRACKING = False


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
                # TRACKING DESATIVADO
                if not ENABLE_TRACKING:
                    return result

                if 'username' in st.session_state:
                    duration = time.time() - start_time

                    supabase = get_supabase()
                    if supabase:
                        supabase.table('access_logs').insert({
                            "username": str(st.session_state.username),
                            "module": str(module_name),
                            "duration": float(round(duration, 2))
                        }).execute()

            except Exception as e:
                st.toast(f"⚠️ Falha no registro: {str(e)}", icon="⚠️")

            return result

        return wrapper

    return decorador