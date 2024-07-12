from flask import jsonify

from models.project import Project


class ProjectService:

    @staticmethod
    def get_all():
        project = Project
        projects = project.query.all()
        return jsonify([project.to_dict() for project in projects]), 200
