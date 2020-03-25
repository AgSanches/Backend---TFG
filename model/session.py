from model.base import BaseModel, db

class Session(BaseModel, db.Model):

    __tablename__ = 'sessions'

    name = db.Column(db.String(255), nullable = False)
    conclusion_ia = db.Column(db.String(255), nullable = True)
    conclusion_expert = db.Column(db.String(255), nullable = True)
    _dog_id = db.Column(db.Integer, db.ForeignKey('dogs.id'), nullable = False)
    tomas = db.relationship('Toma', lazy = 'dynamic', cascade = "all, delete-orphan")

    def __init__(self, name, dog_id, conclusion_ia = "", conclusion_expert = ""):
        self.name = name
        self._dog_id = dog_id
        self.conclusion_ia = conclusion_ia
        self.conclusion_expert = conclusion_expert

    def update(self, name, conclusion_ia, conclusion_expert ):
        self.name = name
        self.conclusion_ia = conclusion_ia
        self.conclusion_expert = conclusion_expert

    def jsonOutput(self):
        return {
            'id':self.id,
            'name' : self.name,
            'dog_id' : self._dog_id,
            'conclusion_ia' : self.conclusion_ia,
            'conclusion_expert' : self.conclusion_expert,
            'tomas': [ toma.jsonOutput() for toma in self.tomas.all() ]
        }

    @classmethod
    def getSessionById(cls, id):
        return cls.query.filter_by(id = id).first()

    @classmethod
    def getSessionByName(cls, name):
        return cls.query.filter_by(name = name).first()

        