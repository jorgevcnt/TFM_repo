# Volver a generar el diagrama UML y asegurarse de que el archivo se guarde correctamente
from graphviz import Digraph
# Crear el diagrama UML con Graphviz
dot = Digraph(comment='Diagrama UML de la Base de Datos')

# Definir las entidades principales con sus atributos
dot.node('Pedido', 'Pedido\n(id_pedido, posicion, tipo, pedido_tipoimp, descripcion, fecha_creacion, fecha_actualizacion, estado_tramitacion_id, creador_id, contrato_id, cesta_id, moneda_id, id_proveedor)')
dot.node('HistorialPedido', 'HistorialPedido\n(id, id_pedido, estado_anterior, estado_nuevo, estado_aprobacion, fecha_cambio, id_usuario, id_transicion)')
dot.node('Transicion', 'Transicion\n(id, estado_origen, estado_destino, estado_origen_id, estado_destino_id)')
dot.node('Estado', 'Estado\n(id, nombre, tipo, requiere_aprobacion)')
dot.node('Usuario', 'Usuario\n(id, nombre, email, rol)')
dot.node('Proveedor', 'Proveedor\n(id_proveedor, nombre, contacto, email, estado, fecha_registro)')
dot.node('Oferta', 'Oferta\n(id, id_pedido, id_proveedor, precio_propuesto, estado_oferta, fecha_oferta)')
dot.node('Facturacion', 'Facturacion\n(id, id_pedido, monto_total, estado_factura, fecha_emision, fecha_pago)')
dot.node('Contrato', 'Contrato\n(id_contrato, descripcion, fecha_creacion, fecha_inicio, fecha_fin, proveedor_id, cesta_general_id, moneda_id)')
dot.node('CestaGeneral', 'CestaGeneral\n(id_cesta_general, nombre, descripcion, fecha_creacion, moneda_id, proveedor_id)')
dot.node('Cesta', 'Cesta\n(id_cesta, nombre, tipo_compra, presupuesto, usuario_sap_id, contrato_id, proveedor_id, moneda_id, fecha_creacion)')
dot.node('Factura', 'Factura\n(id_factura, fecha_creacion, pedido_id, proveedor_id, moneda_id, valor)')
dot.node('Moneda', 'Moneda\n(id_moneda, codigo, nombre)')

# Relaciones entre entidades
dot.edge('Pedido', 'HistorialPedido', label='1 - *')
dot.edge('HistorialPedido', 'Transicion', label='N - 1')
dot.edge('HistorialPedido', 'Usuario', label='N - 1')  # Usuario aprobador
dot.edge('Pedido', 'Estado', label='N - 1')  # Estado actual del pedido
dot.edge('Pedido', 'Usuario', label='N - 1')  # Creador del pedido
dot.edge('Pedido', 'Proveedor', label='N - 1')
dot.edge('Pedido', 'Contrato', label='N - 1')
dot.edge('Pedido', 'Cesta', label='N - 1')
dot.edge('Pedido', 'Moneda', label='N - 1')
dot.edge('Pedido', 'Oferta', label='1 - *')
dot.edge('Pedido', 'Facturacion', label='1 - 1')
dot.edge('Contrato', 'Proveedor', label='N - 1')
dot.edge('Contrato', 'CestaGeneral', label='N - 1')
dot.edge('Contrato', 'Moneda', label='N - 1')
dot.edge('CestaGeneral', 'Proveedor', label='N - 1')
dot.edge('CestaGeneral', 'Moneda', label='N - 1')
dot.edge('Cesta', 'Usuario', label='N - 1')  # Usuario SAP
dot.edge('Cesta', 'Contrato', label='N - 1')
dot.edge('Cesta', 'Proveedor', label='N - 1')
dot.edge('Cesta', 'Moneda', label='N - 1')
dot.edge('Factura', 'Pedido', label='N - 1')
dot.edge('Factura', 'Proveedor', label='N - 1')
dot.edge('Factura', 'Moneda', label='N - 1')

# Guardar el diagrama
uml_path = "uml_diagram.png"
dot.render(uml_path, format='png', cleanup=False)

# Mostrar la ruta del diagrama generado
uml_path
