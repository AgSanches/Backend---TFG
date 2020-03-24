import os
from werkzeug.utils import secure_filename

ALLOWED_PHOTOS = {'png', 'jpg', 'jpeg'}
ALLOWED_VIDEOS = {'mp4', 'mp3'}
ALLOWED_SENSORS = {}
UPLOAD_FOLDER = './uploads/'

def allowed_photo(filename):
    return '.' in filename and filename.split('.')[1].lower() in ALLOWED_PHOTOS

def allowed_video(filename):
    return '.' in filename and filename.split('.')[1].lower() in ALLOWED_VIDEOS

def allowed_sensors(filename):
    return '.' in filename and filename.split('.')[1].lower() in ALLOWED_SENSORS

def save_file(folder, name ,file):
    if not os.path.exists(os.path.join(UPLOAD_FOLDER, folder)):
        os.mkdir(os.path.join(UPLOAD_FOLDER, folder))
    try :
        file.save(os.path.join(UPLOAD_FOLDER, folder, name))
    except:
        return False, ''
    return True, name

def delete_file(folder,target):

    if os.path.exists(os.path.join(UPLOAD_FOLDER, folder, target)):
        try:
            os.remove(os.path.join(UPLOAD_FOLDER, folder, target))
        except:
            return False

    return True