import ee
import streamlit as st
import pandas as pd
from shapely.geometry import Polygon, MultiPolygon
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(os.path.join("config", ".env"))

# ===================== INICIALIZACIÓN GEE =====================
def initialize_gee():
    try:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        print(f"🔌 GEE: Conectando con proyecto {project_id}...")
        
        if project_id:
            ee.Initialize(project=project_id)
        else:
            ee.Initialize()
        print("✅ GEE: Conexión exitosa.")
        return True
    except Exception as e:
        print(f"⚠️ GEE: Fallo inicialización directa. Intentando autenticación local...")
        try:
            ee.Authenticate()
            ee.Initialize()
            print("✅ GEE: Conexión exitosa tras autenticación.")
            return True
        except Exception as e2:
            print(f"❌ GEE Error: {e2}")
            return False

if 'gee_initialized' not in st.session_state:
    st.session_state['gee_initialized'] = initialize_gee()

# ===================== UTILIDADES =====================
def shapely_to_ee(geometry):
    """Convierte geometría local a objeto servidor GEE."""
    try:
        if isinstance(geometry, Polygon):
            return ee.Geometry.Polygon(list(geometry.exterior.coords))
        elif isinstance(geometry, MultiPolygon):
            coords = [list(p.exterior.coords) for p in geometry.geoms]
            return ee.Geometry.MultiPolygon(coords)
    except Exception as e:
        print(f"❌ Error convirtiendo geometría: {e}")
    return None

# ===================== BIOMASA Y CO2 (GEDI) =====================
def analyze_biomass_agbd(geometry):
    print("🛰️ Iniciando análisis de Biomasa (GEDI)...")
    if not st.session_state.get('gee_initialized'): return None, None, None
    
    ee_geom = shapely_to_ee(geometry)
    if not ee_geom: return None, None, None
    
    # 1. Cargar Colección GEDI L4A (Densidad de Biomasa Aérea)
    # Usamos la versión rasterizada mensual para rapidez
    try:
        gedi_col = ee.ImageCollection('LARSE/GEDI/GEDI04_A_002_MONTHLY') \
            .filterBounds(ee_geom) \
            .select('agbd')
        
        # Si no hay datos en la colección filtrada, retornamos error controlado
        gedi_img = gedi_col.mean().clip(ee_geom)
        
        # 2. Estadísticas (Aquí es donde solía fallar)
        stats = gedi_img.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=ee_geom,
            scale=100,      # Aumentamos escala a 100m para asegurar que capture datos promedio
            maxPixels=1e9,
            tileScale=4,
            bestEffort=True
        ).getInfo()
        
        print(f"📊 Stats GEDI crudos: {stats}")

        # Procesar valores
        mean_agbd = stats.get('agbd', 0)
        if mean_agbd is None: mean_agbd = 0
        
        # Calcular Área (en hectáreas)
        area_ha = ee_geom.area(1).getInfo() / 10000
        
        # CÁLCULOS DE BIOMASA Y CO2
        total_biomass = mean_agbd * area_ha
        total_carbon = total_biomass * 0.5  # Aprox. 50% de la biomasa es carbono
        total_co2 = total_carbon * 3.67     # Factor de conversión C -> CO2e

        stats_dict = {
            "Media (Mg/ha)": round(mean_agbd, 2),
            "Biomasa Total (Mg)": round(total_biomass, 2),
            "Carbono (Mg)": round(total_carbon, 2),
            "Captura Potencial CO2 (Mg)": round(total_co2, 2)
        }
        
        # 3. Visualización
        vis_params = {
            'min': 0, 
            'max': 150, 
            'palette': ['ffffe5', 'f7fcb9', 'addd8e', '41ab5d', '238443', '005a32']
        }
        map_id = ee.Image(gedi_img).getMapId(vis_params)
        tile_url = map_id['tile_fetcher'].url_format
        
        return tile_url, stats_dict, vis_params

    except Exception as e:
        print(f"❌ Error en cálculo Biomasa: {e}")
        return None, None, None

# ===================== ALTURA DOSEL (META) =====================
def analyze_canopy_height(geometry):
    print("🌳 GEE: Iniciando análisis de Altura del Dosel (Meta)...")
    if not st.session_state.get('gee_initialized'): return None, None, None
    
    ee_geom = shapely_to_ee(geometry)
    
    try:
        # 1. Cargar la Colección y Renombrar banda a 'height' para asegurar
        canopy = ee.ImageCollection("projects/meta-forest-monitoring-okw37/assets/CanopyHeight") \
            .mosaic() \
            .clip(ee_geom) \
            .rename('height')
        
        # 2. Estadísticas (Optimizadas)
        # scale=100: Sacrificamos detalle microscópico en el número promedio 
        # para ganar velocidad y asegurar que NO salga "Sin datos".
        stats_obj = canopy.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=ee_geom,
            scale=100,      # <--- AUMENTADO DE 10 a 100 para estabilidad
            maxPixels=1e9,
            bestEffort=True, # <--- Permite a GEE ajustar la escala si es necesario
            tileScale=4
        ).getInfo()
        
        print(f"📊 Stats Canopy crudos: {stats_obj}")
        
        mean_val = stats_obj.get('height', 0)
        
        # Si devuelve None (puede pasar en zonas sin árboles), ponemos 0
        if mean_val is None: mean_val = 0
        
        stats = {"Promedio (m)": round(mean_val, 2)}
        
        # 3. Visualización (Aquí sí mantenemos alta resolución visual)
        vis_params = {
            'min': 0, 
            'max': 25, 
            'palette': ['f7fcf5', '#caeac3', '#7bc77c', '#2a924a', '#00441b']
        }
        map_id = ee.Image(canopy).getMapId(vis_params)
        tile_url = map_id['tile_fetcher'].url_format
        
        return tile_url, stats, None

    except Exception as e:
        print(f"❌ Error en cálculo Altura: {e}")
        return None, None, None