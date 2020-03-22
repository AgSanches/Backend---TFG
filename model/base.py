from db import db
from datetime import datetime

class BaseModel():

    id = db.Column(db.Integer, primary_key = True )
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __init__(self):
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()