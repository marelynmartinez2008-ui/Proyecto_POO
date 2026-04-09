import mariadb
import sys

# Configuración de conexión.
# ASEGÚRATE de que la contraseña en MariaDB sea realmente marelyn123
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "marelyn123", # La clave que acabamos de configurar
    "database": "CentroAdopcion"
}

def get_db_connection():
    try:
        # Aquí corregimos el nombre de la variable a DB_CONFIG
        conn = mariadb.connect(**DB_CONFIG)
        return conn
    except mariadb.Error as e:
        print(f"Error conectando a MariaDB: {e}")
        return None

def get_available_dogs():
    conn = get_db_connection()
    if conn is None:
        return []
    
   