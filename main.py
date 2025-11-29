import os
import base64
from pathlib import Path

import streamlit as st

from main_chatbot.main_chatbot import chatbot
from mapas.seleccion_poligono import show_polygon_section

# ===================== CONFIGURACIÓN DE PÁGINA =====================
st.set_page_config(
    page_title="Datos Ecosistema",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.utp.edu.co',
        'About': "# Datos Ecosistema 🌍\nSistema de análisis territorial y agroambiental - UTP 2025"
    }
)

# ===================== ESTILOS PERSONALIZADOS =====================
def load_css(file_path="static/css/style.css"):
    if os.path.exists(file_path):
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # CSS embebido si no tienes el archivo
        st.markdown("""
        <style>
            .main-header {font-size: 3.5rem; font-weight: 800; background: linear-gradient(90deg, #2E86AB, #4CAF50); 
                          -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0;}
            .subtitle {font-size: 1.4rem; color: #555; font-style: italic;}
            .card {
                background: white;
                padding: 1.5rem;
                border-radius: 15px;
                box-shadow: 0 6px 20px rgba(0,0,0,0.08);
                border: 1px solid #e0e0e0;
                margin: 1rem 0;
                transition: all 0.3s;
            }
            .card:hover {transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0,0,0,0.12);}
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1.5rem;
                border-radius: 15px;
                text-align: center;
            }
            .stTabs [data-baseweb="tab-list"] {
                gap: 20px;
                justify-content: center;
                background: #f8f9fa;
                padding: 10px;
                border-radius: 15px;
            }
            .stTabs [data-baseweb="tab"] {
                font-size: 1.1rem;
                font-weight: 600;
                padding: 12px 24px;
                border-radius: 12px;
            }
            .footer {
                text-align: center;
                padding: 2rem;
                color: #666;
                font-size: 0.9rem;
                margin-top: 4rem;
                border-top: 1px solid #eee;
            }
        </style>
        """, unsafe_allow_html=True)

load_css()

# ===================== FUNCIÓN PARA IMAGEN BASE64 =====================
def img_to_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# ===================== HEADER HERMOSO =====================
def mostrar_header():
    col1, col2 = st.columns([1, 6])
    
    with col1:
        logo_path = "static/images/icon.png"
        if os.path.exists(logo_path):
            logo_base64 = img_to_base64(logo_path)
            st.markdown(
                f'<img src="data:image/png;base64,{logo_base64}" width="100" style="border-radius:12px;">',
                unsafe_allow_html=True
            )
        else:
            st.markdown("🌱")
    
    with col2:
        st.markdown('<h1 class="main-header">Sistema Multipropósito de IA para la Comisión Coreográfica del Siglo XXI</h1>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:32px; font-weight:600;" class="subtitle">Sistema geoespacial para la gestion agroforestal local</p>', unsafe_allow_html=True)
    
    st.markdown("---")

# ===================== SIDEBAR PERSONALIZADA =====================
with st.sidebar:
    st.image("static/images/icon.png" if os.path.exists("static/images/icon.png") else "", width=120)
    st.markdown("<h2 style='text-align:center; color:#2E86AB;'>🌍 Datos Ecosistema</h2>", unsafe_allow_html=True)
    st.markdown("### Menú Principal")
    
    st.info("""
    **Funcionalidades disponibles:**
    - Chatbot con IA
    - Mapas geográficos interactivos  
    - Análisis de cultivos
    - Reforma agraria
    - Estadísticas territoriales
    """)
    
    st.markdown("---")
    st.markdown("**Desarrollado por**  \nUniversidad Tecnológica de Pereira  \n2025")

# ===================== CONTENIDO PRINCIPAL =====================
mostrar_header()

# Pestañas modernas
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🤖 Chatbot IA", 
    "🏠 Inicio", 
    "🗺️ Mapa Geográfico", 
    "🌾 Cultivos", 
    "⚖️ Reforma Agraria", 
    "👥 Créditos"
])

# =================================== TAB 1: CHATBOT IA =================================== 
with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        chatbot()
    with col2:
        show_polygon_section()
with tab2:
    st.markdown("<h2 style='color:#4CAF50;'>🏠 Panel Principal</h2>", unsafe_allow_html=True)
    
    # Tarjetas métricas bonitas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card metric-card">
            <h3>12</h3>
            <p>Municipios</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <h3>600 mil</h3>
            <p>Habitantes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <h3>1.845 km²</h3>
            <p>Superficie</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Resumen del Ecosistema")
    st.markdown("""
    <div class="card">
        <p>Esta plataforma integra múltiples fuentes de datos para ofrecer una visión completa del territorio, 
        los cultivos, la reforma agraria y el acceso al crédito rural. 
        Próximamente con mapas interactivos avanzados y análisis predictivo con IA.</p>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.markdown("<h2 style='color:#2E86AB;'>🗺️ Mapa Geográfico Interactivo</h2>", unsafe_allow_html=True)
    st.info("Próximamente: mapas con capas de cobertura vegetal, cuerpos de agua, riesgo y más.")

with tab4:
    st.markdown("<h2 style='color:#4CAF50;'>🌾 Mapa de Cultivos</h2>", unsafe_allow_html=True)
    st.success("Visualización de cultivos permanentes, transitorios y áreas de producción.")

with tab5:
    st.markdown("<h2 style='color:#FF9800;'>⚖️ Reforma Agraria</h2>", unsafe_allow_html=True)
    st.warning("Análisis de predios, adjudicaciones y estado actual de la reforma.")

with tab6:
    st.markdown("<h2 style='color:#9C27B0;'>👥 Créditos y Equipo</h2>", unsafe_allow_html=True)
    
    cols = st.columns(4)
    equipo = [
        ("Paula Andrea Castro", "Ing. de Sistemas", "paula.castro@utp.edu.co", "👩‍💻"),
        ("Carlos Fernando Betancur", "Administrador Ambiental", "cfbetancur@utp.edu.co", "🌿"),
        ("Mario Alejandro Ortegón", "Ing. Físico", "maortegon@utp.edu.co", "⚛️"),
        ("Santiago Restrepo", "Administrador Ambiental", "santiago.restrepo@utp.edu.co", "📊")
    ]
    
    for col, (nombre, rol, correo, emoji) in zip(cols, equipo):
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="font-size:4rem;">{emoji}</div>
                <h4>{nombre.split()[0]}<br>{nombre.split()[-1]}</h4>
                <p><strong>{rol}</strong></p>
                <small>{correo}</small>
            </div>
            """, unsafe_allow_html=True)

# ===================== FOOTER =====================
st.markdown("""
<div class="footer">
    <p>© 2025 <strong>Universidad Tecnológica de Pereira</strong> • Proyecto Datos Ecosistema</p>
    <p>Hecho con ❤️ y Streamlit</p>
</div>
""", unsafe_allow_html=True)