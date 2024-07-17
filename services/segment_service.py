from flask import jsonify

from models.project import Project
from models.segment import Segment


class SegmentService:

    @staticmethod
    def get_all():
        segment = Segment
        segments = segment.query.all()
        return jsonify([sgm.to_dict() for sgm in segments])

    @staticmethod
    def get_segment_by_id(id):
        segment = Segment.query.get(id)
        return segment
