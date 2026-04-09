import mariadb
import sys

# Configuración de conexión.
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "marelyn123",
    "database": "CentroAdopcion"
}

def get_db_connection():
    try:
        conn = mariadb.connect(**DB_CONFIG)
        return conn
    except mariadb.Error as e:
        print(f"Error conectando a MariaDB: {e}")
        return None

def get_available_dogs():
    conn = get_db_connection()
    if not conn: return []
    cur = conn.cursor(dictionary=True)
    try:
        # Al usar *, ya traemos la nueva columna image_url automáticamente
        cur.execute("SELECT * FROM Pet WHERE is_adopted = 0")
        return cur.fetchall()
    except Exception as e:
        print(f"ERROR: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def get_dog_by_id(dog_id):
    conn = get_db_connection()
    if not conn: return None
    cur = conn.cursor(dictionary=True)
    try:
        # AGREGADO: image_url para que se vea la foto al confirmar
        cur.execute("SELECT id, name, age, breed, image_url FROM Pet WHERE id = %s", (dog_id,))
        return cur.fetchone()
    except mariadb.Error as e:
        print(f"Error: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def register_adoption_transactional(dog_id, adopter_name, adopter_lastname, address, id_card):
    conn = get_db_connection()
    if not conn: return False
    cur = conn.cursor()
    try:
        conn.autocommit = False
        cur.execute("INSERT INTO Person (name, lastName, id_card) VALUES (%s, %s, %s)", 
                   (adopter_name, adopter_lastname, id_card))
        person_id = cur.lastrowid
        cur.execute("INSERT INTO Adopter (person_id, address) VALUES (%s, %s)", 
                   (person_id, address))
        cur.execute("INSERT INTO Adoption (adopter_id, dog_id) VALUES (%s, %s)", 
                   (person_id, dog_id))
        cur.execute("UPDATE Pet SET is_adopted = 1 WHERE id = %s", (dog_id,))
        conn.commit()
        return True
    except Exception as e:
        if conn: conn.rollback()
        print(f"Error: {e}")
        return False
    finally:
        if conn: 
            if 'conn' in locals() and conn: conn.close()

def get_adoption_history():
    conn = get_db_connection()
    if not conn: return []
    cur = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT P.name AS adopter_name, P.lastName AS adopter_lastname, 
               Dog.name AS dog_name, 'Reciente' AS date 
        FROM Person P 
        JOIN Adoption A ON P.id = A.adopter_id 
        JOIN Pet Dog ON A.dog_id = Dog.id 
        ORDER BY A.id DESC;
        """
        cur.execute(query)
        return cur.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def login_user(username, password):
    conn = get_db_connection()
    if not conn: return None
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT role FROM Users WHERE username = %s AND password = %s", (username, password))
        return cur.fetchone()
    except Exception as e:
        print(f"Error en login: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def add_new_dog(name, age, breed, image_url):
    conn = get_db_connection()
    if not conn: return False
    cur = conn.cursor()
    try:
        # Importante: is_adopted empieza en 0 porque el perro llega disponible
        cur.execute(
            "INSERT INTO Pet (name, age, breed, image_url, is_adopted) VALUES (%s, %s, %s, %s, 0)",
            (name, age, breed, image_url)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al agregar perro en la base de datos: {e}")
        return False
    finally:
        cur.close()
        conn.close()