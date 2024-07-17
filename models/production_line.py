from database import db
from models.base_model import BaseModel

class ProductionLine(BaseModel, db.Model):
    __tablename__ = 'production_lines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    number_of_operators = db.Column(db.Integer, default=0)
    segment_id = db.Column(db.Integer, db.ForeignKey('segments.id'))
    database_path = db.Column(db.String(200), nullable=False)
    server_url = db.Column(db.String(200), nullable=True)
    segment = db.relationship('Segment', back_populates='production_lines')

    def __init__(self, id, name, number_of_operators, segment_id):
        super().__init__()
        self.id = id,
        self.name = name
        self.number_of_operators = number_of_operators
        self.segment_id = segment_id

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'database_path': self.database_path,
            'segment': self.segment.to_dict() if self.segment else None,
            'number_of_operators': self.number_of_operators,
        }
