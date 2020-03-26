from flask_restful import Resource, reqparse
from model.session import Session
from model.toma import Toma
import werkzeug
from files import allowed_video,save_file, allowed_sensors

def getTomaParser():

    toma_parser  = reqparse.RequestParser()

    toma_parser.add_argument('name', 
    type=str, required=True, 
    help="El nombre se encuentra vacío")

    toma_parser.add_argument('conclusion_ia', 
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

    def post(self):

        toma_parser = getTomaParser()

        toma_parser.add_argument('session_id', 
        type=int, required=True, 
        help="Hay que asignar una sesión destino")

        data = toma_parser.parse_args()

        if not Session.getSessionById(data['session_id']):
            return {"message" : "Sesión no existente"},404

        toma = Toma(**data)
        
        try:
            toma.save_to_db()
        except:
            return {"message": "No se ha podido guardar la toma"}, 500

        return toma.jsonOutput()

    def put(self):

        toma_parser = getTomaParser()

        toma_parser.add_argument('toma_id', 
        type=int, required=True, 
        help="Hay que asignar una toma destino")

        data = toma_parser.parse_args()
        toma = Toma.getTomaById(data['toma_id'])

        if not toma:
            return {'message' : 'No existe una toma con el id suministrado'}, 404

        del data['toma_id']
        toma.update(**data)

        try:
            toma.save_to_db()
        except:
            return {'message' : 'No se ha podido actualizar la toma'}, 500

        return toma.jsonOutput()

class TomaController(Resource):
    
    def get(self, id):

        toma = Toma.getTomaById(id)

        if not toma:
            return {
                'message': 'No se ha encontrado ninguna toma con este id: {}'.format(id)
                }, 404

        return toma.jsonOutput()

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

class TomaUploadVideo(Resource):

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

class TomaUploadSensors(Resource):
    
    def post(self, id):
        file_parser = reqparse.RequestParser()

        file_parser.add_argument(
        'sensor_data_front', type = werkzeug.datastructures.FileStorage, 
        required = False, location = "files")

        file_parser.add_argument(
        'sensor_data_back', type = werkzeug.datastructures.FileStorage, 
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
            
        try:
            toma.save_to_db()
        except:
            return {'message': "Ha ocurrido un problema al almacenar los datos, vuelva a intentarlo"},500
        
        return toma.jsonOutput()