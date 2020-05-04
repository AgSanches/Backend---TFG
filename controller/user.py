from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token 
from model.user import User
from flask_jwt_extended import jwt_required, get_current_user, get_jwt_claims

def getParserLogin():
    _user_parser = reqparse.RequestParser()

    _user_parser.add_argument('email',
                              type=str, required=True,
                              help="El email se encuentra vacío")

    _user_parser.add_argument('password',
                             type=str, required=True,
                             help="La contraseña se encuentra vacía")

    return _user_parser

def getParserUser():

    _user_parser = getParserUpdate()

    _user_parser.add_argument('password',
                             type=str, required=True,
                             help="La contraseña se encuentra vacía")

    return _user_parser

def getParserUpdate():

    _user_parser = reqparse.RequestParser()

    _user_parser.add_argument('name',
                              type=str, required=True,
                              help="Nombre vacío")

    _user_parser.add_argument('surname',
                              type=str, required=True,
                              help="Apellido vacío")

    _user_parser.add_argument('email',
                              type=str, required=True,
                              help="El email se encuentra vacío")

    return _user_parser

class UserRegister(Resource):

    @jwt_required
    def post(self):

        claims = get_jwt_claims()

        if not claims['isAdmin'] :
            return {"message": "No está autorizado"},  401

        user_parser = getParserUser()

        data = user_parser.parse_args()

        if User.findUserByEmail(data['email']):
            return {
                'message' : 'Usuario existente, pruebe otra dirección de correo'
                }, 400

        user = User(
            data['name'],
            data['surname'],
            data['email'],
            generate_password_hash(data['password'],method='pbkdf2:sha256'),
            2
            )

        try:
            user.save_to_db()
        except:
            return {'message' : 'No se ha podido crear el usuario, vuelva a intentarlo más tarde'}, 500

        return {'message' : 'Usuario creado correctamente!'}, 201

class UserLogin(Resource):

    def post(self):

        data = getParserLogin().parse_args()

        user = User.findUserByEmail(data['email'])

        if user and check_password_hash(user.password, data['password']):

            access_token = create_access_token(identity = user.id, fresh = True)
            refresh_token = create_refresh_token(user.id)

            return {
                'name' : user.name,
                'surname' : user.surname,
                'email': user.email,
                'role': user.role,
                'access_token' : access_token,
                'refresh_token' : refresh_token
            }, 200

        return {'message' : 'Credenciales no válidas'}, 401

class UserController(Resource):

    @jwt_required
    def get(self, id):

        claims = get_jwt_claims()

        if not claims['isAdmin']:
            return {"message": "No está autorizado"}, 401

        user = User.findUserById(id)

        if not user:
            return { message: "Usuario no existente" }, 404

        return user.jsonOutput()

    @jwt_required
    def put(self, id):

        claims = get_jwt_claims()

        if not claims['isAdmin']:
            return {"message": "No está autorizado"}, 401

        user_parser = getParserUpdate()

        user = User.findUserById(id)

        data = user_parser.parse_args()

        if not user:
            return { message: "Usuario no existente" }, 404

        if data['email'] != user.email and User.findUserByEmail(data['email']):
            return { 'message' : 'Email no válido, pruebe otra dirección de correo' }, 400

        user.update(**data)

        try:
            user.save_to_db()
        except:
            return {'message': 'No se ha podido actualizar el usuario, vuelva a intentarlo más tarde'}, 500

        return user.jsonOutput(), 200

    @jwt_required
    def delete(self, id):

        claims = get_jwt_claims()

        if not claims['isAdmin']:
            return {"message": "No está autorizado"}, 401

        user = User.findUserById(id)

        if not user:
            return { 'message': "Usuario no existente" }, 404

        try:
            user.delete_from_db()
        except:
            return { 'message': "No se ha podido eliminar el usuario, pruebe en otro momento" }, 500

        return { 'message': "Usuario eliminado" }, 200

class UserList(Resource):

    @jwt_required
    def get(self):
        claims = get_jwt_claims()

        if not claims['isAdmin']:
            return {"message": "No está autorizado"}, 401

        users = User.getUsers()

        return [user.jsonOutput() for user in users]

class UserPassword(Resource):

    @jwt_required
    def put(self, id):

        claims = get_jwt_claims()

        if not claims['isAdmin']:
            return {"message": "No está autorizado"}, 401

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