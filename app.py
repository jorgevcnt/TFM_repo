import streamlit as st
import openai
import os

page_bg_color = '''
<style>
[data-testid="stAppViewContainer"] {
    background-color: #f5f5f5;  /* Color blanco grisáceo */
}
[data-testid="stHeader"] {
    background: #1E1E1E !important;
    color: white !important;
}
[data-testid="stSidebar"] {
    background: #000000 !important;  /* Color oscuro del sidebar */
    color: white !important; /* Texto blanco */
}
[data-testid="stChatInputContainer"] {
    background: rgba(255, 255, 255, 0.8);
    border-radius: 10px;
    padding: 10px;
    width: 80%;
    margin: auto;
}
[data-testid="stChatMessage"] {
    background: rgba(0, 0, 0, 0.5);
    border-radius: 10px;
    padding: 10px;
}
</style>
'''

st.markdown(page_bg_color, unsafe_allow_html=True)


# Titulos
st.markdown('<h1 style="color: black;">Bienvenido</h1>', unsafe_allow_html=True)
st.markdown('<h2 style="color: black;">⬇️ Añade tu mensaje.</h2>', unsafe_allow_html=True)


# Configuración OpenAI
MODELO = os.getenv("MODELO")
KEY = os.getenv("KEY")
VERSION = os.getenv("VERSION")
ENDPOINT = os.getenv("ENDPOINT")

cliente = openai.AzureOpenAI(
    api_key=KEY,
    api_version=VERSION,
    azure_endpoint=ENDPOINT
)

template = '''
Eres el chatbot de un asistente de compras. Tu tarea es ayudar a los usuarios a gestionar sus compras de manera eficiente y profesional.
Siempre debes de responder en tono formal, indistintamente de la conversación.
'''

# Inicializar el modelo por defecto
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = MODELO

# Inicializar el historial de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de usuario
if prompt := st.chat_input("¿Qué necesitas comprar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Preparar contexto e historial
    mensajes = [{"role": "system", "content": template}]
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    with st.chat_message("assistant"):
        with st.spinner("🤖 Pensando..."):
            stream = cliente.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=mensajes + history,
            )
            response_message = stream.choices[0].message.content
            st.markdown(response_message)
            st.session_state.messages.append({"role": "assistant", "content": response_message})



