import numpy as np
import rasterio
from rasterio.mask import mask
import shapely.geometry
import geopandas as gpd
import pandas as pd
import streamlit as st
from pathlib import Path

# Diccionario de leyendas del archivo contenido_cambio.txt
LEYENDAS = {
    1: "Bosque Estable",
    2: "Deforestación",
    3: "Regeneración",
    4: "No Bosque estable",
    5: "Sin información"
}

# Usar Pathlib hace que las rutas sean compatibles entre Windows/Mac/Linux
RASTER_PATH = Path("data/raw/bosques_IDEAM/superficie_bosques.img")

def extract_forest_info(polygon):
    """
    Extrae información de coberturas boscosas del raster IDEAM dentro del polígono.
    Args:
        polygon (shapely.Geometry): Polygon o MultiPolygon.
    Returns:
        pd.DataFrame: Tabla con estadísticas.
    """
    # 1. VALIDACIÓN ROBUSTA: Aceptamos Polygon y MultiPolygon
    if not isinstance(polygon, (shapely.geometry.Polygon, shapely.geometry.MultiPolygon)):
        st.error(f"Geometría no soportada: {type(polygon)}")
        return pd.DataFrame()
    
    # Verificar si el archivo existe antes de intentar abrirlo
    if not RASTER_PATH.exists():
        st.error(f"No se encontró el archivo raster en: {RASTER_PATH}")
        return pd.DataFrame()

    try:
        with rasterio.open(RASTER_PATH) as src:
            # 2. GESTIÓN DE CRS: GeoDataFrame maneja la reproyección automáticamente
            polygon_gdf = gpd.GeoDataFrame(geometry=[polygon], crs="EPSG:4326")
            
            # Reproyectamos al CRS del raster (seguramente Magna-Sirgas)
            if polygon_gdf.crs != src.crs:
                polygon_gdf = polygon_gdf.to_crs(src.crs)
            
            # 3. EXTRACCIÓN (MASKING)
            # mask espera un iterable de geometrías JSON-like
            out_image, _ = mask(src, polygon_gdf.geometry, crop=True, nodata=src.nodata)
            out_image = out_image[0] # Banda 1
            
            # Definir NoData
            nodata = src.nodata if src.nodata is not None else 0
            
            # Filtrar datos válidos
            valid_mask = out_image != nodata
            values = out_image[valid_mask]
            
            if len(values) == 0:
                st.warning("El polígono está fuera de la cobertura del raster o en zona 'NoData'.")
                return pd.DataFrame()
            
            # 4. ESTADÍSTICAS
            unique, counts = np.unique(values, return_counts=True)
            
            # Cálculo de Área
            res_x, res_y = src.res
            if src.crs.is_geographic:
                 st.warning("⚠️ El raster está en grados geográficos. El cálculo de hectáreas será impreciso.")
            
            pixel_area_m2 = abs(res_x * res_y)
            areas_m2 = counts * pixel_area_m2
            areas_ha = areas_m2 / 10000 
            
            total_pixels = len(values)
            percentages = (counts / total_pixels) * 100
            
            # DataFrame Final
            df = pd.DataFrame({
                'Código': unique,
                'Leyenda': [LEYENDAS.get(val, f"Clase {val}") for val in unique],
                'Conteo Píxeles': counts,
                'Área (ha)': np.round(areas_ha, 2),
                'Porcentaje (%)': np.round(percentages, 2)
            })
            
            # Ordenar por área descendente para mejor visualización
            return df.sort_values(by='Área (ha)', ascending=False).reset_index(drop=True)
    
    except Exception as e:
        st.error(f"Error procesando raster: {str(e)}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Test simple
    puntos = [(-75.7, 4.8), (-75.6, 4.8), (-75.6, 4.9), (-75.7, 4.9)]
    poly = shapely.geometry.Polygon(puntos)
    print(extract_forest_info(poly))