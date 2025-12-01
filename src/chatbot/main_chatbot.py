import streamlit as st
from src.chatbot.utils import get_groq_client
from src.chatbot.prompt_builder import build_system_prompt

def parse_groq_stream(stream):
    """
    Función generadora que limpia la respuesta sucia de Groq 
    y entrega solo el texto limpio a Streamlit.
    """
    for chunk in stream:
        if chunk.choices:
            content = chunk.choices[0].delta.content
            if content:
                yield content

def show_chatbot_interface():
    st.markdown("### 💬 Asistente Territorial IA")
    st.caption("Pregúntame sobre el análisis realizado: ¿Cuánto carbono captura? ¿Hay restricciones legales?")

    # 1. Obtener Contexto y Cliente
    ctx = st.session_state.get('analysis_context', {})
    client = get_groq_client()

    if not client:
        return # Error ya mostrado en utils

    # 2. Inicializar Historial
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 3. Mostrar Historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 4. Input del Usuario
    if prompt := st.chat_input("Escribe tu pregunta aquí..."):
        # Guardar y mostrar pregunta
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 5. Generar Respuesta
        with st.chat_message("assistant"):
            try:
                system_context = build_system_prompt(ctx)
                
                messages_payload = [
                    {"role": "system", "content": system_context}
                ] + st.session_state.messages

                # Llamada a la API
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages_payload,
                    temperature=0.5,
                    max_tokens=1024,
                    stream=True,
                )
                
                response = st.write_stream(parse_groq_stream(stream))
                
                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                st.error(f"Error generando respuesta: {e}")