from models.database import engine, Base
from models.models import *

def delete_all_tables():
    """ 🚨 Elimina todas las tablas de la base de datos pero no la elimina. """
    print("🔥 Eliminando todas las tablas...")
    Base.metadata.drop_all(engine)  # 🔥 Borra todas las tablas
    print("✅ Tablas eliminadas.")

if __name__ == "__main__":
    delete_all_tables()
