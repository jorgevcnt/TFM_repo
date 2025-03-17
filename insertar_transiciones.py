from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
from init_database import Transicion, RolAprobador  # Importamos la clase de Transicion

# Conectar a SQLite (más adelante cambiaremos a Snowflake)
DB_URL = "sqlite:///pedidos.db"
engine = create_engine(DB_URL, echo=True)

# Crear sesión para interactuar con la BD
Session = sessionmaker(bind=engine)
session = Session()

# Lista de transiciones
TRANSICIONES_VALIDAS = [
    ("Preparación", "Aprobación"),
    ("Aprobación", "Oferta Enviada"),
    ("Oferta Enviada", "Negociación"),
    ("Negociación", "Adjudicación"),
    ("Adjudicación", "Compra Generada"),
    ("Compra Generada", "Expedición Aceptada"),
    ("Expedición Aceptada", "Finalizado"),
]
# Revisar bien cual de las dos me sirve para el proyecto
TRANSICIONES_VALIDAS = [
        ("Preparación de compra", "Registro de proveedor"),
        ("Registro de proveedor", "Firma informe"),
        ("Firma informe", "Lanzamiento de cesta"),
        ("Lanzamiento de cesta", "Aprobación Manager"),
        ("Aprobación Manager", "Aprobación Control"),
        ("Aprobación Control", "Solicitud de oferta"),
        ("Solicitud de oferta", "Recepción de oferta"),
        ("Recepción de oferta", "Negociación proveedor"),
        ("Negociación proveedor", "Adjudicación proveedor"),
        ("Adjudicación proveedor", "Aprobación Directora"),
        ("Aprobación Directora", "Generación de compra"),
        ("Generación de compra", "Expedición mercancía"),
        ("Expedición mercancía", "Finalizado"),
    ]

def insertar_transiciones(session):
    
    for origen, destino in TRANSICIONES_VALIDAS:
        existe = session.query(Transicion).filter_by(estado_origen=origen, estado_destino=destino).first()
        if not existe:
            session.add(Transicion(estado_origen=origen, estado_destino=destino))
    
    session.commit()

ROLES_APROBADORES = ["Manager CECO", "Control de Gestión", "Directora"]

def insertar_roles_aprobadores(session):
    for rol in ROLES_APROBADORES:
        if not session.query(RolAprobador).filter_by(nombre=rol).first():
            session.add(RolAprobador(nombre=rol))
    session.commit()