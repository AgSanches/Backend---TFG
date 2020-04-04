from model.base import BaseModel, db
import os

class Session(BaseModel, db.Model):

    __tablename__ = 'sessions'

    name = db.Column(db.String(255), nullable = False)
    conclusion_ia = db.Column(db.String(255), nullable = True)
    conclusion_expert = db.Column(db.String(255), nullable = True)
    _dog_id = db.Column(db.Integer, db.ForeignKey('dogs.id'), nullable = False)
    tomas = db.relationship('Toma', backref="session", lazy = 'dynamic', cascade = "all, delete-orphan")

    def __init__(self, name, dog_id, conclusion_ia = "", conclusion_expert = ""):
        super(Session, self).__init__()
        self.name = name
        self._dog_id = dog_id
        self.conclusion_ia = conclusion_ia
        self.conclusion_expert = conclusion_expert

    def update(self, name, conclusion_ia, conclusion_expert ):
        self.name = name
        self.conclusion_ia = conclusion_ia
        self.conclusion_expert = conclusion_expert

    def getFolder(self):
        return os.path.join(self.dog.folderOutput(), "Sesion" + str(self.id))

    def jsonOutput(self):
        return {
            'id':self.id,
            'name' : self.name,
            'dog_id' : self._dog_id,
            'conclusion_ia' : self.conclusion_ia,
            'conclusion_expert' : self.conclusion_expert,
            'created_at': self.created_at.timestamp() * 1000,
            'updated_at': self.updated_at.timestamp() * 1000
        }

    def jsonOutputComplete(self):
        return {
            'id':self.id,
            'name' : self.name,
            'dog_id' : self._dog_id,
            'conclusion_ia' : self.conclusion_ia,
            'conclusion_expert' : self.conclusion_expert,
            'created_at': self.created_at.timestamp() * 1000,
            'updated_at': self.updated_at.timestamp() * 1000,
            'tomas': [ toma.jsonOutput() for toma in self.tomas.all() ]
        }

    @classmethod
    def addParamsQuery(cls, query, orderby, sortby):

        if orderby == 'updated_at':
            if sortby == 'asc':
                query = query.order_by(db.asc(cls.updated_at))
            else:
                query = query.order_by(db.desc(cls.updated_at))
        else:
            if sortby == 'asc':
                query = query.order_by(db.asc(cls.name))
            else:
                query = query.order_by(db.desc(cls.name))

        return query

    @classmethod
    def getSessionById(cls, id):
        return cls.query.filter_by(id = id).first()

    @classmethod
    def getAllSessionsByDog(cls, dog_id, orderby = 'updated_at', sortby = "desc"):
        query = cls.query.filter_by(_dog_id = dog_id)
        return cls.addParamsQuery(query, orderby, sortby).all()

    @classmethod
    def getSessionsByName(cls, name, dog_id, orderby = 'updated_at', sortby='desc'):
        search = "%{}%".format(name)
        query = cls.query.filter_by(_dog_id = dog_id).filter(cls.name.like(search))
        return cls.addParamsQuery(query, orderby, sortby).all()