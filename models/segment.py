from database import db
from models.base_model import BaseModel


class Segment(BaseModel, db.Model):
    __tablename__ = 'segments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    sum_of_hc_of_lines = db.Column(db.Integer, nullable=False)
    production_lines = db.relationship('ProductionLine', back_populates='segment', lazy=True)
    project = db.relationship('Project', back_populates='segments')

    def __init__(self, name, project_id, sum_of_hc_of_lines):
        super().__init__()
        self.name = name
        self.project_id = project_id
        self.sum_of_hc_of_lines = sum_of_hc_of_lines

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'project_id': self.project_id,
            'sum_of_hc_of_lines': self.sum_of_hc_of_lines,
            'project': self.project.to_dict() if self.project else None,
            # 'production_lines': [production_line.to_dict() for production_line in self.production_lines]
        }
