from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from bson import ObjectId 
app = Flask(__name__)
bcrypt = Bcrypt(app)

# Configura la conexión a MongoDB
client = MongoClient('mongodb://mi-mongo-container:27017/')
db = client.tecsup  # Nombre de la base de datos en MongoDB

@app.route('/api/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.json.get('email')

        if not email:
            return jsonify({'error': 'Faltan datos obligatorios'}), 400

        # Buscar el usuario en la colección de usuarios
        user = db.usuarios.find_one({'email': email})

        if user:
            # Convertir el ObjectId a cadena para incluirlo en la respuesta
            user_id = str(user['_id'])
            return jsonify({'user_id': user_id}), 200

    return jsonify({'error': 'Credenciales inválidas'}), 401
@app.route('/api/usuarios', methods=['POST'])
def agregar_usuario():
    if request.method == 'POST':
        # Obtener los datos del nuevo usuario desde la solicitud
        nombre = request.json.get('nombre')
        apellidos = request.json.get('apellidos')
        email = request.json.get('email')
        password = request.json.get('password')
        telefono = request.json.get('telefono')

        # Validar que los campos requeridos no estén vacíos
        if not nombre or not apellidos or not email or not password:
            return jsonify({'error': 'Faltan datos obligatorios'}), 400

        try:
            # Insertar el nuevo usuario en la colección de usuarios
            user_data = {
                'nombre': nombre,
                'apellidos': apellidos,
                'email': email,
                'password': bcrypt.generate_password_hash(password).decode('utf-8'),
                'telefono': telefono
            }

            result = db.usuarios.insert_one(user_data)

            if result.inserted_id:
                return jsonify({'message': 'Usuario agregado correctamente'}), 201
            else:
                return jsonify({'error': 'No se pudo agregar el usuario'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Ruta para obtener todos los usuarios (Listar)
@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = list(db.usuarios.find())
    # Convierte el ObjectId a cadena para cada usuario
    for usuario in usuarios:
        usuario['_id'] = str(usuario['_id'])
    return jsonify(usuarios)
# Ruta para eliminar un usuario por su ID
@app.route('/api/usuarios/<string:id>', methods=['DELETE'])
def eliminar_usuario(id):
    result = db.usuarios.delete_one({'_id': id})

    if result.deleted_count > 0:
        return jsonify({'message': 'Usuario eliminado'})
    else:
        return jsonify({'error': 'No se encontró el usuario para eliminar'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
