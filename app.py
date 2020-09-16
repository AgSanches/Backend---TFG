from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS, cross_origin
from files import UPLOAD_FOLDER
from model.user import User
from os import environ
import torch.nn as nn # Neural Networks
import torch



# Imports
from controller.user import UserRegister, UserLogin, UserController, UserList, UserPassword
from controller.dog import DogController, DogListController, DogObservationController, DogImage, DogManage, DogFindByName
from controller.session import SessionController, SessionManage, SessionsDogs, SessionsDogsByName
from controller.toma import TomaController, TomaManage, TomaManageSensors, TomaManageVideo, TomaGetVideo, TomaByName, TomaReadSensors, TomaGiveResults

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
api.add_resource(TomaGiveResults, '/dog/toma/result/<string:id>')

api.add_resource(TomaGetVideo, '/dog/toma/video/<string:id>/<string:name>')

class LSTM(nn.Module):
    def __init__(self, hidden_size=256, input_size=1, output_size=1, dropout=0.5, num_layers=2):
        super(LSTM, self).__init__()

        self.input = input_size
        self.hidden = hidden_size
        self.output = output_size
        self.n_layers = num_layers

        # Definición LSTM
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout
        )

        # Definición Fully-Connected
        self.fc = nn.Linear(
            hidden_size,
            output_size
        )

    def forward(self, state, hidden):

        batch_size = state.size(0)

        state = state.float()
        # Obtener valores de LSTM
        output_lstm, hidden = self.lstm(state, hidden)

        # Agrupar salidas LSTM
        output_lstm = output_lstm.contiguous().view(-1, self.hidden)

        # Pasar salida por FC
        output = self.fc(output_lstm)

        # Convertir salida para obtener el último valor
        output = output.view(batch_size, -1, self.output)
        output = output[:, -1]

        return output, hidden

    def init_hidden(self, batch_size):
        weight = next(self.parameters()).data

        if (torch.cuda.is_available()):
            hidden = (
                weight.new(self.n_layers, batch_size, self.hidden).zero_().cuda(),
                weight.new(self.n_layers, batch_size, self.hidden).zero_().cuda()
            )
        else:
            hidden = (weight.new(self.n_layers, batch_size, self.hidden).zero_(),
                      weight.new(self.n_layers, batch_size, self.hidden).zero_())

        return hidden

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)
