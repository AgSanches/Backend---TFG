from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token 
from model.user import User


def getParser():
    _user_parser = reqparse.RequestParser()

    _user_parser.add_argument('email',
                              type=str, required=True,
                              help="El email se encuentra vacío")

    _user_parser.add_argument('password',
                              type=str, required=True,
                              help="La contraseña se encuentra vacía")
    return _user_parser

class UserRegister(Resource):

    def post(self):

        user_parser = getParser()

        user_parser.add_argument('name',
        type=str, required=True,
                                  help="Nombre vacío")

        user_parser.add_argument('surname',
                                  type=str, required=True,
                                  help="Apellido vacío")

        data = user_parser.parse_args()

        if User.findUserByEmail(data['email']):
            return {
                'message' : 'Usuario existente, pruebe otra dirección de correo'
                }, 400

        user = User(
            data['name'],
            data['surname'],
            data['email'],
            generate_password_hash(data['password'],method='pbkdf2:sha256')
            )

        try:
            user.save_to_db()
        except:
            return {'message' : 'No se ha podido crear el usuario, vuelva a intentarlo más tarde'}, 500

        return {'message' : 'Usuario creado correctamente!'}, 201

class UserLogin(Resource):

    def post(self):

        data = getParser().parse_args()

        user = User.findUserByEmail(data['email'])

        if user and check_password_hash(user.password, data['password']):

            access_token = create_access_token(identity = user.id, fresh = True)
            refresh_token = create_refresh_token(user.id)

            return {
                'name' : user.name,
                'surname' : user.surname,
                'email': user.email,
                'access_token' : access_token,
                'refresh_token' : refresh_token
            }, 200

        return {'message' : 'Credenciales no válidas'}, 401

class UserController(Resource):

    def get(self, id):

        user = User.findUserById(id)

        if not user:
            return { message: "Usuario no existente" }, 404

        return user.jsonOutput()

    def put(self, id):

        user_parser = getParser()

        user_parser.add_argument('name',
        type=str, required=True,
                                  help="Nombre vacío")

        user_parser.add_argument('surname',
                                  type=str, required=True,
                                  help="Apellido vacío")

        data = user_parser.parse_args()

        user = User.findUserById(id)

        if not user:
            return { message: "Usuario no existente" }, 404

        if data['email'] != user.email and User.findUserByEmail(data['email']):
            return { 'message' : 'Email no válido, pruebe otra dirección de correo' }, 400

        user.update(**data)

        try:
            user.save_to_db()
        except:
            return {'message': 'No se ha podido actualizar el usuario, vuelva a intentarlo más tarde'}, 500

        return {
                    "user": user.jsonOutput()
               }, 200

class UserList(Resource):

    def get(self):

        users = User.getUsers()

        return [user.jsonOutput() for user in users]

class UserPassword(Resource):
    def put(self, id):
        password_parser = reqparse.RequestParser()

        password_parser.add_argument('password',
            type=str, required=True,
            help="La contraseña se encuentra vacía")

        user = User.findUserById(id)

        if not user:
            return { message: "Usuario no existente" }, 404

        password = password_parser.parse_args()['password']
        user.password = generate_password_hash(password, method='pbkdf2:sha256')

        try:
            user.save_to_db()
        except:
            return {'message': 'No se ha podido actualizar la '
                               'contraseña, vuelva a intentarlo más tarde'}, 500
        return {
            'message' : "Contraseña cambiada con éxito."
        }, 200