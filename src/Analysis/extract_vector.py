import geopandas as gpd
import pandas as pd
import streamlit as st
import shapely
from shapely.geometry import Polygon, MultiPolygon
from pathlib import Path

# ===================== GESTIÓN DE RUTAS =====================
current_file_path = Path(__file__).resolve()
PROJECT_ROOT = current_file_path.parent.parent.parent
GPKG_PATH = PROJECT_ROOT / "data" / "raw" / "datos.gpkg"

# ===================== CONFIGURACIÓN DE CAPAS =====================
LAYER_CONFIG = {
    'frontera_agricola_jun2025': 'elemento',       
    'runap__registro_unico_nacional_ap': 'nombre', 
    'consejos_comunitarios': 'NOMBRE',             
    'zonas_de_reserva_campesina': 'NOMBRE_ZON',    
    'centro_poblado': 'NOM_CPOB',                 
    'ley_70_1993': 'DESCRIPCIO'                    
}

GENERIC_COLS = ['categoria', 'clase', 'nombre', 'name', 'tipo', 'objectid', 'elemento']

def _load_vector_data(polygon, layer_name, format_type):
    """
    Retorna una tupla: (DataFrame_Resumen, Diccionario_Metadata)
    """
    metadata = {} 
    
    if not isinstance(polygon, (Polygon, MultiPolygon)):
        return pd.DataFrame(), metadata

    bounds = polygon.bounds
    gdf = gpd.GeoDataFrame()
    
    # 1. LECTURA (GPKG)
    try:
        if GPKG_PATH.exists():
            gdf = gpd.read_file(GPKG_PATH, layer=layer_name, bbox=bounds)
        else:
            print("GPKG no encontrado")
            return pd.DataFrame(), metadata
    except Exception as e:
        print(f"Error lectura GPKG {layer_name}: {e}")
        return pd.DataFrame(), metadata

    if gdf.empty:
        return pd.DataFrame(), metadata

    # 2. PROCESAMIENTO ESPACIAL
    # Aseguramos CRS WGS84 para el polígono
    polygon_gdf = gpd.GeoDataFrame(geometry=[polygon], crs="EPSG:4326")
    
    # Si los datos vienen en otro CRS (ej. Magna Sirgas), reproyectamos el polígono
    if gdf.crs and polygon_gdf.crs != gdf.crs:
        polygon_gdf = polygon_gdf.to_crs(gdf.crs)

    # Intersección
    try:
        intersected = gpd.overlay(gdf, polygon_gdf, how='intersection')
    except:
        intersected = gpd.sjoin(gdf, polygon_gdf, predicate='intersects')

    if intersected.empty:
        return pd.DataFrame(), metadata

    # 3. EXTRACCIÓN DE CONTEXTO (Específico para Frontera Agrícola)
    cols_lower = {c.lower(): c for c in intersected.columns}
    
    if 'municipio' in cols_lower and 'departamen' in cols_lower:
        try:
            col_muni = cols_lower['municipio']
            col_depto = cols_lower['departamen']
            
            # Calculamos cuál es el municipio con mayor área intersectada
            intersected['tmp_area_calc'] = intersected.geometry.area
            top_muni = intersected.groupby(col_muni)['tmp_area_calc'].sum().idxmax()
            
            # Obtenemos el departamento asociado a ese municipio
            subset = intersected[intersected[col_muni] == top_muni]
            top_depto = subset.iloc[0][col_depto]
            
            metadata['municipio'] = top_muni
            metadata['departamento'] = top_depto
        except Exception as e:
            print(f"No se pudo extraer contexto: {e}")

    # 4. CÁLCULO DE ÁREA (Hectáreas)
    try:
        if intersected.crs.is_geographic:
            intersected['area_ha'] = intersected.to_crs(epsg=3116).area / 10000
        else:
            intersected['area_ha'] = intersected.area / 10000
    except:
        intersected['area_ha'] = 0

    # 5. AGRUPACIÓN
    target_col = LAYER_CONFIG.get(layer_name)
    
    # Si no encuentra la columna configurada, busca en las genéricas
    if not target_col or target_col not in intersected.columns:
        # Intenta buscar insensible a mayúsculas
        found = False
        for col in intersected.columns:
            if col.lower() == target_col.lower():
                target_col = col
                found = True
                break
        
        if not found:
             target_col = next((c for c in intersected.columns if c.lower() in GENERIC_COLS), None)

    if target_col and target_col in intersected.columns:
        summary = intersected.groupby(target_col, as_index=False).agg(
            area_total_ha=('area_ha', 'sum'),
            count_features=('geometry', 'count')
        )
        summary.rename(columns={target_col: 'Categoría'}, inplace=True)
    else:
        summary = pd.DataFrame({
            'Categoría': ['Total Área (Sin clasificar)'],
            'area_total_ha': [intersected['area_ha'].sum()],
            'count_features': [len(intersected)]
        })

    summary['area_total_ha'] = summary['area_total_ha'].round(2)
    return summary.sort_values(by='area_total_ha', ascending=False).reset_index(drop=True), metadata


# ===================== WRAPPER STREAMLIT =====================
@st.cache_data(show_spinner=False, hash_funcs={Polygon: lambda x: x.wkt, MultiPolygon: lambda x: x.wkt})
def extract_vector_info(polygon, layer_name='frontera_agricola_jun2025', format_type='gpkg'):
    return _load_vector_data(polygon, layer_name, format_type)