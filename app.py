from flask import Flask, render_template, request, jsonify, redirect, url_for
from entities.user import User
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from dotenv import load_dotenv
import os

from entities.word import Word

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configuración de la aplicación Flask
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "index"



# Función para cargar el usuario a partir de su ID, requerida por Flask-Login
@login_manager.user_loader
def load_user(id_user):
    return User.get_by_id(id_user)


# Rutas de la aplicación
@app.route('/')
def index():
    return render_template('index.html')


# Ruta para la página de registro de usuarios
@app.route("/signup")
def signup():
    return render_template("signup.html")


# Ruta para la página de bienvenida después de iniciar sesión
@app.route('/welcome', methods=["GET"])
@login_required
def welcome():
    return render_template("welcome.html")


# Ruta para crear un nuevo usuario a través de una solicitud POST
@app.route('/api/users', methods=["POST"])
def create_user():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if User.check_email_exists(email):
        return jsonify({"success": False, "message": "El correo electrónico ingresado ya se encuentra registrado."}), 409

    if User.save(name, email, password):
        return jsonify({"success": True, "message": "Su cuenta fue creada correctamente."}), 201
    else:
        return jsonify({"success": False, "message": "Ocurrió un error al crear su cuenta. Intente de nuevo"}), 500


# Ruta para iniciar sesión a través de una solicitud POST
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = User.check_login(email, password)

    # Validar si la cuenta del usuario esta activa
    if user:
        if user.is_active:
            login_user(user)
            return jsonify({
                "success": True,
                "message": "Sesión iniciada correctamente"
            }), 200
        else:
            return jsonify({
                "success": False,
                "deactivated": True,
                "message": "Su cuenta ha sido desactivada. Comuniquese con el administrador del sistema."
            }), 401
    else:
        return jsonify({
            "success": False,
            "message": "Los datos de acceso ingresados no son correctos."
        }), 401


# Ruta para cerrar sesión
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# Ruta para la página del juego
@app.route('/game', methods=["GET"])
@login_required
def game():
    return render_template("game.html")

#ruta del nivel 1
@login_required
@app.route('/nivel1')
def nivel1():
    return render_template("nivel1.html")



@app.route('/api/juego/palabra/<int:word_id>', methods=['GET'])
def obtener_pista(word_id):
    
    palabra = Word.wordbyId(word_id)
    
    if palabra:
        return jsonify({
            'status': 'ok',
            'phrase': palabra.phrase 
        })
    else:
        return jsonify({'status': 'fin'}), 404

@app.route('/api/juego/validar', methods=['POST'])
def validar_intento():
    data = request.json
    word_id = data.get('id')
    intento_usuario = data.get('intento', '').strip().lower()

    palabra = Word.wordbyId(word_id)
    
    if not palabra:
        return jsonify({'error': 'Palabra no encontrada'}), 404

    palabra_real = palabra.word.lower()

    if intento_usuario == palabra_real:
        return jsonify({'correcto': True})
    else:
        return jsonify({'correcto': False})



# Ejecutar la aplicación Flask
if __name__ == '__main__':
    app.run()
