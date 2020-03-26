from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from files import UPLOAD_FOLDER

from os import environ

#Imports
from controller.user import UserRegister, UserLogin
from controller.dog import DogController,DogListController,DogObservationController, DogUploadImage, DogManage
from controller.session import SessionController, SessionManage
from controller.toma import TomaController, TomaManage, TomaUploadSensors, TomaUploadVideo

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.secret_key = environ.get('SECRET_KEY')
api = Api(app)

jwt = JWTManager(app)

api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')

api.add_resource(DogController, '/dog/<string:id>',)
api.add_resource(DogManage, '/dog',)

api.add_resource(DogListController, '/dogs')
api.add_resource(DogObservationController, '/observation/dog')
api.add_resource(DogUploadImage, '/dog/upload/image')

api.add_resource(SessionController, '/dog/session/<string:id>')
api.add_resource(SessionManage, '/dog/session/manage')

api.add_resource(TomaController, '/dog/toma/<string:id>')
api.add_resource(TomaManage, '/dog/toma/manage')

api.add_resource(TomaUploadVideo, '/dog/toma/upload/video/<string:id>')
api.add_resource(TomaUploadSensors, '/dog/toma/upload/sensor/<string:id>')


if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run( port= 5000, debug = True)