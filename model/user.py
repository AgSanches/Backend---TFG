from model.base import BaseModel, db

class User(BaseModel, db.Model):

    __tablename__ = 'users'

    name = db.Column(db.String(255), nullable = False)
    surname = db.Column(db.String(255), nullable = False)
    email = db.Column(db.String(255), unique = True)
    password = db.Column(db.String(255), nullable = False)

    def __init__(self, name, surname, email, password):
        BaseModel.__init__(self)
        self.update(name, surname, email, password)

    def update(self, name, surname, email, password):
        self.name = name
        self.surname = surname
        self.email = email
        self.password = password

    def jsonOutput(self):
        return {
            'id': self.id,
            'name' : self.name,
            'surname' : self.surname,
            'email' : self.email,
            'created_at': self.created_at.timestamp() * 1000,
        }

    @classmethod
    def findUserByEmail(cls, email):
        return cls.query.filter_by( email = email ).first()

    @classmethod
    def findUserById(cls, id):
        return cls.query.filter_by( id = id).first()

    @classmethod
    def getUsers(cls):
        return cls.query.all()