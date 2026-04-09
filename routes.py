from flask import Flask, render_template, request, redirect, url_for, session
import database
import models

app = Flask(__name__)
# Esta llave es obligatoria para que el Login funcione
app.secret_key = 'mi_llave_secreta_123'

@app.route('/')
def index():
    # Si no han iniciado sesión, los mandamos al login
    if 'username' not in session:
        return redirect(url_for('login'))
        
    perros = database.get_available_dogs()
    return render_template('index.html', perros=perros)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        
        account = database.login_user(user, pw)
        
        if account:
            session['username'] = user
            session['role'] = account['role']
            return redirect(url_for('index'))
        else:
            return "Usuario o contraseña incorrectos. <a href='/login'>Intentar de nuevo</a>"
            
    return render_template('login.html')

@app.route('/agregar_perro', methods=['GET', 'POST'])
def agregar_perro():
    # Seguridad: Solo admin
    if session.get('role') != 'admin':
        return "Acceso denegado", 403

    if request.method == 'POST':
        nombre = request.form['name']
        edad = request.form['age']
        raza = request.form['breed']
        imagen = request.form['image_url'] # Aquí pondrás el nombre del archivo (ej: nuevo.jpg)
        
        if database.add_new_dog(nombre, edad, raza, imagen):
            return redirect(url_for('index'))
        else:
            return "Error al guardar en la base de datos"

    return render_template('agregar_perro.html')

@app.route('/adoptar/<int:id>')
def adoptar(id):
    if 'username' not in session:
        return redirect(url_for('login'))
        
    perrito_encontrado = database.get_dog_by_id(id)
    if perrito_encontrado is None:
        return "Perro no encontrado", 404
    return render_template('confirmacion.html', dog=perrito_encontrado)

@app.route('/confirmar_adopcion', methods=['POST'])
def procesar_adopcion():
    dog_id = request.form['dog_id']
    name = request.form['name']
    lastname = request.form['lastname']
    address = request.form['address']
    id_card = request.form['id_card']
    
    success = database.register_adoption_transactional(dog_id, name, lastname, address, id_card)
    
    if success:
        dog = database.get_dog_by_id(dog_id)
        return f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
            body {{ font-family: 'Poppins', sans-serif; background-color: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .success-card {{ background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center; }}
            h1 {{ color: #27ae60; }}
            .btn-back {{ display: inline-block; padding: 12px 30px; background-color: #e67e22; color: white; text-decoration: none; border-radius: 25px; font-weight: bold; }}
        </style>
        <div class="success-card">
            <h1>¡Felicidades!</h1>
            <p>Has adoptado a <strong>{dog['name']}</strong> exitosamente.</p>
            <a href="/" class="btn-back">Volver al catálogo</a>
        </div>
        """
    else:
        return "Error al procesar la adopción. <a href='/'>Volver</a>"

@app.route('/historial')
def historial():
    # Solo el admin puede entrar aquí
    if session.get('role') != 'admin':
        return "Acceso denegado. Solo administradores.", 403
        
    adopciones = database.get_adoption_history()
    return render_template('historial.html', adopciones=adopciones)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)