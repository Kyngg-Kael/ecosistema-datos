import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(os.path.join("config", ".env"))

def get_groq_client():
    """Inicializa el cliente de Groq de forma segura."""
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        st.error("⚠️ No se encontró la API Key de Groq en .env")
        return None
    
    return Groq(api_key=api_key)