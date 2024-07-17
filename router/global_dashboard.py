from datetime import datetime
import requests
import pyodbc
from flask import Blueprint, request, jsonify

from models.project import Project
from services.production_line_service import ProductionLineService
from services.segment_service import SegmentService
from services.project_service import ProjectService

global_dashboard_bp = Blueprint('global_dashboard_bp', __name__)


def get_db_connection(DBQ):
    conn = pyodbc.connect(
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=./db.accdb;'
    )
    return conn


# Function to apply filters to queries
def apply_filters(query, params, filters):
    from_date = filters.get('from')
    to_date = filters.get('to')
    shift = filters.get('shift')

    # Default from_date and to_date to current date if empty or not provided
    if not from_date or from_date == "":
        from_date = datetime.now().strftime('%Y-%m-%d %H:%M')
    if not to_date or to_date == "":
        to_date = datetime.now().strftime('%Y-%m-%d %H:%M')

    query += ' WHERE Date_validation BETWEEN ? AND ?'
    params.extend([from_date, to_date])

    # Determine shifts to include based on provided or default shift
    shifts_to_include = []
    if shift and shift != "":
        shifts_to_include.append(shift)
    else:
        shifts_to_include = ['a', 'b', 'c']  # Include all shifts

    # Build shift conditions for the query
    shift_conditions = []
    for shift in shifts_to_include:
        if shift == 'a':
            shift_conditions.append('(FORMAT(Date_validation, \'HH\') BETWEEN 06 AND 14)')
        elif shift == 'b':
            shift_conditions.append('(FORMAT(Date_validation, \'HH\') BETWEEN 14 AND 22)')
        elif shift == 'c':
            shift_conditions.append(
                '((FORMAT(Date_validation, \'HH\') BETWEEN 22 AND 23) OR (FORMAT(Date_validation, \'HH\') BETWEEN 00 '
                'AND 06))')

    # Join shift conditions with OR if multiple shifts are included
    if shift_conditions:
        query += ' AND (' + ' OR '.join(shift_conditions) + ')'

    return query, params


@global_dashboard_bp.route('/api/global-dashboard/total-quantity', methods=['POST'])
def get_total_fx():
    try:
        filters = request.json
        project = filters.get('project')
        segment = filters.get('segment')
        line = filters.get('line')

        if line and segment:
            selected_line = ProductionLineService.get_by_id(int(line))
            try:
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.post(
                    selected_line.server_url + '/api/line-dashboard/total-quantity',
                    json=filters,
                    headers=headers
                )
                data_from_server = response.json()
                data_from_server['line'] = selected_line.to_dict()
                return jsonify(data_from_server)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        elif not line and segment and project:
            try:
                selected_segment = SegmentService.get_segment_by_id(segment)
                data = []
                headers = {
                    'Content-Type': 'application/json'
                }
                for line in selected_segment.production_lines:
                    response = requests.post(
                        line.server_url + '/api/line-dashboard/total-quantity',
                        json=filters,
                        headers=headers
                    )
                    data_from_server = response.json()
                    data_from_server['line'] = line.to_dict()
                    data.append(data_from_server)

                return jsonify(data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        elif not segment and not line and project:
            try:
                headers = {
                    'Content-Type': 'application/json'
                }
                data = []

                selected_project = Project.query.get(project)

                for segment in selected_project.segments:
                    selected_segment = segment
                    for line in selected_segment.production_lines:
                        response = requests.post(
                            line.server_url + '/api/line-dashboard/total-quantity',
                            json=filters,
                            headers=headers
                        )
                        data_from_server = response.json()
                        data_from_server['line'] = line.to_dict()
                        data.append(data_from_server)

                return jsonify(data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
