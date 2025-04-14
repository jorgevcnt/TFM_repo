import streamlit as st
import openai
import os
from langchain_core.messages import HumanMessage
from langchain_openai import AzureChatOpenAI
from sqlalchemy.orm import Session
from models.models import *
from models.database import *
from grafo.tools import *
from langgraph.prebuilt import create_react_agent
from grafo.builder import construir_flujo

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

llm = AzureChatOpenAI(
    api_key = KEY,
    api_version = VERSION,
    azure_endpoint = ENDPOINT,
    azure_deployment = MODELO
    )

cliente = openai.AzureOpenAI(
    api_key=KEY,
    api_version=VERSION,
    azure_endpoint=ENDPOINT
)

template = '''
Eres el chatbot de un asistente de compras. Tu tarea es ayudar a los usuarios a gestionar sus compras de manera eficiente y profesional.
Siempre debes de responder en tono formal, indistintamente de la conversación.
'''
# Funcion que identifica si es solicitud de compra
def solicitud_compra(mensaje_usuario):
    prompt=f"""
    Eres un asistente que debe de clasificar el siguiente mensaje del usuario
    representa una solicitus de compra.

    Mensaje: {mensaje_usuario}.

    Responde únicamente con True si es una solicitud de compra o False si no lo es.
    No añadas ninguna otra palabra ni explicación
    """
    print("Entra al comprobador")
    respuesta = llm.invoke([HumanMessage(content = prompt)]).content.strip().lower()
    if respuesta == "true":
        return True
    else:
        return False

def extraer_proveedor(mensaje_usuario):
    session = Session(bind=engine)
    prompt = f"""
    Eres un modelo que extrae unicmente el nombre del proveedor mencionado en un mensaje de solicitud de compra.
    Mensaje: {mensaje_usuario}.
    Responde únicamente con el nombre del proveedor.
    """
    respuesta = llm.invoke([HumanMessage(content = prompt)]).content.strip().lower()
    print(respuesta)
    if not respuesta or respuesta in ["", "desconocido", "ninguno"]:
        print("No se ha podido identificar el proveedor")
        session.close()
        return None


    proveedor = session.query(Proveedor).filter_by(nombre=respuesta).first()
    session.close()

    if proveedor:
        return True
    else:
        return False


# Inicializar el modelo por defecto
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = MODELO

# Inicializar el historial de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pedido_procesado" not in st.session_state:
    st.session_state["pedido_procesado"] = False

if "esperando_datos_proveedor" not in st.session_state:
    st.session_state["esperando_datos_proveedor"] = False

if "grafo_compilado" not in st.session_state:
    st.session_state["grafo_compilado"] = construir_flujo()


# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de usuario
if prompt := st.chat_input("¿Qué necesitas comprar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Si se estan esperando datos del proveedor entra aquí.
    if st.session_state["esperando_datos_proveedor"] == True:
        with st.chat_message("assistant"):
            with st.spinner("Procesando los datos del proveedor..."):
                #INSERTAR DATOS DEL PROVEEDOR Y EL INVOKE DEL GRAFO
                agente_proveedor = create_react_agent(llm ,tools=[insertar_proveedores])
                prompt = f''' 
                Eres el encargado de obtener la información de un proveedor.
                Se necesita conocer:
                - Nombre del proveedor 
                - Mail del proveedor
                - Contacto del proveedor

                Aqui tienes la información que tienes que obtener:

                {prompt}

                Devuelve unicamente un formato JSON como:
                    "nombre": "...",
                    "email": "...",
                    "contacto": "..."
                '
                Una vez generado el json, utiliza la herramienta insertar_proveedores para insertar el proveedor en la base de datos 
                y devuelve como resultado final UNICAMENTE el json que genera la tool.
                '''
                session = Session(bind=engine)
                response = agente_proveedor.invoke({'messages': [HumanMessage(content = prompt)]})
                contenido = response['messages'][-1].content
                print(f"El LLM devuelve: {contenido}")
                try: 
                    print("ya se ha hehco el insert del nuevo proveedor, ahora falta meterle el proveedor para meterlo por el invoke si es nuevo o no")
        
                    datos = json.loads(contenido)
                    print(datos)
                    nombre_proveedor = datos['nombre'].strip().lower()
                    print(f"nombre provedor es {nombre_proveedor}")
                
                    # 🔁 Volver a buscar el proveedor recién insertado
                    proveedor = session.query(Proveedor).filter_by(nombre=nombre_proveedor.lower()).first()
                    proveedor_id = proveedor.id_proveedor if proveedor else None
                    print(f"✅ Proveedor '{proveedor_id}' encontrado en la base de datos.")
                    session.close()
                    # Resetear estado

                    st.session_state["esperando_datos_proveedor"] = False
                    with st.spinner("🔄 Realizando el pedido, por favor espere..."):

                        # Obtener mensaje original
                    
                        mensaje_lang = st.session_state.get("mensaje_compra_detectado") + "Proveedor nuevo"
                    
                        grafo = st.session_state["grafo_compilado"]
                        resultado = grafo.invoke(mensaje_lang)
                    mensaje_resumen = f"""
                    ✅ Su pedido ha sido creado con éxito.

                    - 🧾 **ID del pedido**: `{resultado["id_pedido"]}`
                    - 📦 **Producto**: {resultado["descripcion"]}
                    - 💰 **Presupuesto**: {resultado["presupuesto"]} €
                    - 🧾 **Cantidad**: {resultado["cantidad"]}
                    - 📄 **Nombre proveedor**: `{resultado["nombre_proveedor"]}`
                    """

                    st.markdown(mensaje_resumen)


                except Exception as e:
                    print(e)
                    
                


    # Detectar si es solicitud de compra
    elif solicitud_compra(prompt) == True:
        with st.chat_message("assistant"):
            with st.spinner("Analizando solicitud"):
                proveedor_existe = extraer_proveedor(prompt)
                st.session_state["mensaje_compra_detectado"] = prompt
                if proveedor_existe:
                    with st.spinner("🔄 Realizando el pedido, por favor espere..."):

                        ## LLAMAR AL GRAFO, HACER EL INVOKE.
                        mensaje_lang = st.session_state.get("mensaje_compra_detectado") 
                        grafo = st.session_state["grafo_compilado"]
                        resultado = grafo.invoke(mensaje_lang)
                    mensaje_resumen = f"""
                    ✅ Su pedido ha sido creado con éxito.

                    - 🧾 **ID del pedido**: `{resultado["id_pedido"]}`
                    - 📦 **Producto**: {resultado["descripcion"]}
                    - 💰 **Presupuesto**: {resultado["presupuesto"]} €
                    - 🧾 **Cantidad**: {resultado["cantidad"]}
                    - 📄 **Nombre proveedor**: `{resultado["nombre_proveedor"]}`
                    """
                    st.markdown(mensaje_resumen)
                else:
                    ## PROCESAR EL NUEVO PROVEEDOR
                    st.session_state["esperando_datos_proveedor"] = True
                    mensaje_solicitud = """
                                        El proveedor mencionado no se encuentra registrado en la base de datos.
                                        Por favor, introduza la siguiente información en lenguaje natural:
                                        - Nombre del proveedor
                                        - Correo electronico
                                        - Contacto

                                        Ejemplo: El proveedor se llama Office Pro, el contacto es Laura Ramírez y su mail es laura@office.com
                                        """
                    st.session_state.messages.append({"role":"assistant", "content": mensaje_solicitud})
                    st.markdown(mensaje_solicitud)


    else:

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



