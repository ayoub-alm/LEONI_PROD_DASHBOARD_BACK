from flask import jsonify

from models.production_line import ProductionLine


class ProductionLineService:
    @staticmethod
    def get_all():
        production_line = ProductionLine
        production_lines = production_line.query.all()
        return jsonify([production_line.to_dict() for production_line in production_lines])

    @staticmethod
    def get_by_id(id):
        production_line = ProductionLine
        production_line = production_line.query.get(id)
        return production_line