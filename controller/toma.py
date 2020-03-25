from flask_restful import Resource, reqparse
from model.session import Session
from model.toma import Toma

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