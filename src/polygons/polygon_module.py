#Librerias estandar de Python
import os #operaciones del sistema de archivos
import io #herramientas para manejar entradas y salidas en memoria
import tempfile #directorios y archivos temporales que se borran despues de usados
import zipfile #manejo de archivos zip

#librerias instaladas
import openpyxl #lectura y escritura de archivos de excel
import pandas as pd #manipula datos en formato tabular
import geopandas as gpd #manejo de datos geoespaciales
import shapely.geometry #manipula geometrias espaciales
import streamlit as st #crea interfaces web
import folium #crea mapas interactivos
from streamlit_folium import st_folium #integra folium con streamlit
from folium.plugins import Draw #plugin para dibujar formas en el mapa

#función principal del modulo
def show_polygon_section():
    """
    Función principal del módulo: Muestra la sección para definir un polígono.
    
    Esta función configura la interfaz inicial en Streamlit y permite seleccionar
    el método para crear/cargar el polígono. Usa session_state para persistir datos
    entre interacciones, promoviendo escalabilidad.
    
    No recibe parámetros para mantenerla independiente y reutilizable.
    """

    #configuración base de streamlit
    st.title("Prototipo: Análisis de Polígonos con Datos Abiertos")
    st.write("Dibuja un polígono en el mapa o carga los archivos (.shp, .csv, .xlsx) guárdalo y analiza con shapefiles/rasters")

    #seleccionar método para definir el poligono
    method = st.selectbox("Método para definir el polígono",
                      ["Dibujar en el mapa",                    #opción 1
                       "Cargar desde Shapefile (ZIP)",          #opción 2
                       "Cargar desde CSV/Excel (coordenadas)"]) #opción 3

    #crear mapa base interactivo con Folium
    #nota: Folium usa coordenadas [lat, lon]; asumimos CRS WGS84 (estándar para GPS)
    if 'polygon' in st.session_state:
        #centrar en el polígono guardado para enfoque relevante
        bounds = st.session_state['polygon'].bounds #obtener límites: (min_lon, min_lat, max_lon, max_lat)
        m = folium.Map() #crear mapa vacío (sin ubicación inicial)
        m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]]) #ajustar zoom y centro: [[min_lat, min_lon], [max_lat, max_lon]]
    else:
        m = folium.Map(location=[4.814448, -75.694678], zoom_start=6) #centrar en Pereira, Colombia; zoom=6 para vista nacional. Ajustar de acuerdo al departamento priorizado

    #añadir plugin de Draw a Folium para dibujo y edición interactiva
    draw = Draw(export=True,  #habilitar descarga del dibujo como GeoJSON
                filename='polygon.geojson', #nombrar por default el archivo a descargar
                position='topleft', #ubicar controles del mapa
                draw_options={'polyline': False, 'circle': False, 'rectangle': False, 'marker': False, 'circlemarker': False}, #desactivar todas las opciones del poligono
                edit_options={'edit': True} #permite al usuario modificar los vertices despues de dibujar
    ) 
    draw.add_to(m)
    #el plugin está siempre activo para permitir dibujo/edición en cualquier método

    #mostrar polígono guardado (si existe) como capa en el mapa
    if 'polygon' in st.session_state:
        folium.GeoJson(
            st.session_state['polygon'].__geo_interface__, #convertir Shapely Polygon a GeoJSON
            style_function=lambda x: {'fillColor': 'blue', 'color': 'black', 'weight': 3}, #estilo visual
            name="Polígono guardado" #etiqueta para la capa
        ).add_to(m)
        #proporciona feedback visual inmediato, integrando polígonos de shapefile/CSV/Excel/dibujo

    #renderizar el mapa en Streamlit y capturar interacciones
    map_data = st_folium(m, width=700, height=500)
    #integrar Folium con Streamlit; devuelve 'map_data' (diccionario con dibujos/ediciones)

    #opción 1: Dibujar en el mapa (método interactivo manual)
    if method == "Dibujar en el mapa":
        st.info("Dibuja el polígono en el mapa y pulsa 'Guardar Polígono'.")

    #opción 2: cargar desde Shapefile (ZIP) - manejo de archivos geoespaciales
    #este bloque se activa solo si el usuario selecciona "Cargar desde Shapefile (ZIP)"
    #procesa ZIP con shapefiles (formato estándar para datos vectoriales abiertos)
    #extrae temporalmente, carga con GeoPandas y permite seleccionar/validar polígonos
    if method == "Cargar desde Shapefile (ZIP)":
        shp_zip = st.file_uploader("Sube el shapefile comprimido en ZIP", type="zip")
        #crear widget para subir ZIP; restringe a tipo 'zip' para validación básica
        #Shapefiles requieren múltiples archivos, ZIP es el empaquetado estándar.

        if shp_zip and st.button("Cargar Shapefile"):
            #procesar solo si hay archivo y se pulsa botón (control usuario)
            with tempfile.TemporaryDirectory() as tmpdir:
                #crear directorio temporal (auto-borrado al salir del bloque)
                with zipfile.ZipFile(shp_zip) as z:
                    z.extractall(tmpdir)
                    #extraer ZIP a temporal

                shp_files = [f for f in os.listdir(tmpdir) if f.endswith('.shp')]
                #buscar archivos .shp en temporal
                if shp_files:
                    gdf = gpd.read_file(os.path.join(tmpdir, shp_files[0]))
                    if gdf.crs and gdf.crs.to_string() != "EPSG:4326":
                        gdf = gdf.to_crs(epsg=4326) # <--- Agrega esto
                    #cargar el primer .shp como GeoDataFrame (manejando geometrías y atributos)

                    if len(gdf) > 1:
                        idx = st.selectbox("Selecciona el polígono", range(len(gdf)),
                                          format_func=lambda i: gdf.iloc[i].get('NAME', f'Feature {i}'))
                        #si hay múltiples registros, selectbox para elegir, Shapefiles pueden tener varios polígonos
                    else:
                        idx = 0
                        #si solo hay uno lo selecciona automaticamente

                    poly = gdf.geometry.iloc[idx]
                    #extraer geometría del índice seleccionado

                    if poly.geom_type not in ['Polygon', 'MultiPolygon']:
                        st.error("Selecciona una geometría tipo Polígono.")
                        #errores si no hay un poligono valido

                    else:
                        st.session_state['polygon'] = poly
                        st.success("Polígono cargado desde shapefile.")
                        st.rerun() #guardar en session_state, muestra éxito y recarga app (actualiza mapa).
                else:
                    st.error("No se encontró archivo .shp en el ZIP.") #manejo de error: guía al usuario si ZIP inválido.


    #opción 3: Cargar desde CSV/Excel (coordenadas) - manejo de datos tabulares
    #leer archivos con columnas de latitud/longitud, crea puntos y forma un polígono con Shapely
    #Soporta datos simples como GPS recolectados
    if method == "Cargar desde CSV/Excel (coordenadas)":
        coord_file = st.file_uploader("CSV o Excel (columnas: lat, latitud, lon, longitud)", 
                                      type=['csv', 'xlsx'])
        #crear widget para subir CSV/Excel; indica columnas esperadas en etiqueta
        if coord_file and st.button("Crear polígono desde coordenadas"): #procesar solo si hay archivo y botón pulsado (control usuario)
            
            #detectar con base en extensión del nombre
            if coord_file.name.lower().endswith('.csv'):
                df = pd.read_csv(coord_file)
            elif coord_file.name.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(coord_file)
            else:
                st.error("Formato no soportado. Usa .csv o .xlsx.")
                return
            
            #detectar columnas (insensible a mayúsculas)
            lat_col = next((c for c in df.columns if 'lat' in c.lower()), None)
            lon_col = next((c for c in df.columns if 'lon' in c.lower() or 'long' in c.lower()), None)
            if not lat_col or not lon_col:
                st.error("No se encontraron columnas de latitud/longitud.") #error si faltan las columnas requeridas
            else:
                points = list(zip(df[lon_col], df[lat_col]))  #orden: (lon, lat) para Shapely
                #crear lista de tuplas (lon, lat) de filas

                if len(points) < 3:
                    st.error("Se necesitan al menos 3 puntos.")
                    #mostrar error si son insuficientes puntos para el polígono.
                else:
                    polygon = shapely.geometry.Polygon(points) #crear Polygon con Shapely

                    if not polygon.is_valid:
                        st.warning("Polígono inválido (puntos no cierran o se cruzan). Intenta ordenar los puntos.")

                    st.session_state['polygon'] = polygon
                    st.success("Polígono creado desde coordenadas.")
                    st.rerun()
                    #guardar en session_state, muestra éxito y recarga app (actualiza mapa)
    
    #botón universal para guardar dibujo/editado desde el mapa, captura la geometría del último dibujo o edición en el mapa independientemente del método inicial
    if st.button("Guardar Polígono dibujado/editado"):
        if map_data and 'last_active_drawing' in map_data and map_data['last_active_drawing']:
            geojson = map_data['last_active_drawing']['geometry']
            #extraer geometría del dibujo activo como GeoJSON
            polygon = shapely.geometry.shape(geojson)
            #convertir GeoJSON a objeto Shapely Polygon
            st.session_state['polygon'] = polygon
            #guardar en session_state para persistencia entre recargas
            st.success("Polígono guardado.") #recargar app para actualizar mapa y UI.
            st.rerun()
        else:
            st.warning("Dibuja o edita un polígono primero.")

    #mostrar información del polígono guardado
    if 'polygon' in st.session_state:
        st.success("¡Polígono listo para análisis!")
        #mensaje de éxito para indicar disponibilidad para módulos posteriores

        col1, col2 = st.columns(2)
        #crear dos columnas iguales para display side-by-side
        with col1:
            st.write("**Tipo:**", st.session_state['polygon'].geom_type)
            #mostrar tipo de geometría (e.g., 'Polygon' o 'MultiPolygon')
        with col2:
            st.write("**Área (grados²):**", round(st.session_state['polygon'].area, 6))
            #calcular y redondea área (aproximada en coords lat/lon)
        
        if st.button("🗑️ Borrar polígono guardado"):
            del st.session_state['polygon']
            #eliminar clave de session_state para resetear
            st.success("Polígono borrado.")
            st.rerun() #recargar app para limpiar mapa y UI.

#ejecución:
if __name__ == "__main__":
    show_polygon_section()