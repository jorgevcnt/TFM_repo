import sys
import os

# Permite importar módulos desde el directorio `app`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.database import engine, Base
from models.models import *


def initialize_database():
    """ Crea todas las tablas en la base de datos si no existen """
    print("🔧 Creando la base de datos...")
    Base.metadata.create_all(engine)
    print("✅ Base de datos creada correctamente.")

if __name__ == "__main__":
    initialize_database()
