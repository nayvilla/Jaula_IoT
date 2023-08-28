from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required

from config import config

# Models:
from models.ModelUser import ModelUser, subirusuario

# Entities:
from models.entities.User import User, hash

app = Flask(__name__)

csrf = CSRFProtect()
db = MySQL(app)
login_manager_app = LoginManager(app)


@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # print(request.form['username'])
        # print(request.form['password'])
        user = User(0, request.form['username'], request.form['password'])
        logged_user = ModelUser.login(db, user)
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('home'))
            else:
                flash("Contraseña Incorrecta...")
                return render_template('auth/login.html')
        else:
            flash("Usuario no encontrado, porfavor registrate...")
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Obtener los datos del formulario
        username = request.form.get('username')
        fullname = request.form.get('fullname')
        password = request.form.get('password')
        email = request.form.get('email')
        cifrado=(hash.has(password))

        # Si los datos del formulario no están completos, muestra la plantilla de registro nuevamente
        if not fullname or not password:
            
            return render_template('auth/registro.html')

        #print(fullname, cifrado)
        # Mostrar un mensaje flash de éxito
        subirusuario.sub(db, username, fullname, cifrado, email)
        flash(f'Registro exitoso. ¡Bienvenido, {username}!', 'success')

        # Redireccionar a la página de inicio de sesión ('auth/login.html')
        return redirect('/login')

    else:
        return render_template('auth/registro.html')

@app.route('/home')
def home():
    # URL a la que deseas redirigir en Ubidots
    url_destino = 'https://stem.ubidots.com/app/dashboards/64b60095b2d816000b7201e8?devices=64b60012b2d816000b7201e6'

    # Redirigir al usuario a la URL de Ubidots
    return redirect(url_destino, code=302)


@app.route('/protected')
@login_required
def protected():
    return "<h1>Esta es una vista protegida, solo para usuarios autenticados.</h1>"


def status_401(error):
    return redirect(url_for('login'))


def status_404(error):
    return "<h1>Página no encontrada</h1>", 404


if __name__ == '__main__':
    app.config.from_object(config['development'])
    csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run()
