from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS, cross_origin
from files import UPLOAD_FOLDER
from model.user import User
from os import environ

# Imports
from controller.user import UserRegister, UserLogin, UserController, UserList, UserPassword
from controller.dog import DogController, DogListController, DogObservationController, DogImage, DogManage, DogFindByName
from controller.session import SessionController, SessionManage, SessionsDogs, SessionsDogsByName
from controller.toma import TomaController, TomaManage, TomaManageSensors, TomaManageVideo, TomaGetVideo, TomaByName, TomaReadSensors

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600 * 24 * 2 #JWT Access Token Expiration 2 days.

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.secret_key = str(environ.get('SECRET_KEY')) + "adrian"
api = Api(app)

jwt = JWTManager(app)

@jwt.user_claims_loader
def addClaimsJwt(identity):
    user = User.findUserById(identity)
    if not user or user.role != 1:
        return {'isAdmin': False}
    return {'isAdmin': True}

api.add_resource(UserRegister, '/user')
api.add_resource(UserController, '/user/<string:id>')
api.add_resource(UserList, '/users')
api.add_resource(UserLogin, '/login')
api.add_resource(UserPassword, '/user/change-password/<string:id>')

api.add_resource(DogController, '/dog/<string:id>',)
api.add_resource(DogFindByName, '/dog/name/<string:name>',)
api.add_resource(DogManage, '/dog',)

api.add_resource(DogListController, '/dogs')
api.add_resource(DogObservationController, '/observation/dog')
api.add_resource(DogImage, '/dog/image/<string:id>')

api.add_resource(SessionController, '/dog/session/<string:id>')
api.add_resource(SessionsDogs, '/dog/sessions/<string:id>')
api.add_resource(SessionsDogsByName, '/dog/sessions/<string:id>/<string:name>')

api.add_resource(SessionManage, '/dog/session/manage')

api.add_resource(TomaController, '/dog/toma/<string:id>')
api.add_resource(TomaByName, '/dog/toma/<string:id>/<string:name>')
api.add_resource(TomaManage, '/dog/toma/manage')

api.add_resource(TomaManageVideo, '/dog/toma/video/upload/<string:id>')
api.add_resource(TomaManageSensors, '/dog/toma/sensor/upload/<string:id>')

api.add_resource(TomaReadSensors, '/dog/toma/sensor/<string:id>')

api.add_resource(TomaGetVideo, '/dog/toma/video/<string:id>/<string:name>')

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)
