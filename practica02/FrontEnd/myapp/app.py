from flask import Flask, render_template, request, session, redirect
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
import os
import pathlib


import requests
from flask import Flask, session, abort, redirect, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

app = Flask("Google Login App")
app.secret_key = "CodeSpecialist.com"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "436740255304-i0otosm2kpfqt15tbfos4p1kmg2mh993.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://ec2-18-224-68-202.us-east-2.compute.amazonaws.com/callback"
)

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        response = requests.post('http://ec2-18-224-68-202.us-east-2.compute.amazonaws.com/api/login', json={'email': email, 'password': password})

        if response.status_code == 200 and 'user_id' in response.json():
            session['user_id'] = response.json()['user_id']
            return redirect('/menu')

        return render_template('login.html', error='Credenciales inválidas')

    return render_template('login.html')

@app.route('/google_login')
def google_login():
    authorization_url, state = flow.authorization_url()
    return redirect(authorization_url)


@app.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    id_info = id_token.verify_oauth2_token(
        credentials.id_token, google.auth.transport.requests.Request())

    response = requests.post('http://ec2-18-224-68-202.us-east-2.compute.amazonaws.com/api/login', json={'email': id_info['email'], 'password': ''})

    if response.status_code == 200:
        user_id = response.json().get('user_id')
        if user_id:
            session['user_id'] = user_id
            return redirect('/menu')

    return render_template('error.html', error='No se pudo verificar el usuario')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        telefono = request.form['telefono']

        # Realiza una solicitud a la API para registrar un nuevo usuario
        response = requests.post('http://ec2-18-224-68-202.us-east-2.compute.amazonaws.com/api/usuarios', json={
            'nombre': nombre,
            'apellidos': apellidos,
            'email': email,
            'password': password,
            'telefono': telefono
        })

        if response.status_code == 201:
            return redirect('/login')
        else:
            return render_template('register.html', error='No se pudo registrar el usuario')

    return render_template('register.html')

@app.route('/menu')
def menu():
    if 'user_id' in session:
        return render_template('home.html')
    else:
        return redirect('/login')

# Ruta para mostrar todos los usuarios
@app.route('/usuarios')
def usuarios():
    if 'user_id' in session:
        # Realiza una solicitud a la API para obtener la lista de usuarios
        response = requests.get('http://ec2-18-224-68-202.us-east-2.compute.amazonaws.com/api/usuarios')
        if response.status_code == 200:
            usuarios = response.json()
            return render_template('usuarios.html', usuarios=usuarios)
        else:
            return render_template('usuarios.html', error='No se pueden cargar los usuarios')
    else:
        return redirect('/login')

@app.route('/usuarios/eliminar/<int:id>', methods=['GET', 'POST'])
def eliminar_usuario(id):
    if 'user_id' in session:
        # Realiza una solicitud a la API para eliminar un usuario por su ID
        response = requests.delete(f'http://ec2-18-224-68-202.us-east-2.compute.amazonaws.com/api/usuarios/{id}')
        if response.status_code == 200:
            return redirect('/usuarios')
        else:
            return render_template('usuarios.html', error='No se pudo eliminar el usuario')
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
