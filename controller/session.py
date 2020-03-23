from flask_restful import Resource, reqparse
from model.session import Session
from model.dog import Dog


class SessionController(Resource):

    def get(self, id):

        session = Session.getSessionById(id)

        if not session:
            return {
                'message': 'No se ha encontrado ninguna sesión con este id: {}'.format(id)
                }, 404

        return session.jsonOutput()

    def post(self):

        session_parser  = reqparse.RequestParser()

        session_parser.add_argument('name', 
        type=str, required=True, 
        help="El nombre se encuentra vacío")

        session_parser.add_argument('dog_id', 
        type=int, required=True, 
        help="Hay que asignar un perro destino")

        session_parser.add_argument('conclusion_ia', 
        type=str, required=False)

        session_parser.add_argument('conclusion_expert', 
        type=str, required=False)

        data = session_parser.parse_args()

        if not Dog.getDogById(data['dog_id']):
            return {"message" : "Perro no existente"},404

        session = Session(**data)
        
        try:
            session.save_to_db()
        except:
            return {"message": "No se ha podido guardar la sesión"}, 500

        return session.jsonOutput()

