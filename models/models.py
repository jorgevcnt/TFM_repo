from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from models.database import Base
import datetime

# Tabla de Pedidos (Estado actual)
class Pedido(Base):
    __tablename__ = "pedidos"

    id_pedido = Column(Integer, primary_key=True, autoincrement=True)
    posicion = Column(Integer, nullable=False)  # Posición dentro del pedido
    tipo = Column(String, nullable=False)  # Ordinario,Derivado, razón de cargo, no MCT
    pedido_tipoimp = Column(String, nullable=True)  # K, L, O, etc.
    descripcion = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relaciones
    estado_tramitacion_id = Column(Integer, ForeignKey("estados.id_estado"), nullable=False)  # 🔹 Se agrega ForeignKey correctamente
    estado_tramitacion = relationship("Estado", back_populates="pedidos")  # 🔹 Relación corregida

    creador_id = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    creador = relationship("Usuario")

    contrato_id = Column(Integer, ForeignKey("contratos.id_contrato"), nullable=True)
    contrato = relationship("Contrato")

    cesta_id = Column(Integer, ForeignKey("cestas.id_cesta"), nullable=True)
    cesta = relationship("Cesta")

    moneda_id = Column(Integer, ForeignKey("monedas.id_moneda"), nullable=True) 
    moneda = relationship("Moneda")

    historial = relationship("HistorialPedido", back_populates="pedido")
    ofertas = relationship("Oferta", back_populates="pedido")
    factura = relationship("Factura", back_populates="pedido")

    id_proveedor = Column(Integer, ForeignKey("proveedores.id_proveedor"), nullable=True)
    proveedor = relationship("Proveedor", back_populates="pedidos")

# Tabla de Historial de Estados

class HistorialPedido(Base):
    __tablename__ = "historial_pedidos"

    id_historial = Column(Integer, primary_key=True, autoincrement=True)
    id_pedido = Column(Integer, ForeignKey("pedidos.id_pedido"), nullable=False)
    estado_anterior = Column(Integer, nullable=False)
    estado_nuevo = Column(Integer, nullable=False)
    estado_aprobacion = Column(String, nullable=False, default="pendiente")
    fecha_cambio = Column(DateTime, default=datetime.datetime.utcnow)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)  # Quién aprobó/rechazó
    id_transicion = Column(Integer, ForeignKey("transiciones.id_transicion"), nullable=False)

    # Relación con Pedido
    pedido = relationship("Pedido", back_populates="historial")
    # Relación con Transiciones
    usuario_aprobador = relationship("Usuario", back_populates="historial")

    transicion = relationship("Transicion")

# Tabla de transiciones

class Transicion(Base):
    __tablename__ = "transiciones"

    id_transicion = Column(Integer, primary_key=True, autoincrement=True)
    estado_origen = Column(String, nullable=False)
    estado_destino = Column(String, nullable=False)
    estado_origen_id = Column(Integer, ForeignKey("estados.id_estado"), nullable=False)
    estado_destino_id = Column(Integer, ForeignKey("estados.id_estado"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    evento = Column(String)

    __table_args__ = (
        UniqueConstraint('estado_origen', 'estado_destino', name='_estado_origen_destino_uc'),
    )
    
    usuario = relationship("Usuario")  # Relación con Usuario

# Tabla proveedores

class Proveedor(Base):
    __tablename__ = "proveedores"

    id_proveedor = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    contacto = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    estado = Column(String, default="pendiente")  # "pendiente", "aprobado", "rechazado"
    fecha_registro = Column(DateTime, default=datetime.datetime.utcnow)

    pedidos = relationship("Pedido", back_populates="proveedor")

# Tabla de ofertas

class Oferta(Base):
    __tablename__ = "ofertas"

    id_oferta = Column(Integer, primary_key=True, autoincrement=True)
    id_pedido = Column(Integer, ForeignKey("pedidos.id_pedido"), nullable=False)
    id_proveedor = Column(Integer, ForeignKey("proveedores.id_proveedor"), nullable=False)
    precio_propuesto = Column(Float, nullable=False)
    estado_oferta = Column(String, default="pendiente")  # "pendiente", "aceptada", "rechazada"
    fecha_oferta = Column(DateTime, default=datetime.datetime.utcnow)

    pedido = relationship("Pedido", back_populates="ofertas")
    proveedor = relationship("Proveedor")

#Tabla de facturación

class Factura(Base):
    __tablename__ = "facturas"

    id_factura = Column(Integer, primary_key=True, autoincrement=True)
    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow)

    pedido_id = Column(Integer, ForeignKey("pedidos.id_pedido"), nullable=False)
    pedido = relationship("Pedido")

    proveedor_id = Column(Integer, ForeignKey("proveedores.id_proveedor"), nullable=False)
    proveedor = relationship("Proveedor")

    moneda_id = Column(Integer, ForeignKey("monedas.id_moneda"), nullable=True)
    moneda = relationship("Moneda")

    valor = Column(Float, nullable=False)

# Tabla Usuarios

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    rol = Column(String, nullable=False)  # Ej: "Control de Gestión", "Director", "Comprador"

    historial = relationship("HistorialPedido")
    pedidos = relationship("Pedido", back_populates="creador")
# Tabla de Estados (fusionando estados de aprobación)
class Estado(Base):
    __tablename__ = "estados"

    id_estado = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, unique=True, nullable=False)  # Ej: "Pendiente de Aprobación", "Aprobado", "Rechazado"
    tipo = Column(String, nullable=False)  # "flujo" o "aprobacion"
    requiere_aprobacion = Column(Boolean, default=False)  # Indica si este estado necesita aprobación manual
    
    pedidos = relationship("Pedido", back_populates="estado_tramitacion")
    

# Tabla de Contratos
class Contrato(Base):
    __tablename__ = "contratos"

    id_contrato = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow)
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)

    proveedor_id = Column(Integer, ForeignKey("proveedores.id_proveedor"), nullable=True)
    proveedor = relationship("Proveedor")
    
    cestas = relationship("Cesta", back_populates="contrato")

    moneda_id = Column(Integer, ForeignKey("monedas.id_moneda"), nullable=True)
    moneda = relationship("Moneda")

# Tabla de Cestas

class Cesta(Base):
    __tablename__ = "cestas"

    id_cesta = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    tipo_compra = Column(String, nullable=False)  # ordinaria, no mct, complementaria, razón de cargo, derivada)
    presupuesto = Column(Float, nullable=True)

    usuario_sap_id = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    usuario_sap = relationship("Usuario")

    contrato_id = Column(Integer, ForeignKey("contratos.id_contrato"), nullable=True)
    contrato = relationship("Contrato", foreign_keys=[contrato_id], back_populates="cestas")
     
    proveedor_id = Column(Integer, ForeignKey("proveedores.id_proveedor"), nullable=True)
    proveedor = relationship("Proveedor")

    moneda_id = Column(Integer, ForeignKey("monedas.id_moneda"), nullable=True)
    moneda = relationship("Moneda")

    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow)



# Tabla de Monedas

class Moneda(Base):
    __tablename__ = "monedas"

    id_moneda = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String, unique=True, nullable=False)  # Ej: "USD", "EUR"
    nombre = Column(String, nullable=False)  # Ej: "Dólar estadounidense"