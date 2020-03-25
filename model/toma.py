from model.base import BaseModel, db

class Toma(BaseModel, db.Model):

    __tablename__ = "tomas"

    name = db.Column(db.String(255), nullable = False)
    _session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable = False)
    conclusion_ia = db.Column(db.String(255), nullable = True)
    conclusion_expert = db.Column(db.String(255), nullable = True)

    #TODO Archivos y videos

    def __init__(self, name, session_id, conclusion_ia = "", conclusion_expert = ""):
        self.name = name
        self._session_id = session_id
        self.conclusion_ia = conclusion_ia
        self.conclusion_expert = conclusion_expert

    def update(self, name, conclusion_ia, conclusion_expert):
        self.name = name
        self.conclusion_ia = conclusion_ia
        self.conclusion_expert = conclusion_expert

    def jsonOutput(self):
        return {
            'id':self.id,
            'name' : self.name,
            'session_id' : self._session_id,
            'conclusion_ia' : self.conclusion_ia,
            'conclusion_expert' : self.conclusion_expert
        }

    @classmethod
    def getTomaById(cls, id):
        return cls.query.filter_by(id = id).first()