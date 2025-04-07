from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Obtener la ruta absoluta del directorio anterior
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Construir la ruta completa al archivo pedidos.db
DB_PATH = os.path.join(BASE_DIR, "pedidos.db")

# Conectar a SQLite (luego cambiaremos a Snowflake)
DB_URL = f"sqlite:///{DB_PATH}"

# Crear motor de base de datos
engine = create_engine(DB_URL, echo=False)

# Crear sesión para interactuar con la BD
SessionLocal = sessionmaker(bind=engine)

# Base de datos con SQLAlchemy
Base = declarative_base()

