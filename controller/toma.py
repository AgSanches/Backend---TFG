from flask_restful import Resource, reqparse
from model.session import Session
from model.toma import Toma

class TomaController(Resource):

    def get(self, id):

        toma = Toma.getTomaById(id)

        if not toma:
            return {
                'message': 'No se ha encontrado ninguna toma con este id: {}'.format(id)
                }, 404

        return toma.jsonOutput()

    def post(self):

        toma_parser  = reqparse.RequestParser()

        toma_parser.add_argument('name', 
        type=str, required=True, 
        help="El nombre se encuentra vacío")

        toma_parser.add_argument('session_id', 
        type=int, required=True, 
        help="Hay que asignar una sesión destino")

        toma_parser.add_argument('conclusion_ia', 
        type=str, required=False)

        toma_parser.add_argument('conclusion_expert', 
        type=str, required=False)

        data = toma_parser.parse_args()

        if not Session.getSessionById(data['session_id']):
            return {"message" : "Sesión no existente"},404

        toma = Toma(**data)
        
        try:
            toma.save_to_db()
        except:
            return {"message": "No se ha podido guardar la toma"}, 500

        return toma.jsonOutput()
