from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from flask import Flask, render_template, request, jsonify, redirect, url_for
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from entities.user import User
from entities.word import Word
from entities.winner import Winner
import hashlib
import base64
import os



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


# Ruta para editar niveles (solo administrador)
@app.route('/edit_level', methods=["GET"])
@login_required
def edit_level():
    # Si el perfil del usuario no es 1 (administrador), redirigir a la página de bienvenida
    if current_user.profile.value != 1:
        return redirect(url_for('welcome'))
    return render_template('edit_level.html')


# API: lista de IDs disponibles en la tabla words
@app.route('/api/words', methods=['GET'])
@login_required
def api_list_words():
    ids = Word.list_ids()
    return jsonify({ 'ids': ids })


# API: obtener palabra por id
@app.route('/api/words/<int:word_id>', methods=['GET'])
@login_required
def api_get_word(word_id):
    w = Word.wordbyId(word_id)
    if not w:
        return jsonify({'error': 'not found'}), 404
    word_value = w.word
    secret = app.secret_key or os.getenv('SECRET_KEY') or 'default_secret'
    key_bytes = hashlib.sha256(secret.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    f = Fernet(fernet_key)
    try:
        word_value = f.decrypt(word_value.encode()).decode()
    except Exception:
        # No se pudo descifrar, devolvemos el valor original para no perder datos
        pass
    return jsonify({ 'id': w.id, 'word': word_value, 'phrase': w.phrase, 'character': w.character })


# API: actualizar palabra por id
@app.route('/api/words/<int:word_id>', methods=['POST'])
@login_required
def api_update_word(word_id):
    if current_user.profile.value != 1:
        return jsonify({'success': False, 'message': 'forbidden'}), 403
    data = request.get_json() or {}
    word = data.get('word')
    phrase = data.get('phrase')
    character = data.get('character')
    if word is None or phrase is None:
        return jsonify({'success': False, 'message': 'missing data'}), 400

    try:
        secret = app.secret_key or os.getenv('SECRET_KEY') or 'default_secret'
        key_bytes = hashlib.sha256(secret.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(key_bytes)
        f = Fernet(fernet_key)
        encrypted = f.encrypt(word.encode()).decode()
    except Exception as ex:
        print(f"Encryption error: {ex}")
        return jsonify({'success': False, 'message': 'encryption error'}), 500

    ok = Word.update_word(word_id, encrypted, phrase, character)
    if ok:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'db error'}), 500


# Ruta de la página de récords
@app.route('/records')
@login_required
def records():
    # Datos de prueba simples
    top_10 = [
        {"nombre": "Andrey", "puntos": 2500, "nivel": 10},
        {"nombre": "Migna", "puntos": 2100, "nivel": 8},
        {"nombre": "Miguel", "puntos": 1850, "nivel": 7},
        {"nombre": "Valeria", "puntos": 1200, "nivel": 5},
        {"nombre": "Efraín", "puntos": 950, "nivel": 4}
    ]
    
    # Récord personal del usuario
    user_best = {"nombre": current_user.name, "puntos": 450, "nivel": 2}

    return render_template("records.html", top_10=top_10, user_best=user_best)


# API para obtener la pista de una palabra por su ID
@app.route('/api/juego/palabra/<int:word_id>', methods=['GET'])
def obtener_pista(word_id):
    
    palabra = Word.wordbyId(word_id)
    
    if palabra:
        response_data = {
            'status': 'ok',
            'phrase': palabra.phrase,
            'character': palabra.character if hasattr(palabra, 'character') else 'ayame.png'
        }
        print(f"[obtener_pista] word_id={word_id}, character={response_data['character']}")
        return jsonify(response_data)
    else:
        return jsonify({'status': 'fin'}), 404


# API para guardar el registro de ganador cuando el juego termina
@app.route('/api/juego/guardar_ganador', methods=['POST'])
@login_required
def guardar_ganador():
    data = request.get_json() or {}
    score = data.get('score', 0)

    winner = Winner(None, score, current_user.id)
    if winner.save():
        return jsonify({'success': True}), 201
    return jsonify({'success': False, 'message': 'No se pudo guardar el registro del ganador'}), 500


# API para validar el intento del usuario
@app.route('/api/juego/validar', methods=['POST'])
def validar_intento():
    data = request.json
    word_id = data.get('id')
    intento_usuario = data.get('intento', '').strip().lower()

    palabra = Word.wordbyId(word_id)
    
    if not palabra:
        return jsonify({'error': 'Palabra no encontrada'}), 404

    palabra_real = palabra.word
    secret = app.secret_key or os.getenv('SECRET_KEY') or 'default_secret'
    key_bytes = hashlib.sha256(secret.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    f = Fernet(fernet_key)
    try:
        palabra_real = f.decrypt(palabra_real.encode()).decode()
    except Exception:
        pass

    palabra_real = palabra_real.lower()

    if intento_usuario == palabra_real:
        return jsonify({'correcto': True})
    else:
        return jsonify({'correcto': False})



# Ejecutar la aplicación Flask
if __name__ == '__main__':
    app.run()
