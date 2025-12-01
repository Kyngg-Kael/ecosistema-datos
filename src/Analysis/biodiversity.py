import pandas as pd
import geopandas as gpd
from shapely.ops import orient
from shapely.geometry import Polygon, MultiPolygon
from pygbif import occurrences
import concurrent.futures
import streamlit as st

# IDs taxonómicos fijos de GBIF para ahorrar tiempo de consulta
TAXON_GROUPS = {
    "Aves": 212,
    "Mamíferos": 359,
    "Reptiles": 358,
    "Anfibios": 131,
    "Plantas Vasculares": 7707728,
    "Mariposas": 797
}

def _fetch_group_count(group_name, taxon_key, wkt_geometry):
    """Consulta un grupo específico en hilo separado."""
    try:
        res = occurrences.search(
            geometry=wkt_geometry,
            taxonKey=taxon_key,
            hasCoordinate=True,
            limit=0,              # Solo metadatos, no descargas
            facet='speciesKey',   # Contar especies únicas
            facetLimit=1000
        )
        # Extraer conteo de la faceta
        riqueza = len(res.get('facets', [])[0]['counts']) if res.get('facets') else 0
        return group_name, riqueza
    except:
        return group_name, 0

def fetch_biodiversity_data(polygon):
    """Orquesta la consulta paralela a GBIF."""
    if not isinstance(polygon, (Polygon, MultiPolygon)):
        return pd.DataFrame()

    # 1. Preparar Geometría (WKT + Orientación)
    try:
        geom_simple = polygon.simplify(0.001, preserve_topology=True)
        geom_oriented = orient(geom_simple, sign=1.0) # Anti-horario obligatorio
        wkt = geom_oriented.wkt
    except Exception as e:
        print(f"Error geometría GBIF: {e}")
        return pd.DataFrame()

    # 2. Multithreading para velocidad
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        future_to_group = {
            executor.submit(_fetch_group_count, name, key, wkt): name 
            for name, key in TAXON_GROUPS.items()
        }
        for future in concurrent.futures.as_completed(future_to_group):
            name, count = future.result()
            results[name] = count

    # 3. DataFrame Final
    df = pd.DataFrame(list(results.items()), columns=['Grupo', 'Especies (GBIF)'])
    return df.sort_values(by='Especies (GBIF)', ascending=False).reset_index(drop=True)