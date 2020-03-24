from flask_restful import Resource, reqparse
from model.dog import Dog, DogObservation
import werkzeug
from files import allowed_photo, save_file

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

class DogUploadImage(Resource):

    dog_parser = reqparse.RequestParser()

    dog_parser.add_argument(
        'dog_id', type= str, required = True, 
        help="Especifica un perro destino")

    dog_parser.add_argument(
        'file', type = werkzeug.datastructures.FileStorage, required = True, location = "files", 
        help="Añade una imagen")

    def post(self):

        data = DogUploadImage.dog_parser.parse_args()
        dog = Dog.getDogById(data['dog_id'])

        if dog is None:
            return {'message' : 'Perro no encontrado'}, 404
        
        if not allowed_photo(data['file'].filename):
            return { 'message' : "Archivo erróneo, solo se pueden subir imágenes"}, 400 

        status = save_file( 
            dog.folderOutput(), #Folder Target
            dog.photoOutput() + '.' + data['file'].filename.split('.')[1],  #Image name
            data['file'])

        if not status[0]:
            return {'message' : "No se ha podido subir la imagen, vuelva a intentarlo en otro momento"}, 500

        dog.photo_path = status[1]
        dog.save_to_db()
        return dog.jsonOutput()