from langgraph.graph import START, END, Graph 
from grafo.nodos import *

def construir_flujo():

    # Codigo para generar el flujo

    graph_builder = Graph()

    # Nodos al grafo

    graph_builder.add_node("obtener_datos_pedido", obtener_datos_pedido)
    graph_builder.add_node("decidir_siguiente_nodo", decidir_siguiente_nodo)
    graph_builder.add_node("gestionar_proveedor_nuevo", gestionar_proveedor_nuevo)
    graph_builder.add_node("grabar_cesta_srm", grabar_cesta_srm)
    graph_builder.add_node("aprobar_compra_manager", aprobar_compra_manager)
    graph_builder.add_node("aprobacion_proveedor", aprobacion_proveedor)
    graph_builder.add_node("lanzar_cesta_srm", lanzar_cesta_srm)
    graph_builder.add_node("resumen_cesta_para_envio", resumen_cesta_para_envio)
    graph_builder.add_node("envio_proveedores", envio_proveedores)
    graph_builder.add_node("registro_oferta", registro_oferta)
    graph_builder.add_node("negociacion_proposicion", negociacion_proposicion)
    graph_builder.add_node("aproabar_adjudicacion", aproabar_adjudicacion)
    graph_builder.add_node("facturar", facturar)
    graph_builder.add_node("fin", fin)
    # Empieza en obtener datos del pedido
    graph_builder.add_edge(START, "obtener_datos_pedido")

    # Se decido el siguente nodo
    graph_builder.add_edge("obtener_datos_pedido", "decidir_siguiente_nodo")

    # Configurar la decisión basada en la existencia del proveedor
    graph_builder.add_conditional_edges("decidir_siguiente_nodo", decidir_siguiente_nodo)

    # PROVEEDOR NUEVO
    graph_builder.add_edge("gestionar_proveedor_nuevo", "aprobacion_proveedor")
    graph_builder.add_edge("aprobacion_proveedor", "lanzar_cesta_srm")
    graph_builder.add_edge("lanzar_cesta_srm", "aprobar_compra_manager")

    # PROVEEDOR EXISTENTE
    graph_builder.add_edge("grabar_cesta_srm", "aprobar_compra_manager")

    # FLUJO GENERAL
    graph_builder.add_edge("aprobar_compra_manager","resumen_cesta_para_envio")
    graph_builder.add_edge("resumen_cesta_para_envio","envio_proveedores")
    graph_builder.add_edge("envio_proveedores","registro_oferta")
    graph_builder.add_edge("registro_oferta","negociacion_proposicion")
    graph_builder.add_edge("negociacion_proposicion","aproabar_adjudicacion")
    graph_builder.add_edge("aproabar_adjudicacion","facturar")
    graph_builder.add_edge("facturar","fin")
    graph_builder.add_edge("fin", END)

    return graph_builder.compile()