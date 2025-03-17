from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import create_engine
from datetime import datetime
from init_database import Pedido, HistorialPedido, Transicion, Base, PedidoCreate, Facturacion, RolAprobador, EstadoUpdate  # Importamos los modelos
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Configuración de la base de datos
DATABASE_URL = "sqlite:///pedidos.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Sesión de la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas en la BD (solo si no existen)
Base.metadata.create_all(bind=engine)

# FastAPI App
app = FastAPI()

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear una orden de compra
@app.post("/pedidos/")
def crear_pedido(pedido: PedidoCreate, db: Session = Depends(get_db)):
    print(pedido.model_dump())
    nuevo_pedido = Pedido(estado_actual=pedido.estado_actual)
    db.add(nuevo_pedido)
    db.commit()
    db.refresh(nuevo_pedido)
    return nuevo_pedido

@app.put("/pedidos/{pedido_id}/estado")
def actualizar_estado_pedido(pedido_id: int, nuevo_estado: EstadoUpdate, db: Session = Depends(get_db)):
    
    pedido = db.query(Pedido).filter(Pedido.id_pedido == pedido_id).first()
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    try:
        pedido.cambiar_estado(nuevo_estado, db)
        return {"message": "Estado actualizado con éxito"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


## Obtener una orden por ID
#@app.get("/ordenes/{id}")
#def obtener_orden(id: int, db=Depends(get_db)):
#    orden = db.query(OrdenCompra).filter(OrdenCompra.id == id).first()
#    if not orden:
#        raise HTTPException(status_code=404, detail="Orden no encontrada")
#    return orden
#
## Actualizar una orden
#@app.put("/ordenes/{id}")
#def actualizar_orden(id: int, proveedor: str, monto: float, db=Depends(get_db)):
#    orden = db.query(OrdenCompra).filter(OrdenCompra.id == id).first()
#    if not orden:
#        raise HTTPException(status_code=404, detail="Orden no encontrada")
#    orden.proveedor = proveedor
#    orden.monto = monto
#    db.commit()
#    db.refresh(orden)
#    return orden
#
## Eliminar una orden
#@app.delete("/ordenes/{id}")
#def eliminar_orden(id: int, db=Depends(get_db)):
#    orden = db.query(OrdenCompra).filter(OrdenCompra.id == id).first()
#    if not orden:
#        raise HTTPException(status_code=404, detail="Orden no encontrada")
#    db.delete(orden)
#    db.commit()
#    return {"message": "Orden eliminada"}
#
## Cambiar estado de una orden
#@app.patch("/ordenes/{id}/cambiar_estado")
#def cambiar_estado(id: int, nuevo_estado: str, db=Depends(get_db)):
#    orden = db.query(OrdenCompra).filter(OrdenCompra.id == id).first()
#    if not orden:
#        raise HTTPException(status_code=404, detail="Orden no encontrada")
#    
#    # Guardar el estado anterior en el historial
#    historial = HistorialEstado(orden_id=id, estado=nuevo_estado)
#    db.add(historial)
#    
#    orden.estado = nuevo_estado
#    db.commit()
#    db.refresh(orden)
#    return orden
#
## Ver historial de una orden
#@app.get("/ordenes/{id}/historial")
#def ver_historial(id: int, db=Depends(get_db)):
#    historial = db.query(HistorialEstado).filter(HistorialEstado.orden_id == id).all()
#    return historial
#