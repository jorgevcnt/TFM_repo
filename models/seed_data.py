from sqlalchemy.orm import Session
from models.database import engine
from models.models import Estado, Transicion, Usuario, Moneda

# Crear sesión de la base de datos
session = Session(bind=engine)

# 📌 1. Insertar Usuarios
usuarios = [
    {"nombre": "IoTBD-Control de gestión", "email": "control_gestion@empresa.com", "rol": "Control de Gestión"},
    {"nombre": "IoTBD-Funciones", "email": "funciones@empresa.com", "rol": "Funciones"},
    {"nombre": "IoTBD-Director del área técnica", "email": "director_tecnico@empresa.com", "rol": "Director Técnico"},
    {"nombre": "IoTBD-Responsable CECO", "email": "responsable_ceco@empresa.com", "rol": "Responsable CECO"},
    {"nombre": "IoTBD-Compras", "email": "compras@empresa.com", "rol": "Compras"},
    {"nombre": "Proveedor", "email": "proveedor@empresa.com", "rol": "Proveedor"},
    {"nombre": "IoTBD-Responsable Técnico solicitud", "email": "responsable_tecnico@empresa.com", "rol": "Responsable Técnico"},
    {"nombre": "IoTBD-Directora", "email": "directora@empresa.com", "rol": "Directora"},
    {"nombre": "IoTBD-Finanzas", "email": "finanzas@empresa.com", "rol": "Finanzas"},
]

# Insertar usuarios si no existen
usuarios_db = {u.nombre: u for u in session.query(Usuario).all()}
for usuario in usuarios:
    if usuario["nombre"] not in usuarios_db:
        session.add(Usuario(**usuario))

session.commit()

# 📌 2. Insertar Estados
estados = [
    ("pendiente_condicionada", "flujo"),
    ("pendiente_no_condicionada", "flujo"),
    ("grabar_cesta_srm", "flujo"),
    ("solicitar_firma_inf_prov_cond", "flujo"),
    ("firma_inf_prov_cond", "flujo"),
    ("lanzar_cesta_srm", "flujo"),
    ("aprobar_compra_manager", "flujo"),
    ("revision_compra", "flujo"),
    ("solicitar_oferta_provedoores", "flujo"),
    ("consulta_acep_oferta", "flujo"),
    ("negociacion_proposicion_proveedores", "flujo"), 
    ("aprobar_adjudicacion", "flujo"),
    ("facturar", "flujo"),
    ("finalizado", "flujo"),
]


# Insertar estados si no existen
# Obtener los estados existentes en la base de datos
estados_db = {e.nombre: e for e in session.query(Estado).all()}

for estado in estados:
    nombre, tipo = estado  # 🔹 Asegurar que se desempaqueta correctamente

    if nombre not in estados_db:
        session.add(Estado(
            nombre=nombre,  # 🔹 Aquí solo el nombre
            tipo=tipo,  # 🔹 Aquí solo el tipo
            requiere_aprobacion=True if "aprobar" in nombre else False
        ))

session.commit()


# 📌 3. Insertar Transiciones con Usuarios
transiciones = [
    ("pendiente_condicionada", "solicitar_firma_inf_prov_cond", "Se genera la creación de la compra", "IoTBD-Control de gestión"),
    ("pendiente_no_condicionada", "grabar_cesta_srm", "Se genera la creación de la compra", "IoTBD-Control de gestión"),
    ("solicitar_firma_inf_prov_cond", "firma_inf_prov_cond", "Pedido registrado en SRM", "IoTBD-Director del área técnica"),
    ("firma_inf_prov_cond", "lanzar_cesta_srm", "Firma de informe", "IoTBD-Control de gestión"),
    ("lanzar_cesta_srm", "aprobar_compra_manager", "Nueva cesta en SRM", "IoTBD-Control de gestión"),
    ("grabar_cesta_srm", "aprobar_compra_manager", "Nueva cesta en SRM", "IoTBD-Control de gestión"),
    ("aprobar_compra_manager", "revision_compra", "Aprobación anterior", "IoTBD-Responsable CECO"),
    ("revision_compra", "solicitar_oferta_provedoores", "Compra revisada", "IoTBD-Compras"),
    ("solicitar_oferta_provedoores", "consulta_acep_oferta", "Pedido en regla", "IoTBD-Compras"),
    ("consulta_acep_oferta", "negociacion_proposicion_proveedores", "El proveedor envía la oferta", "IoTBD-Responsable Técnico solicitud"),
    ("negociacion_proposicion_proveedores", "aprobar_adjudicacion", "Una vez la oferta se consulta", "IoTBD-Compras"),
    ("aprobar_adjudicacion", "facturar", "Una vez elegido el proveedor se cierra", "IoTBD-Directora"),
    ("facturar", "finalizado", "Se contabiliza la factura", "IoTBD-Finanzas"),
]

# Insertar transiciones si no existen
for estado_origen, estado_destino, evento, usuario in transiciones:
    estado_origen_obj = session.query(Estado).filter_by(nombre=estado_origen).first()
    estado_destino_obj = session.query(Estado).filter_by(nombre=estado_destino).first()
    usuario_obj = session.query(Usuario).filter_by(nombre=usuario).first()

    transicion_existente = session.query(Transicion).filter_by(
        estado_origen=estado_origen_obj.nombre,  # ✅ Agregar nombre del estado de origen
        estado_destino=estado_destino_obj.nombre,  # ✅ Agregar nombre del estado de destino
        estado_origen_id=estado_origen_obj.id_estado,
        estado_destino_id=estado_destino_obj.id_estado,
        id_usuario=usuario_obj.id_usuario
    ).first()

    if not transicion_existente:
        session.add(Transicion(
            estado_origen=estado_origen_obj.nombre,  # ✅ Agregar nombre del estado de origen
            estado_destino=estado_destino_obj.nombre,  # ✅ Agregar nombre del estado de destino
            estado_origen_id=estado_origen_obj.id_estado,
            estado_destino_id=estado_destino_obj.id_estado,
            id_usuario=usuario_obj.id_usuario,
            evento=evento
        ))

session.commit()



monedas = [
    {"codigo": "EUR", "nombre": "Euro"},
    {"codigo": "GBP", "nombre": "Libra esterlina"},
    {"codigo": "USD", "nombre": "Dólar estadounidense"},
    {"codigo": "CHF", "nombre": "Franco suizo"},
    {"codigo": "NOK", "nombre": "Corona noruega"},
    {"codigo": "SEK", "nombre": "Corona sueca"},
    {"codigo": "DKK", "nombre": "Corona danesa"},
    {"codigo": "PLN", "nombre": "Zloty polaco"},
    {"codigo": "HUF", "nombre": "Forinto húngaro"},
    {"codigo": "CZK", "nombre": "Corona checa"},
    {"codigo": "BGN", "nombre": "Lev búlgaro"},
    {"codigo": "RON", "nombre": "Leu rumano"},
]

# Insertar monedas si no existen
monedas_db = {m.codigo: m for m in session.query(Moneda).all()}
for moneda in monedas:
    if moneda["codigo"] not in monedas_db:
        session.add(Moneda(**moneda))

session.commit()




session.close()

print("📌 ¡Base de datos inicializada con usuarios, estados, transiciones y monedas!")
