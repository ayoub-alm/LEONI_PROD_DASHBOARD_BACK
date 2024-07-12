import datetime

from database import db


class BaseModel(db.Model):
    __abstract__ = True
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def __init__(self):
        self.created_at = datetime.datetime.utcnow()
        self.deleted_at = datetime.datetime.utcnow()
        self.updated_at = datetime.datetime.utcnow()
