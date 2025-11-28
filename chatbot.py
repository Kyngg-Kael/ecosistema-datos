import pandas as pd
import nltk
from groq import Groq
import glob
import os
import geopandas as gpd
import re 
import numpy as np
import streamlit as st

nltk.download('punkt')

client = Groq(api_key="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") #

st.set_page_config(
    page_title="Asistente de Chat",
    layout="centered",
)

def load_csv(file_path):
    return pd.read_csv(file_path)

def load_gpkg(file_path):
    gdf = gpd.read_file(file_path) #
    return pd.DataFrame(gdf) 

def load_all_dataframes():
    csv_files = glob.glob("*.csv") 
    gpkg_files = glob.glob("*.gpkg") #
    all_files = csv_files + gpkg_files #

    if not all_files:
        st.error("No se encontraron archivos en el directorio actual.")
        return pd.DataFrame()

    list_of_dfs = []
    for file_path in all_files:
        try:
            if file_path.endswith('.csv'):
                df = load_csv(file_path)
            elif file_path.endswith('.gpkg'):
                df = load_gpkg(file_path)
            
            list_of_dfs.append(df)
            print(f"Cargado automáticamente: {file_path}")
        except Exception as e:
            st.warning(f"Error al cargar {file_path}: {e}")

    if list_of_dfs:
        combined_df = pd.concat(list_of_dfs, ignore_index=True) #
        return combined_df
    else:
        return pd.DataFrame()


def get_ai_response(messages):
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.2,
        max_tokens=512,
        stream=True,
    )
    response = "".join(chunk.choices.delta.content or "" for chunk in completion)
    return response

def analyze_numeric_query(query, dataframe):
    if dataframe.empty:
        return None, None
    
    query_lower = query.lower()
    
    operation = None
    if any(op in query_lower for op in ["máximo", "max", "mayor", "alto"]):
          operation = 'max'
    elif any(op in query_lower for op in ["mínimo", "min", "menor", "bajo"]):
          operation = 'min'
    elif any(op in query_lower for op in ["promedio", "media", "mean", "prom"]):
          operation = 'mean'
      
    if not operation:
          return None, None 
    
    numeric_patterns = 'area|hectar|ha|área|superf|lat|lon|valor|shape|length|leng|met|geomet|alt'
    
    numeric_cols = [col for col in dataframe.columns if pd.api.types.is_numeric_dtype(dataframe[col])]

    column_candidates = [col for col in numeric_cols if any(kw in col.lower() for kw in numeric_patterns.split('|'))]
    
    if not column_candidates:
          explicit_kw = re.findall(r"[\'\"](.*?)[\'\"]", query_lower)
          column_candidates = [col for col in numeric_cols if any(kw.lower() in col.lower() for kw in explicit_kw)]

    if not column_candidates:
        column_candidates = numeric_cols
          
    if not column_candidates:
          return None, "No se encontraron columnas numéricas relevantes."

    results = {}
    for col in column_candidates:
        try:
            if operation == 'max':
                value = dataframe[col].max()
            elif operation == 'min':
                value = dataframe[col].min()
            elif operation == 'mean':
                value = dataframe[col].mean()
            
            if not np.isnan(value): 
                results[col] = f"{value:.2f}"
        except Exception:
            continue
        
    if results:
        return operation, f"Operación analítica '{operation}' solicitada. Resultados de cálculo directo en el DataFrame:\n{results}"
    
    return None, None

def search_in_data(query, dataframe):
    if dataframe is None or dataframe.empty:
        return []
    
    result = []
    query_lower = query.lower()
    
    for column in dataframe.columns:
        if dataframe[column].dtype == 'object':
            valid_rows = dataframe[column].astype(str).str.lower().str.contains(query_lower, na=False)
            result.extend(dataframe[valid_rows].head(3).values.tolist()) 
    
    return result[:10]

def chat():
    st.title("Sistema Inteligente de Análisis Territorial y Agroambiental")
    st.write("Bienvenido a tu asistente de información de Ecosistema")

    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    
    if 'combined_dataframe' not in st.session_state: 
        with st.spinner("Cargando todos los datos disponibles. Este proceso puede tardar..."):
            st.session_state['combined_dataframe'] = load_all_dataframes()
        
        column_info = list(st.session_state['combined_dataframe'].columns) if not st.session_state['combined_dataframe'].empty else "No hay datos cargados."
        
        promptSistema = f"""
        Eres un analista de datos, especializado en información geoespacial, 
        entiendes por completo el contexto ambiental y de Desarrollo Sostenible en Colombia
        y para tus respuestas siempre consideras que el usuario está interesado en la biodiversidad,
        los servicios ecosistémicos y las dinámicas socioculturales de zonas periféricas y de difícil acceso.
        Tu tarea es responder de manera directa y concisa, sin agregar información innecesaria o redundante.
        Prioriza responder con los datos cargados. Si no encuentras la respuesta en los datos, puedes usar tu conocimiento general,
        si no conoces la respuesta infórmale al usuario y discúlpate brevemente.
        Las columnas del DataFrame cargado son: {column_info}
        """
        st.session_state['messages'].append({"role": "system", "content": promptSistema})

    combined_dataframe = st.session_state.get('combined_dataframe')

    def submit():
        user_input = st.session_state.user_input
        if not user_input:
            return

        st.session_state['messages'].append({"role": "user", "content": user_input})
        st.session_state.user_input = "" 

        operation, analytic_result = analyze_numeric_query(user_input, combined_dataframe)
        
        current_messages = st.session_state['messages']
        
        if analytic_result and operation and "Error" not in analytic_result and "no encontrado" not in analytic_result:
            
            context_message = f"""
            Como analista de datos geoespaciales y experto en sostenibilidad en Colombia, responde la consulta: '{user_input}'.
            El sistema de análisis de datos realizó la operación '{operation}' y obtuvo el siguiente resultado exacto en el DataFrame cargado:
            {analytic_result}
            Usa ESTOS resultados para formular una respuesta ÚNICA, directa y concisa sin ser redundante y sin
            añadir información innecesaria para el usuario 
            (máximo 2 oraciones), manteniendo tu enfoque en el contexto ambiental/socio-cultural.
            """
            
            current_messages.append({"role": "user", "content": context_message})
            response_generator = get_ai_response(current_messages)
            current_messages.pop() 
        
        else:
            search_results = search_in_data(user_input, combined_dataframe)
            
            if search_results:
                preview_results_str = "\n".join([str(row) for row in search_results])
                
                context_message = f"""
                Como analista de datos geoespaciales y experto en sostenibilidad, responde la consulta: '{user_input}'.
                He encontrado estas filas de datos cargados que coinciden:\n{preview_results_str}\n
                Genera una respuesta muy concisa sin ser redundante y sin
                añadir información innecesaria para el usuario (máximo 3 oraciones), 
                priorizando esta información y contextualizándola desde la perspectiva de la biodiversidad o la dinámica sociocultural.
                """
                
                current_messages.append({"role": "user", "content": context_message})
                response_generator = get_ai_response(current_messages)
                current_messages.pop()

            else:
                context_message = f"""
                El usuario pregunta: '{user_input}'.
                No se encontraron datos relevantes en los archivos cargados. 
                Tu tarea ahora es responder a esta consulta utilizando tu conocimiento general experto en Ambiente y Desarrollo Sostenible en Colombia.
                Responde de manera directa y concisa sin ser redundante y sin
                añadir información innecesaria para el usuario (máximo 4 oraciones), 
                manteniendo el enfoque en la biodiversidad y dinámicas socioculturales.
                """
                
                current_messages.append({"role": "user", "content": context_message})
                response_generator = get_ai_response(current_messages)
                current_messages.pop()

        full_response = ""
        with st.chat_message("assistant"):
            st.markdown("🤖 **Bot**")
            full_response = st.write_stream(response_generator)
            
        st.session_state['messages'].append({"role": "assistant", "content": full_response})

    for message in st.session_state['messages']:
        if message["role"] == "user":
            st.chat_message("user").markdown(f"**Tú**: {message['content']}")
        elif message["role"] == "assistant":
            st.chat_message("assistant").markdown(f"**Bot**: {message['content']}")
            
    with st.form(key='chat_form', clear_on_submit=True):
        st.text_input("Ingresa tu consulta:", key="user_input")
        st.form_submit_button(label='Enviar', on_click=submit)

if __name__ == "__main__":
    chat()
