from flask_restful import Resource, reqparse
from model.session import Session
from model.dog import Dog

def getSessionParser():
    session_parser  = reqparse.RequestParser()

    session_parser.add_argument('name', 
    type=str, required=True, 
    help="El nombre se encuentra vacío")

    session_parser.add_argument('conclusion_ia', 
    type=str, required=False)

    session_parser.add_argument('conclusion_expert', 
    type=str, required=False)

    return session_parser

class SessionManage(Resource):

    def post(self):

        session_parser  = getSessionParser()

        session_parser.add_argument('dog_id', 
        type=int, required=True, 
        help="Hay que asignar un perro destino")

        data = session_parser.parse_args()

        if not Dog.getDogById(data['dog_id']):
            return {"message" : "Perro no existente"},404

        session = Session(**data)
        
        try:
            session.save_to_db()
        except:
            return {"message": "No se ha podido guardar la sesión"}, 500

        return session.jsonOutput()

    def put(self):

        session_parser  = getSessionParser()

        session_parser.add_argument('session_id', 
        type=int, required=True, 
        help="Hay que asignar una sesión destino")

        data = session_parser.parse_args()
        session = Session.getSessionById(data['session_id'])

        if not session:
            return {"message" : "Sesión no existente"}, 404

        del data['session_id']
        session.update(**data)

        try:
            session.save_to_db()
        except:
            return {"message": "No se ha podido guardar la sesión"}, 500

        return session.jsonOutput()

class SessionController(Resource):

    def get(self, id):

        session = Session.getSessionById(id)

        if not session:
            return {
                'message': 'No se ha encontrado ninguna sesión con este id: {}'.format(id)
                }, 404

        return session.jsonOutputComplete()

    def delete(self, id):

        session = Session.getSessionById(id)

        if not session:
            return {'message':"No existe ninguna sesión con este id"}, 404

        try:
            session.delete_from_db()
        except:
            return {'message' : 'No se ha podido eliminar la sesión'}, 500

        return { 'message':"Sesión eliminada correctamente" }

class SessionsDogs(Resource):

    def get(self, id):

        if not Dog.getDogById(id):
            return {'message': 'El perro no existe'}, 404

        sessions = Session.getAllSessionsByDog(id)

        return [session.jsonOutput() for session in sessions]

class SessionsDogsByName(Resource):

    def get(self, id, name, orderby, sortby):

        if not Dog.getDogById(id):
            return {'message': 'El perro no existe'}, 404

        sessions = Session.getSessionsByName(name, id, orderby, sortby)

        return [session.jsonOutput() for session in sessions]