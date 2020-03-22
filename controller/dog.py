from flask_restful import Resource, reqparse
from model.dog import Dog, DogObservation

class DogController(Resource):

    dog_parser  = reqparse.RequestParser()

    dog_parser.add_argument('name', 
    type=str, required=True, 
    help="El nombre se encuentra vacío")

    dog_parser.add_argument('bread', 
    type=str, required=True, 
    help="La raza se encuentra vacía")

    dog_parser.add_argument('birth', 
    type=str, required=True, 
    help="El nacimiento se encuentra vacío")

    dog_parser.add_argument('gender', 
    type=str, required=True, 
    help="El género se encuentra vacío")

    dog_parser.add_argument('weight', 
    type=float, required=True, 
    help="El peso se encuentra vacío")

    dog_parser.add_argument('height', 
    type=int, required=True, 
    help="La altura se encuentra vacía")

    def get(self, id):

        dog = Dog.getDogById(id)

        if dog:
            return dog.jsonOutput()

        return {'message' : 'Perro no encontrado'}, 404

    def post(self):

        data = DogController.dog_parser.parse_args()

        dog = Dog(**data)
        dog.save_to_db()

        return dog.jsonOutput(), 201


class DogListController(Resource):

    def get(self):
        data = Dog.getDogs()
        return [dog.jsonOutput() for dog in data]

class DogObservationController(Resource):

    dog_parser  = reqparse.RequestParser()

    dog_parser.add_argument('observation', 
    type=str, required=True, 
    help="La observación se encuentra vacía")

    dog_parser.add_argument('dog_id', 
    type=str, required=True, 
    help="Especifica un perro destino")

    def post(self):
        data = DogObservationController.dog_parser.parse_args()

        if Dog.getDogById(data['dog_id']) is None:
            return {'message' : 'Perro no encontrado'}, 404

        observation = DogObservation(**data)
        observation.save_to_db()

        return observation.jsonOutput(), 201