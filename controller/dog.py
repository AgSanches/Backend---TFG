from flask_restful import Resource, reqparse
from flask import send_file
from model.dog import Dog, DogObservation
import werkzeug
from files import allowed_photo, save_file, delete_file, returnDefaultPhoto, checkFileExists, getFile


def getParserDog():
    dog_parser = reqparse.RequestParser()

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

    return dog_parser


def getParserObservation():
    observation_parser = reqparse.RequestParser()

    observation_parser.add_argument('observation',
                                    type=str, required=True,
                                    help="La observación se encuentra vacía")

    return observation_parser


class DogController(Resource):

    def get(self, id):

        dog = Dog.getDogById(id)

        if dog:
            return dog.jsonOutput()

        return {'message': 'Perro no encontrado'}, 404

    def delete(self, id):

        dog = Dog.getDogById(id)

        if not dog:
            return {'message': 'El perro con id {} no existe'.format(id)}, 404
        try:
            dog.delete_from_db()
        except:
            return {'message': 'No se ha podido eliminar el perro'}, 500

        return {'message': 'Perro correctamente eliminado'}

class DogName(Resource):

    def get(self, name):

        dogs = Dog.getDogsByName(name)
        print(dogs)

        return {}


class DogManage(Resource):

    def post(self):

        data = getParserDog().parse_args()

        dog = Dog(**data)
        dog.save_to_db()

        return dog.jsonOutput(), 201

    def put(self):

        dog_parser = getParserDog()

        dog_parser.add_argument('dog_id',
                                type=str, required=True,
                                help="Elige un perro que editar")

        data = dog_parser.parse_args()

        dog = Dog.getDogById(data['dog_id'])

        if not dog:
            return {'message': 'Perro no existente'}, 404

        del data['dog_id']
        dog.update(**data)

        try:
            dog.save_to_db()
        except:
            return {
                       'message': "Ha ocurrido un problema al actualizar el perro, vuelva a intentarlo en otro momento"}, 500

        return dog.jsonOutput()


class DogListController(Resource):

    def get(self):
        data = Dog.getDogs()
        return [dog.jsonOutput() for dog in data]


class DogObservationController(Resource):

    def post(self):

        observation_parser = getParserObservation()

        observation_parser.add_argument('dog_id',
                                        type=str, required=True,
                                        help="Especifica un perro destino")

        data = observation_parser.parse_args()

        if Dog.getDogById(data['dog_id']) is None:
            return {'message': 'Perro no encontrado'}, 404

        observation = DogObservation(**data)
        observation.save_to_db()

        return observation.jsonOutput(), 201

    def put(self):
        observation_parser = getParserObservation()
        observation_parser.add_argument('observation_id',
                                        type=str, required=True, help="Especifica una observación destino")

        data = observation_parser.parse_args()
        observation = DogObservation.getObservationById(data['observation_id'])

        if not observation:
            return {'message': "Observación no encontrada"}, 404

        observation.observation = data['observation']

        try:
            observation.save_to_db()
        except:
            return {'message': "No se ha podido actualizar"}, 500

        return observation.jsonOutput()


class DogImage(Resource):

    def get(self, id):

        dog = Dog.getDogById(id)

        if dog is None:
            return {'message': 'Perro no encontrado'}, 404

        if dog.photo_path == '' or not checkFileExists(dog.folderOutput(), dog.photo_path):
            return send_file(returnDefaultPhoto())

        return send_file(getFile(dog.folderOutput(), dog.photo_path))

    def post(self, id):

        file_parser = reqparse.RequestParser()

        file_parser.add_argument(
            'file', type=werkzeug.datastructures.FileStorage, required=True, location="files",
            help="Añade una imagen")

        data = file_parser.parse_args()

        dog = Dog.getDogById(id)

        if dog is None:
            return {'message': 'Perro no encontrado'}, 404

        if not allowed_photo(data['file'].filename):
            return {'message': "Archivo erróneo, solo se pueden subir imágenes"}, 400

        status = save_file(
            dog.folderOutput(),  # Folder Target
            dog.photoOutput() + '.' + data['file'].filename.split('.')[1],  # Image name
            data['file'])

        if not status[0]:
            return {'message': "No se ha podido subir la imagen, vuelva a intentarlo en otro momento"}, 500

        dog.photo_path = status[1]
        dog.save_to_db()
        return dog.jsonOutput()

    def delete(self, id):

        dog = Dog.getDogById(id)

        if not dog:
            return {'message': "Perro no encontrado"}, 404

        if dog.photo_path == '':
            return {'message': "Este perro no cuenta con ninguna imagen"}, 404

        status = delete_file(dog.folderOutput(), dog.photo_path)

        if status:
            dog.photo_path = ''
            try:
                dog.save_to_db()
                return {'message': 'Imagen eliminada'}
            except:
                return {"message": 'Ha ocurrido un problema al eliminar la imagen'}, 500

        return {"message": 'Ha ocurrido un problema al eliminar la imagen'}, 500