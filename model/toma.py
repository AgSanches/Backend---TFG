from model.base import BaseModel, db
import os

class Toma(BaseModel, db.Model):

    __tablename__ = "tomas"

    name = db.Column(db.String(255), nullable = False)
    _session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable = False)
    conclusion_ia = db.Column(db.String(255), nullable = True)
    conclusion_expert = db.Column(db.String(255), nullable = True)

    video_front = db.Column(db.String(255), nullable = True)
    video_middle = db.Column(db.String(255), nullable = True)
    video_back = db.Column(db.String(255), nullable = True)

    sensor_data_front = db.Column(db.String(255), nullable = True)
    sensor_data_back = db.Column(db.String(255),  nullable = True)

    sensor_data_foot_upper = db.Column(db.String(255), nullable=True)
    sensor_data_foot_lower = db.Column(db.String(255), nullable=True)

    def __init__(self, name, session_id, conclusion_ia = "", conclusion_expert = ""):
        super(Toma, self).__init__()
        self.name = name
        self._session_id = session_id
        self.conclusion_ia = conclusion_ia
        self.conclusion_expert = conclusion_expert

    def update(self, name, conclusion_ia, conclusion_expert):
        self.name = name
        self.conclusion_ia = conclusion_ia
        self.conclusion_expert = conclusion_expert

    def getFileName(self, prefix):
        return "toma_" + prefix + "_" + str(self.id)

    def getFolder(self):
        return os.path.join(self.session.getFolder(),'Toma' + str(self.id))

    def jsonOutput(self):
        return {
            'id':self.id,
            'name' : self.name,
            'session_id' : self._session_id,
            'conclusion_ia' : self.conclusion_ia,
            'conclusion_expert' : self.conclusion_expert,
            'created_at': self.created_at.timestamp() * 1000,
            'updated_at': self.updated_at.timestamp() * 1000,
            'video_front' : self.video_front,
            'video_middle' : self.video_middle,
            'video_back' : self.video_back,
            'sensor_data_front' : self.sensor_data_front,
            'sensor_data_back' : self.sensor_data_back,
            'sensor_data_foot_upper' : self.sensor_data_foot_upper,
            'sensor_data_foot_lower' : self.sensor_data_foot_lower
        }

    @classmethod
    def getTomaById(cls, id):
        return cls.query.filter_by(id = id).first()

    @classmethod
    def getAllTomasByDog(cls, session_id):
        query = cls.query.filter_by(_session_id = session_id)
        return query.all()

    @classmethod
    def getTomaByName(cls, name, session_id):
        search = "%{}%".format(name)
        query = cls.query.filter_by(_session_id = session_id).filter(cls.name.like(search))
        return query.all()