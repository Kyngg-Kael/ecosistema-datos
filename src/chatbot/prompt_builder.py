def build_system_prompt(context):
    """
    Convierte los datos técnicos del análisis en un prompt narrativo para el LLM.
    """
    if not context or not context.get('processed'):
        return """Eres un asistente experto en territorio y paz. 
        Actualmente el usuario NO ha generado ningún análisis. 
        Invítalo amablemente a dibujar un polígono y ejecutar el diagnóstico primero."""

    # 1. Ubicación
    loc = context.get('location_info', {})
    ubicacion = f"{loc.get('municipio', 'Desconocido')}, {loc.get('departamento', 'Colombia')}"

    # 2. Datos Ambientales (Raster)
    raster = context.get('raster_data')
    bosque_txt = "No se detectó bosque."
    if raster is not None and not raster.empty:
        # Intentamos buscar la fila de Bosque
        bosque = raster[raster['Leyenda'].str.contains("Bosque", case=False, na=False)]
        total_bosque = bosque['Área (ha)'].sum() if not bosque.empty else 0
        bosque_txt = f"El predio tiene {total_bosque:.1f} hectáreas de bosque natural."

    # 3. Datos Legales (Vector)
    vector = context.get('vector_data', {})
    restricciones = []
    if vector:
        for nombre_capa, df in vector.items():
            area = df['area_total_ha'].sum()
            restricciones.append(f"- {nombre_capa}: {area:.1f} ha intersectadas.")
    
    legal_txt = "\n".join(restricciones) if restricciones else "No se encontraron intersecciones legales (Frontera agrícola, Parques, etc)."

    # 4. Datos Satelitales (Biomasa)
    sat = context.get('satellite_data', {})
    bio_txt = "Sin datos de biomasa."
    if sat.get('biomass') and sat['biomass']['stats']:
        s = sat['biomass']['stats']
        bio_txt = (f"Biomasa media: {s.get('Media (Mg/ha)')} Mg/ha. "
                   f"Potencial de Carbono Total: {s.get('Carbono (Mg)')} Toneladas. "
                   f"Potencial de Captura CO2e: {s.get('Captura Potencial CO2 (Mg)')} Toneladas.")

    # 5. Biodiversidad
    biodiv = context.get('biodiversity_data')
    bio_spp = 0
    if biodiv is not None and not biodiv.empty:
        bio_spp = biodiv['Especies (GBIF)'].sum()
    
    # --- PROMPT FINAL ---
    system_prompt = f"""
    Actúa como un Asistente Experto de la 'Comisión Corográfica del Siglo XXI'.
    Tu misión es apoyar a comunidades campesinas, entidades y tomadores de decisiones.
    
    ESTÁS ANALIZANDO EL SIGUIENTE PREDIO EN TIEMPO REAL:
    - Ubicación: {ubicacion}
    - Componente Bosque: {bosque_txt}
    - Componente Legal/Restrictivo:
    {legal_txt}
    - Inteligencia Satelital (Clima): {bio_txt}
    - Biodiversidad Potencial: {bio_spp} especies registradas históricamente en la zona.

    INSTRUCCIONES:
    1. Responde SIEMPRE basándote en estos datos.
    2. Usa un tono empático, profesional y constructivo (enfocado en Paz y Desarrollo Sostenible).
    3. Si el usuario pregunta algo que no está en los datos, usa tu conocimiento general sobre geografía colombiana, pero aclara que es información general.
    4. Sé conciso. Respuestas de máximo 3 o 4 párrafos.
    5. Si hay mucho CO2 o Bosque, felicita al usuario por el potencial de bonos de carbono.
    """
    
    return system_prompt