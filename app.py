from flask import Flask, render_template, request, jsonify, redirect, url_for
from entities.user import User
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "index"


@login_manager.user_loader
def load_user(id_user):
    return User.get_by_id(id_user)


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route('/welcome', methods=["GET"])
@login_required
def welcome():
    return render_template("welcome.html")


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


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

"""@app.route("/api/welcome", methods=["GET"])
@login_required
def check_account():
    user_id = int(request.cookies.get("id"))
    has_account = Account.check_account(user_id)

    return jsonify({"has_account": has_account}), 200
"""


if __name__ == '__main__':
    app.run()






'''
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/login')
def login():
    # Dejare el is_active para mas tarde por mi salud mental
    return render_template('login.html')


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')


@app.route('/api/login', methods=['POST'])
def api_login():
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run()
'''
