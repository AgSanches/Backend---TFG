from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token 
from model.user import User

_user_parser  = reqparse.RequestParser()

_user_parser.add_argument('email', 
type=str, required=True, 
help="El email se encuentra vacío")

_user_parser.add_argument('password', 
type=str, required=True, 
help="La contraseña se encuentra vacía")

_user_parser.add_argument('name', 
type=str, required=False, 
help="Nombre vacío")

_user_parser.add_argument('surname', 
type=str, required=False, 
help="Apellido vacío")

class UserRegister(Resource):

    def post(self):

        data = _user_parser.parse_args()

        if data['name'] == '' or data['surname'] == '':
            return {
                'message' : 'Nombre o apellido no válido'
                }, 400

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

        data = _user_parser.parse_args()

        user = User.findUserByEmail(data['email'])

        if user and check_password_hash(user.password, data['password']):

            access_token = create_access_token(identity = user.id, fresh = True)
            refresh_token = create_refresh_token(user.id)

            return {
                'name' : user.name,
                'surname' : user.surname,
                'access_token' : access_token,
                'refresh_token' : refresh_token
            }, 200

        return {'message' : 'Credenciales no válidas'}, 401