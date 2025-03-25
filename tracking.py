# tracking.py
import time
from datetime import datetime
from supabase import create_client, Client
import streamlit as st

# Configuração do Supabase (será armazenada nos segredos do Streamlit)
def get_supabase():
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["key"]
    )

def track_access(module_name):
    """Decorador para registrar acesso aos módulos"""
    def decorador(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            
            if 'username' in st.session_state:
                duration = time.time() - start_time
                
                supabase = get_supabase()
                supabase.table('access_logs').insert({
                    "username": st.session_state.username,
                    "module": module_name,
                    "duration": round(duration, 2)
                }).execute()
            
            return result
        return wrapper
    return decorador