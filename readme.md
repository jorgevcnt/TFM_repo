# Proyecto Trabajo Fin de Máster. 

Este repositorio contiene la implementación de una solución para la gestión y seguimiento de pedidos. El objetivo principal es centralizar, automatizar y agilizar los procesos de compra, reduciendo tiempos de ejecución y costes operativos.

---

## Estructura del repositorio

La estructura principal del proyecto se organiza en carpetas que agrupan la lógica de modelos, definición de grafos y la aplicación de interfaz. A continuación, se describe cada sección:
.
├── models/
│   ├── database.py
│   ├── delete_tables.py
│   ├── inicializacion.py
│   ├── models.py
│   └── seed_data.py
├── grafo/
│   ├── nodos.py
│   ├── tools.py
│   └── builder.py
└── app.py


### Carpeta `models/`

En esta carpeta se encuentra toda la lógica relacionada con la definición de tablas, conexiones a la base de datos y scripts auxiliares para la creación o carga inicial de datos.

- **database.py**  
  Contiene la configuración de la base de datos y la instancia principal que se usa para establecer la conexión utilizando el framework SQLAlchemy.  

- **delete_tables.py**  
  Script encargado de eliminar o vaciar las tablas de la base de datos. Se utiliza principalmente para entornos de desarrollo o pruebas en los que se necesita limpiar completamente la base de datos.  

- **inicializacion.py**  
  Rutina de inicialización que prepara el entorno, crea las tablas necesarias si no existen.  

- **models.py**  
  Define los modelos de datos (ORM) para cada entidad relevante (como Pedidos, Contratos, Proveedores, Facturas, etc.). Estas clases especifican la estructura de las tablas y las relaciones entre ellas.  

- **seed_data.py**  
  Se encarga de insertar datos iniciales en la base de datos para poder arrancar el proyecto con contenido.

### Carpeta `grafo/`

Esta carpeta alberga la lógica relacionada con la representación de grafos dentro del proyecto. Principalmente se enfoca en los estados, transiciones y herramientas para construir y manipular flujos o nodos.

- **nodos.py**  
  Contiene la definición de las estructuras para los nodos del grafo, así como la lógica para identificar qué información mantiene cada nodo.  

- **tools.py**  
  Conjunto de tools que pueden utilizar los agentes.  

- **builder.py**  
  Herramienta o script principal para armar y configurar el grafo a partir de los nodos y las reglas de transición definidas.

### Archivo `app.py`

Este archivo representa la **capa frontal** de la aplicación, desarrollada con Streamlit. Es la interfaz que los usuarios verán y con la que interactuarán. Además de la presentación, contiene algo de lógica de negocio para comprobar los datos antes de enviarlos al servidor o para gestionar ciertas validaciones en tiempo real.  

- Lógica de **comprobación** o validación ligera, para asegurar la consistencia de los datos antes de la inserción o actualización en la base de datos.

---

## Instalación y configuración

1. **Clona el repositorio**  

git clone https://github.com/

2. **Instala los requisitos**  

pip install -r requirements.txt

3. **Configura la base de datos**  

En el archivo database.py, actualiza la cadena de conexión para que apunte a tu servidor o instancia de base de datos.

4. **Inicializa las tablas**

python models/inicialización.py

Para cargar la maquina de estados

python models/seed_data.py

5. **Ejecuta la aplicación**

streamlit run app.py