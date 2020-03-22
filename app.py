from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

#Imports
from controller.user import UserRegister, UserLogin
from controller.dog import DogController,DogListController,DogObservationController


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Dont track every changes to objects.
# TODO cambiar secret key, mirar variables .env
app.secret_key = 'cambiarla'
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()

jwt = JWTManager(app)

api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(DogController, '/dog/get/<string:id>', '/dog/create')
api.add_resource(DogListController, '/dogs/get')
api.add_resource(DogObservationController, '/dog/comment/create')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run( port= 5000, debug = True)