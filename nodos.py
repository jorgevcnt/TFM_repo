from langchain_openai import AzureChatOpenAI
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END, Graph 
from models.database import *
from models.models import *
import os
from sqlalchemy.orm import Session
import json

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

def obtener_datos_pedido(entrada_usuario):
    ''' Nodo que usa IA para obtener los datos del pedido del usuario, crea la cesta y el pedido con el estado inicial,
      y decide si el flujo valida el proveedor o graba la cesta.
    '''
    # Se crea la sesión de SQLAlchemy	
    session = Session(bind=engine)

    prompt = f''' 
    Eres el encargado de obtener la información de un pedido.
    Se necesita conocer:
    - Nombre del proveedor (si no se menciona, deja "desconocido")
    - Moneda en la que se realizó la compra
    - Presupuesto estimado
    - Producto a comprar

    {entrada_usuario}

    Devuelve los datos en un formato claro como:
    "Proveedor: Proveedor X, Moneda: EUR, Presupuesto: 5000, Producto: [Producto Y]"
    '''
    response = llm.invoke(prompt)
    datos_ia = response.content.strip()

    print(f'IA: {datos_ia}')

    # Extraer los datos del texto
    datos_extraidos = {}
    for item in datos_ia.split(','):
        key, value = item.strip().split(':')
        datos_extraidos[key.lower().strip()] = value.strip()
    
    nombre_proveedor = datos_extraidos.get('proveedor', 'desconocido')
    codigo_moneda = datos_extraidos.get('moneda', 'EUR') # Por defecto EUR
    presupuesto = float(datos_extraidos.get('presupuesto', 1000)) # Por defecto 1000

    print(f"📦 Datos extraídos: Proveedor: {nombre_proveedor}, Moneda: {codigo_moneda}, Presupuesto: {presupuesto}")
    
    # Verificar si el proveedor ya existe en la BD
    proveedor = session.query(Proveedor).filter_by(nombre=nombre_proveedor).first()
    proveedor_id = proveedor.id_proveedor if proveedor else None

    if proveedor:
        print(f"✅ Proveedor '{proveedor.nombre}' encontrado en la base de datos.")
        es_nuevo = False
        estado_inicial_nombre = "pendiente_no_condicionada"
    else:
        print(f"⚠️ Proveedor '{nombre_proveedor}' no encontrado. Requiere validación.")
        es_nuevo = True
        estado_inicial_nombre = "pendiente_condicionada"
    
    # Obtener estado inicial correspondiente
    estado_inicial = session.query(Estado).filter_by(nombre=estado_inicial_nombre).first()
    if not estado_inicial:
        print(f"⚠️ Estado '{estado_inicial_nombre}' no encontrado en la base de datos.")
        return {"error": "Estado inicial no encontrado"}



    # Verificar que la moneda existe en la BD
    moneda = session.query(Moneda).filter(Moneda.codigo == codigo_moneda).first()
    moneda_id = moneda.id_moneda if moneda else None

    if not moneda:
        print(f"⚠️ Moneda '{codigo_moneda}' no encontrada. Se usará EUR por defecto.")
        moneda = session.query(Moneda).filter_by(codigo="EUR").first()
        moneda_id = moneda.id_moneda

    # Crear la cesta y el pedido
    nueva_cesta = Cesta(
        nombre="Cesta generada automáticamente",
        descripcion="Pedido generado automáticamente",
        tipo_compra="ordinaria",
        presupuesto=presupuesto,
        usuario_sap_id=1,
        proveedor_id=proveedor_id,
        moneda_id=moneda_id,
        contrato_id=None
    )
    session.add(nueva_cesta)
    session.commit()

    print(f"✅ Cesta creada con ID: {nueva_cesta.id_cesta}")

    nuevo_pedido = Pedido(
        posicion=1,
        tipo="Ordinario",
        pedido_tipoimp="K",
        descripcion=f"Compra de {datos_extraidos.get('productos', 'productos no especificados')}",
        id_proveedor=proveedor_id,
        cesta_id=nueva_cesta.id_cesta,  # La Cesta ya está asignada
        estado_tramitacion_id=estado_inicial.id_estado,
        creador_id=1,
        moneda_id=moneda_id
    )
    session.add(nuevo_pedido)
    session.commit()

    # Se extraen las variables antes de cerrar la sesion 

    pedido_id = nuevo_pedido.id_pedido
    cesta_id = nueva_cesta.id_cesta
    session.close()

    return {

        "id_pedido": pedido_id,
        "id_proveedor": proveedor_id,  # ✅ Ya no intenta acceder a un objeto desvinculado
        "nombre_proveedor": nombre_proveedor,
        "id_cesta": cesta_id,
        "id_moneda": moneda_id,  # ✅ Ya no intenta acceder a un objeto desvinculado
        "estado_actual": estado_inicial_nombre,
        "id_usuario": 1,
        "nombre_cesta": "Cesta generada automáticamente",
        "tipo_compra": "ordinaria",
        "presupuesto": presupuesto,
        "descripcion_pedido": "Pedido generado automáticamente",
        "pedido_tipoimp": "K",
        "es_nuevo": es_nuevo  # 🔹 Indica si el proveedor debe validarse antes de continuar
    }


def grabar_cesta_srm(datos):
    """
     Simula el envío del pedido a SAP SRM, registra el estado en la BD y actualiza `HistorialPedido`
    antes de cambiar el estado a `aprobar_compra_manager`.
    """
    session = Session(bind=engine)

    id_pedido = datos["id_pedido"]

    #  Obtener el Pedido de la base de datos
    pedido = session.query(Pedido).filter_by(id_pedido=id_pedido).first()
    
    if not pedido:
        print(f"❌ Error: No se encontró el Pedido {id_pedido}.")
        return {"error": "Pedido no encontrado"}

    #  Guardar el estado inicial del Pedido antes de enviarlo a SAP
    estado_anterior_id = pedido.estado_tramitacion_id

    #  Crear JSON para enviar a SAP SRM
    data_sap = {
        "pedido_id": pedido.id_pedido,
        "descripcion": pedido.descripcion,
        "tipo": pedido.tipo,
        "proveedor_id": pedido.id_proveedor,
        "moneda_id": pedido.moneda_id,
        "cesta_id": pedido.cesta_id
    }

    json_sap = json.dumps(data_sap, indent=4)  # 🔹 Simulación de envío
    print(f"📤 Simulando envío de Pedido {id_pedido} a SAP SRM en formato JSON:\n{json_sap}")

    response_data = {
        "status": "success",
        "message": "Pedido registrado correctamente en SAP SRM"
    }

    print(f"✅ Pedido {id_pedido} registrado en SAP SRM (simulación).")
    

    # Se cambia el estado de la tabla pedido a aprobar compra manager
    nuevo_estado = session.query(Estado).filter_by(nombre="grabar_cesta_srm").first()
    if not nuevo_estado:
        print("❌ Error: No se encontró el estado 'grabar_cesta_srm'.")
        return {"error": "Estado no encontrado"}
    
    # Se obtiene la transicion correspondiente en la tabla transiciones
    transicion = session.query(Transicion).filter_by(
        estado_origen_id=estado_anterior_id,
        estado_destino_id=nuevo_estado.id_estado
    ).first()

    if not transicion:
        print(f"⚠️ Advertencia: No se encontró una transición desde {estado_anterior_id} a {nuevo_estado.id_estado}.")
        return {"error": "Transición no encontrada"}

    # Se registra el cambio en el historial del pedido
    historial = HistorialPedido(
        id_pedido=pedido.id_pedido,
        estado_anterior=estado_anterior_id,  # 🔹 Estado antes de SAP
        estado_nuevo=nuevo_estado.id_estado,  # 🔹 Estado después de SAP
        estado_aprobacion="pendiente",
        id_usuario=pedido.creador_id,
        id_transicion=transicion.id_transicion
    )
    session.add(historial)
    session.commit()

    print(f" Cambio registrado en HistorialPedido para Pedido {id_pedido}.")
    
    #  Ahora cambiar el estado del Pedido
    pedido.estado_tramitacion_id = nuevo_estado.id_estado
    session.commit()

    print(f"🔄 Pedido {id_pedido} actualizado al estado '{nuevo_estado.nombre}'.")

    session.close()

    return {
        "id_pedido": id_pedido,
        "estado_actual": nuevo_estado.nombre,
    }


def decidir_siguiente_nodo(datos):
    """
    Determina si el flujo sigue a `grabar_cesta_srm` o `gestionar_proveedor_nuevo`
    dependiendo de si el proveedor es nuevo o no.
    """
    if datos["es_nuevo"]:
        return "gestionar_proveedor_nuevo", datos
    return "grabar_cesta_srm", datos
