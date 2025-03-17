from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
import datetime
from init_database import Pedido, HistorialPedido, Transicion, Base, Proveedor, AprobacionPedido, Oferta, PedidoCreate, Facturacion, RolAprobador  # Importamos los modelos
from fastapi import HTTPException

# Conectar a SQLite (más adelante cambiaremos a Snowflake)
DB_URL = "sqlite:///pedidos.db"
engine = create_engine(DB_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
session = Session()

# 🔹 Definir la máquina de estados

def cambiar_estado_pedido(db: Session, pedido_id: int, nuevo_estado: str):
    pedido = db.query(Pedido).filter(Pedido.id_pedido == pedido_id).first()
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    # Verificar si la transición es válida
    transicion_valida = db.query(Transicion).filter(
        Transicion.estado_origen == pedido.estado_actual,
        Transicion.estado_destino == nuevo_estado
    ).first()

    if not transicion_valida:
        raise HTTPException(status_code=400, detail="Transición de estado no permitida")

    # Registrar en historial
    historial = HistorialPedido(
        pedido_id=pedido_id,
        estado_anterior=pedido.estado_actual,
        estado_nuevo=nuevo_estado
    )
    db.add(historial)

    # Actualizar estado del pedido
    pedido.estado_actual = nuevo_estado
    pedido.fecha_actualizacion = datetime.utcnow()
    
    db.commit()
    db.refresh(pedido)

    return pedido


TRANSICIONES_VALIDAS = [
    ("Preparación", "Aprobación"),
    ("Aprobación", "Oferta Enviada"),
    ("Oferta Enviada", "Negociación"),
    ("Negociación", "Adjudicación"),
    ("Adjudicación", "Compra Generada"),
    ("Compra Generada", "Expedición Aceptada"),
    ("Expedición Aceptada", "Finalizado"),
]

def insertar_transiciones(session):
    for origen, destino in TRANSICIONES_VALIDAS:
        if not session.query(Transicion).filter_by(estado_origen=origen, estado_destino=destino).first():
            session.add(Transicion(estado_origen=origen, estado_destino=destino))
    
    session.commit()
