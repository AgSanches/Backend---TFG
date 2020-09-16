from flask_restful import Resource, reqparse
from model.session import Session
from model.toma import Toma
from flask import send_file
import werkzeug
from files import allowed_video,save_file, allowed_sensors, checkFileExists, getFile
import pandas as pd
from flask_jwt_extended import jwt_required
import numpy as np
import torch

def getTomaParser():

    toma_parser  = reqparse.RequestParser()

    toma_parser.add_argument('name', 
        type=str, required=True,
        help="El nombre se encuentra vacío")

    toma_parser.add_argument('conclusion_expert',
        type=str, required=False)

    return toma_parserdef

def getTomaObservationParser():

    toma_parser  = reqparse.RequestParser()

    toma_parser.add_argument('name',
        type=str, required=False)

    toma_parser.add_argument('conclusion_expert',
        type=str, required=False)

    return toma_parser

def getTomaFilesParser():

    toma_parser  = reqparse.RequestParser()

    toma_parser.add_argument('toma_id', 
    type=str, required=True, 
    help="Seleccione una toma destino")

    return toma_parser

def manageDataToma(data, toma, allowed_item):

    returnDict = {}

    for key,content in data.items():

            if content == None:
                continue

            if allowed_item(content.filename):
                name = toma.getFileName(key) + '.' + content.filename.split('.')[1]
                returnDict[name] = content, key
    
    return returnDict

class TomaManage(Resource):

    @jwt_required
    def post(self):

        toma_parser = getTomaParser()

        toma_parser.add_argument('session_id', 
        type=int, required=True, 
        help="Hay que asignar una sesión destino")

        data = toma_parser.parse_args()

        if not Session.getSessionById(data['session_id']):
            return {"message" : "Sesión no existente"}, 404

        toma = Toma(**data)
        
        try:
            toma.save_to_db()
        except:
            return {"message": "No se ha podido guardar la toma"}, 500

        return toma.jsonOutput()

class TomaController(Resource):

    @jwt_required
    def get(self, id):

        toma = Toma.getTomaById(id)

        if not toma:
            return {
                'message': 'No se ha encontrado ninguna toma con este id: {}'.format(id)
                }, 404

        return toma.jsonOutput()

    @jwt_required
    def delete(self, id):

        toma = Toma.getTomaById(id)

        if not toma:
            return {
                'message': 'No se ha encontrado ninguna toma con este id: {}'.format(id)
                }, 404

        try:
            toma.delete_from_db()
        except:
            return {'message' : 'No se ha podido eliminar la toma'}, 500

        return {'message' : 'Toma eliminada'}

    @jwt_required
    def put(self, id):

        toma_parser = getTomaObservationParser()

        data = toma_parser.parse_args()

        toma = Toma.getTomaById(id)

        if not toma:
            return {'message' : 'No existe una toma con el id suministrado'}, 404

        toma.update(**data)

        try:
            toma.save_to_db()
        except:
            return {'message' : 'No se ha podido actualizar la toma'}, 500

        return toma.jsonOutput()

class TomaGetVideo(Resource):

    def get(self, id, name):

        if name not in ['front', 'middle', 'back']:
            return {'message': "Especifica que tipo de video deseas obtener, front, middle o back"}, 400

        toma = Toma.getTomaById(id)

        if toma is None:
            return {'message' : "La toma no existe"}, 404

        if name == 'front':
            video = toma.video_front
        elif name == 'middle':
            video = toma.video_middle
        else:
            video = toma.video_back

        if video == '' or  not checkFileExists(toma.getFolder(), video):
            return {'El video pedido no existe'}, 404

        return send_file(getFile(toma.getFolder(), video))

class TomaManageVideo(Resource):

    @jwt_required
    def post(self, id):

        file_parser = reqparse.RequestParser()

        file_parser.add_argument(
        'video_front', type = werkzeug.datastructures.FileStorage, required = False, location = "files", 
        help="Añade un video frontal")

        file_parser.add_argument(
        'video_middle', type = werkzeug.datastructures.FileStorage, required = False, location = "files", 
        help="Añade un video lateral")

        file_parser.add_argument(
        'video_back', type = werkzeug.datastructures.FileStorage, required = False, location = "files", 
        help="Añade un video trasero")

        data = file_parser.parse_args()

        toma = Toma.getTomaById(id)

        if toma is None:
            return {'message' : 'Toma no existente'}, 404

        videos = manageDataToma(data, toma, allowed_video)

        if len(videos) < 1:
            return {'message' : 'No se han enviado videos o no son archivos correctos.'}, 400
        
        for key, video in videos.items():
            status = save_file(toma.getFolder(), key ,video[0])
            if not status[0]:
                return {'Ha ocurrido un problema al almacenar uno de los videos, vuelva a intentarlo'}, 500
            
            if video[1] == 'video_front':
                toma.video_front = key
            elif video[1] == 'video_middle':
                toma.video_middle = key
            else:
                toma.video_back = key

        try:
            toma.save_to_db()
        except:
            return {'message': "Ha ocurrido un problema al almacenar los datos, vuelva a intentarlo"},500
            
        return toma.jsonOutput()

class TomaManageSensors(Resource):

    @jwt_required
    def post(self, id):
        file_parser = reqparse.RequestParser()

        file_parser.add_argument(
        'sensor_data_front', type = werkzeug.datastructures.FileStorage, 
        required = False, location = "files")

        file_parser.add_argument(
        'sensor_data_back', type = werkzeug.datastructures.FileStorage, 
        required = False, location = "files")

        file_parser.add_argument(
        'sensor_data_foot_upper', type = werkzeug.datastructures.FileStorage,
        required = False, location = "files")

        file_parser.add_argument(
        'sensor_data_foot_lower', type = werkzeug.datastructures.FileStorage,
        required = False, location = "files")

        data = file_parser.parse_args()

        toma = Toma.getTomaById(id)

        if toma is None:
            return {'message' : 'Toma no existente'}, 404

        sensors = manageDataToma(data, toma, allowed_sensors)

        if len(sensors) < 1:
            return {'message' : 'No se han enviado datos o no son archivos correctos.'}, 400
        
        for key, sensor in sensors.items():
            status = save_file(toma.getFolder(), key ,sensor[0])
            if not status[0]:
                return {'Ha ocurrido un problema al almacenar uno de los datos, vuelva a intentarlo'}, 500
            
            if sensor[1] == 'sensor_data_front':
                toma.sensor_data_front = key
            elif sensor[1] == 'sensor_data_back':
                toma.sensor_data_back = key
            elif sensor[1] == 'sensor_data_foot_upper':
                toma.sensor_data_foot_upper = key
            elif sensor[1] == 'sensor_data_foot_lower':
                toma.sensor_data_foot_lower = key
            
        try:
            toma.save_to_db()
        except:
            return {'message': "Ha ocurrido un problema al almacenar los datos, vuelva a intentarlo"},500
        
        return toma.jsonOutput()

class TomaByName(Resource):

    @jwt_required
    def get(self, id, name):

        if not Session.getSessionById(id):
            return {'message': "No existe ninguna sesión con id {}".format(id)}, 404

        return {
            'tomas' : [toma.jsonOutput() for toma in Toma.getTomaByName(name, id)]
        }

class TomaGiveResults(Resource):

    def pad_features(self, inputData, seq_length):
        features = np.zeros(seq_length, dtype=int)
        features[-len(inputData):] = inputData[0:seq_length]

        return features

    def predict(self, model, test, sequence_length):
        model.eval()

        # pad tokenized sequence
        seq_length = sequence_length
        features = self.pad_features(test, seq_length)
        # convert to tensor to pass into your model
        feature_tensor = torch.from_numpy(features)

        # initialize hidden state
        h = model.init_hidden(1)

        if (torch.cuda.is_available()):
            model.cuda()
            feature_tensor = feature_tensor.cuda()

        # get the output from the model
        output, h = model(feature_tensor.view(1, -1, 1), h)
        # printing output value, before rounding
        print('Predicción: {:.6f}'.format(output.item()))
        return output.item()

    @jwt_required
    def get(self, id):

        toma = Toma.getTomaById(id)

        if toma is None:
            return {'message' : "La toma no existe"}, 404

        if toma.conclusion_ia:
            return {
                'result': toma.conclusion_ia
            }

        if toma.sensor_data_back:
            try:
                sequence_length = 250

                print(getFile(toma.getFolder(), toma.sensor_data_back))

                df = pd.read_csv(
                    getFile(toma.getFolder(), toma.sensor_data_back),
                    skiprows=4,
                    sep="\t"
                )

                sensor_data = df["Roll"][50:].tolist()

                features = self.pad_features(sensor_data, sequence_length)

                # Read model
                model = torch.load('./data/model1.pt', map_location=torch.device('cpu'))

                # Predict
                output = self.predict(model, features, sequence_length)
                toma.conclusion_ia = output

                # Save result
                toma.save_to_db()

                # Return result
                return {
                    'toma': toma.jsonOutput()
                }

            except FileNotFoundError:
                return {'message': 'Ha ocurrido un problema, no se encuentra el archivo'}, 500
            except UnicodeDecodeError:
                return { 'message' : 'Ha ocurrido un problema'}, 500

        else:
            return { 'message' : 'La toma no cuenta con datos'}, 404

class TomaReadSensors(Resource):

    @jwt_required
    def get(self, id):

        toma = Toma.getTomaById(id)

        if toma is None:
            return {'message' : "La toma no existe"}, 404

        data = {}
        if toma.sensor_data_front:
            try:
                sensor_data = pd.read_csv(
                    getFile(toma.getFolder(), toma.sensor_data_front),
                    skiprows=4,
                    sep="\t"
                )
                sensor_data.fillna(0,inplace=True)
                data['front_data'] = list(sensor_data['Roll'])
            except FileNotFoundError:
                data['front_data'] = []
            except UnicodeDecodeError:
                data['front_data'] = []

        if toma.sensor_data_back:
            try:
                sensor_data = pd.read_csv(
                    getFile(toma.getFolder(), toma.sensor_data_back),
                    skiprows=4,
                    sep="\t"
                )
                sensor_data.fillna(0,inplace=True)
                data['back_data'] = list(sensor_data['Roll'])
            except FileNotFoundError:
                data['back_data'] = []
            except UnicodeDecodeError:
                data['back_data'] = []

        if toma.sensor_data_foot_upper:
            try:
                sensor_data = pd.read_csv(
                    getFile(toma.getFolder(), toma.sensor_data_foot_upper),
                    skiprows=4,
                    sep="\t"
                )
                sensor_data.fillna(0,inplace=True)
                data['sensor_data_foot_upper'] = list(sensor_data['Roll'])
            except FileNotFoundError:
                data['sensor_data_foot_upper'] = []
            except UnicodeDecodeError:
                data['sensor_data_foot_upper'] = []

        if toma.sensor_data_foot_lower:
            try:
                sensor_data = pd.read_csv(
                    getFile(toma.getFolder(), toma.sensor_data_foot_lower),
                    skiprows=4,
                    sep="\t"
                )
                sensor_data.fillna(0,inplace=True)
                data['sensor_data_foot_lower'] = list(sensor_data['Roll'])
            except FileNotFoundError:
                data['sensor_data_foot_lower'] = []
            except UnicodeDecodeError:
                data['sensor_data_foot_lower'] = []

        if toma.sensor_data_front and toma.sensor_data_back:
            min_range = max(len(data['front_data']), len(data['back_data']))
        else:
            min_range = 0


        return {
            "labels": [i+1 for i in range(min_range)],
            "data": data
        }

