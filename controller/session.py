from flask_restful import Resource, reqparse
from model.session import Session
from model.dog import Dog
from flask_jwt_extended import jwt_required

def getSessionParser():
    session_parser  = reqparse.RequestParser()

    session_parser.add_argument('name', 
    type=str, required=True, 
    help="El nombre se encuentra vacío")


    return session_parser

def getSessionObservationParser():
    session_parser  = reqparse.RequestParser()

    session_parser.add_argument('name',
    type=str, required=False,
    help="El nombre se encuentra vacío")

    session_parser.add_argument('conclusion_expert',
    type=str, required=False)

    return session_parser

class SessionManage(Resource):

    @jwt_required
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

class SessionController(Resource):

    @jwt_required
    def get(self, id):

        session = Session.getSessionById(id)

        if not session:
            return {
                'message': 'No se ha encontrado ninguna sesión con este id: {}'.format(id)
                }, 404

        return session.jsonOutputComplete()

    @jwt_required
    def put(self, id):

        session_parser  = getSessionObservationParser()

        data = session_parser.parse_args()
        session = Session.getSessionById(id)

        if not session:
            return {"message" : "Sesión no existente"}, 404

        session.update(**data)

        try:
            session.save_to_db()
        except:
            return {"message": "No se ha podido guardar la sesión"}, 500

        return session.jsonOutput()

    @jwt_required
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

    @jwt_required
    def get(self, id):

        if not Dog.getDogById(id):
            return {'message': 'El perro no existe'}, 404

        sessions = Session.getAllSessionsByDog(id)

        return [session.jsonOutput() for session in sessions]

class SessionsDogsByName(Resource):

    @jwt_required
    def get(self, id, name):

        if not Dog.getDogById(id):
            return {'message': 'El perro no existe'}, 404

        sessions = Session.getSessionsByName(name, id)

        return [session.jsonOutput() for session in sessions]