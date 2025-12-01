import os
import base64
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Cargar variables de entorno al inicio
load_dotenv(os.path.join("config", ".env"))

# Importación de módulos propios
from src.polygons.polygon_module import show_polygon_section
from src.analysis.extract_raster import extract_forest_info
from src.analysis.extract_vector import extract_vector_info
from src.analysis.biodiversity import fetch_biodiversity_data
from src.analysis.satellite_fetch import analyze_biomass_agbd, analyze_canopy_height
from src.reports.generate_reports import generate_docx_report
from src.chatbot.main_chatbot import show_chatbot_interface

# ===================== CONFIGURACIÓN DE PÁGINA =====================
st.set_page_config(
    page_title="Datos Ecosistema",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== GESTIÓN DE ESTADO =====================
if 'analysis_context' not in st.session_state:
    st.session_state['analysis_context'] = {
        'geometry': None,        
        'raster_data': None,     
        'vector_data': {}, 
        'location_info': {},
        'biodiversity_data': None, # Datos GBIF
        'satellite_data': {},      # Datos GEE (Biomasa/Altura)
        'processed': False       
    }

if 'polygon' in st.session_state:
    st.session_state['analysis_context']['geometry'] = st.session_state['polygon']

# ===================== ESTILOS =====================
def load_css(file_path="static/css/style.css"):
    if os.path.exists(file_path):
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
            .main-header {
                font-size: 3.5rem; font-weight: 800; 
                background: linear-gradient(90deg, #2E86AB, #4CAF50);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                margin-bottom: 0;
            }
            .subtitle { font-size: 1.4rem; color: #888; font-style: italic; }
            .card {
                background: white; color: #333; padding: 1.5rem; border-radius: 15px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: 1px solid #e0e0e0;
                margin: 1rem 0; height: 100%; text-align: center;
            }
            .footer {
                text-align: center; padding: 2rem; color: #888; margin-top: 4rem; 
                border-top: 1px solid #444; 
            }
        </style>
        """, unsafe_allow_html=True)
load_css()

# ===================== UI HELPERS =====================
def img_to_base64(path):
    try:
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return None

def mostrar_header():
    col1, col2 = st.columns([1, 6])
    with col1:
        logo = img_to_base64("static/images/icon.png")
        if logo: st.markdown(f'<img src="data:image/png;base64,{logo}" width="100">', unsafe_allow_html=True)
        else: st.markdown("🌱")
    with col2:
        st.markdown('<h1 class="main-header">Sistema Multipropósito de IA</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Comisión Corográfica del Siglo XXI</p>', unsafe_allow_html=True)
    st.markdown("---")

# ===================== SIDEBAR =====================
with st.sidebar:
    st.markdown("### 🌍 Datos Ecosistema")
    st.info("1. 🗺️ Define área.\n2. 🚀 Ejecuta análisis.\n3. 📊 Consulta reporte.")
    st.markdown("---")
    st.markdown("**Equipo UTP - 2025**")

# ===================== APP PRINCIPAL =====================
mostrar_header()

# Definimos 4 pestañas incluyendo el Chatbot
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Generar Polígono", 
    "📊 Análisis Integral", 
    "💬 Asistente IA", 
    "👥 Créditos"
])

# --- TAB 1: POLÍGONO ---
with tab1:
    show_polygon_section()

# --- TAB 2: ANÁLISIS ---
with tab2:
    st.header("📊 Diagnóstico Territorial")
    geo = st.session_state['analysis_context']['geometry']
    
    if geo:
        if st.button("🚀 Ejecutar Diagnóstico Completo", type="primary", use_container_width=True):
            with st.status("Procesando territorio...", expanded=True) as status:
                
                # 1. RASTER (IDEAM)
                st.write("🌲 Consultando Bosques (IDEAM)...")
                try:
                    st.session_state['analysis_context']['raster_data'] = extract_forest_info(geo)
                except Exception as e: st.error(f"Error Raster: {e}")

                # 2. VECTORES (SIPRA)
                st.write("🚜 Cruzando Capas Legales (SIPRA)...")
                capas = [('frontera_agricola_jun2025', 'Frontera Agrícola'),
                         ('runap__registro_unico_nacional_ap', 'Áreas Protegidas'),
                         ('consejos_comunitarios', 'Consejos Comunitarios'),
                         ('ley_70_1993', 'Ley 70'),
                         ('zonas_de_reserva_campesina', 'Reservas Campesinas'),
                         ('centro_poblado', 'Centros Poblados')]
                res_vect, loc_info = {}, {}
                for lid, tit in capas:
                    try:
                        df, meta = extract_vector_info(geo, layer_name=lid)
                        if not df.empty: res_vect[tit] = df
                        if meta: loc_info.update(meta)
                    except: pass
                st.session_state['analysis_context']['vector_data'] = res_vect
                st.session_state['analysis_context']['location_info'] = loc_info

                # 3. BIODIVERSIDAD (GBIF)
                st.write("🐸 Consultando Biodiversidad (GBIF)...")
                try:
                    st.session_state['analysis_context']['biodiversity_data'] = fetch_biodiversity_data(geo)
                except Exception as e: st.error(f"Error GBIF: {e}")

                # 4. SATELITES (GEE)
                st.write("🛰️ Analizando Imágenes Satelitales (GEE)...")
                try:
                    tile_bio, stat_bio, _ = analyze_biomass_agbd(geo)
                    tile_can, stat_can, _ = analyze_canopy_height(geo)
                    st.session_state['analysis_context']['satellite_data'] = {
                        'biomass': {'tile': tile_bio, 'stats': stat_bio},
                        'canopy': {'tile': tile_can, 'stats': stat_can}
                    }
                except Exception as e: st.error(f"Error Satélite: {e}")

                st.session_state['analysis_context']['processed'] = True
                status.update(label="¡Diagnóstico Finalizado!", state="complete", expanded=False)

        # --- RESULTADOS ---
        if st.session_state['analysis_context']['processed']:
            st.divider()
            
            # HEADER UBICACIÓN
            loc = st.session_state['analysis_context']['location_info']
            if 'municipio' in loc:
                st.success(f"📍 **Ubicación:** {loc.get('municipio')}, {loc.get('departamento')}")
            
            # COLUMNAS SUPERIORES
            c1, c2 = st.columns(2)
            
            with c1:
                st.subheader("🌲 Cobertura (IDEAM)")
                rdf = st.session_state['analysis_context']['raster_data']
                if rdf is not None and not rdf.empty:
                    st.dataframe(rdf, use_container_width=True, hide_index=True)
                    bosque = rdf[rdf['Leyenda'].str.contains("Bosque", case=False)]['Área (ha)'].sum()
                    st.metric("Total Bosque", f"{bosque:.1f} ha")
                else: st.info("Sin datos de bosque.")

            with c2:
                st.subheader("⚖️ Legal/Productivo")
                vdata = st.session_state['analysis_context']['vector_data']
                if vdata:
                    tabs = st.tabs(list(vdata.keys()))
                    for i, (tit, df) in enumerate(vdata.items()):
                        with tabs[i]:
                            st.dataframe(df, use_container_width=True, hide_index=True)
                else: st.warning("Sin intersecciones legales.")

            st.divider()
            
            # SECCIÓN INFERIOR (SATELITES + BIO)
            st.subheader("🛰️ Inteligencia Territorial (IA + Satélites)")
            sat = st.session_state['analysis_context'].get('satellite_data', {})
            bio = st.session_state['analysis_context'].get('biodiversity_data')

            sc1, sc2, sc3 = st.columns(3)
            
            with sc1:
                st.markdown("#### 🌱 Biomasa & Carbono")
                if sat.get('biomass') and sat['biomass']['stats']:
                    s = sat['biomass']['stats']
                    st.metric("Biomasa Media", f"{s['Media (Mg/ha)']} Mg/ha")
                    st.metric("CO2 Potencial", f"{s['Captura Potencial CO2 (Mg)']} Mg", delta="Captura Estimada")
                    st.caption(f"Biomasa Total: {s['Biomasa Total (Mg)']} Mg")
                else: 
                    st.info("Sin datos GEDI.")

            with sc2:
                st.markdown("#### 🌳 Altura del Dosel")
                if sat.get('canopy') and sat['canopy']['stats']:
                    s = sat['canopy']['stats']
                    st.metric("Altura Promedio", f"{s['Promedio (m)']} m")
                else: st.info("Sin datos Altura.")

            with sc3:
                st.markdown("#### 🐸 Biodiversidad (GBIF)")
                if bio is not None and not bio.empty:
                    st.dataframe(bio, use_container_width=True, hide_index=True)
                    st.metric("Spp. Registradas", bio['Especies (GBIF)'].sum())
                else: st.info("Sin registros GBIF.")
            
            # --- SECCIÓN DE REPORTE ---
            st.divider()
            st.subheader("📥 Exportar Informe")
            
            col_d1, col_d2 = st.columns([2, 1])
            with col_d1:
                st.write("Descarga la **'Bitácora Territorial'** con todos los hallazgos técnicos, ambientales y sociales listos para imprimir o presentar.")
            
            with col_d2:
                try:
                    docx_file = generate_docx_report(st.session_state['analysis_context'])
                    st.download_button(
                        label="📄 Descargar Bitácora (.docx)",
                        data=docx_file,
                        file_name="Bitacora_Territorial_XXI.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        type="primary",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"No se pudo generar el reporte: {e}")

    else:
        st.warning("⚠️ Genera un polígono primero en la pestaña anterior.")

# --- TAB 3: CHATBOT ---
with tab3:
    show_chatbot_interface()

# --- TAB 4: CRÉDITOS ---
with tab4:
    st.subheader("👥 Equipo de Trabajo")
    cols = st.columns(4)
    equipo = [
        ("Paula Castro", "Ing. Sistemas", "paula.castro@utp.edu.co", "👩‍💻"),
        ("Carlos Betancur", "Adm. Ambiental", "cfbetancur@utp.edu.co", "🌿"),
        ("Mario Ortegón", "Ing. Físico", "maortegon@utp.edu.co", "⚛️"),
        ("Santiago Restrepo", "Adm. Ambiental", "santiago.restrepo@utp.edu.co", "📊")
    ]
    for c, (nom, rol, mail, em) in zip(cols, equipo):
        with c:
            st.markdown(f"""<div class="card"><h1>{em}</h1><h3>{nom}</h3><p>{rol}</p><small>{mail}</small></div>""", unsafe_allow_html=True)

# FOOTER
st.markdown('<div class="footer"><p>© 2025 Datos al Ecosistema • Sistema para la Comisión Corográfica XXI</p></div>', unsafe_allow_html=True)