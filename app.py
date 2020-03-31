from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS, cross_origin

from files import UPLOAD_FOLDER

from os import environ

# Imports
from controller.user import UserRegister, UserLogin
from controller.dog import DogController, DogListController, DogObservationController, DogImage, DogManage, DogFindByName, DogListWithParamsController, DogCount
from controller.session import SessionController, SessionManage
from controller.toma import TomaController, TomaManage, TomaManageSensors, TomaManageVideo, TomaGetVideo

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.secret_key = str(environ.get('SECRET_KEY')) + "adrian"
api = Api(app)

jwt = JWTManager(app)

api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')

api.add_resource(DogController, '/dog/<string:id>',)
api.add_resource(DogFindByName, '/dog/name/<string:name>',)
api.add_resource(DogManage, '/dog',)
api.add_resource(DogCount, '/count/dog',)

api.add_resource(DogListWithParamsController, '/dogs/<int:limit>/<string:order>/<string:method>/<int:offset>')
api.add_resource(DogListController, '/dogs')
api.add_resource(DogObservationController, '/observation/dog')
api.add_resource(DogImage, '/dog/image/<string:id>')

api.add_resource(SessionController, '/dog/session/<string:id>')
api.add_resource(SessionManage, '/dog/session/manage')

api.add_resource(TomaController, '/dog/toma/<string:id>')
api.add_resource(TomaManage, '/dog/toma/manage')

api.add_resource(TomaManageVideo, '/dog/toma/video/upload/<string:id>')
api.add_resource(TomaManageSensors, '/dog/toma/sensor/upload/<string:id>')

api.add_resource(TomaGetVideo, '/dog/toma/video/<string:id>/<string:name>')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)
