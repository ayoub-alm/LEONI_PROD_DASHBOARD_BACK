from datetime import datetime

import pyodbc
from flask import Blueprint, request, jsonify

from models.production_line import ProductionLine
from services.production_line_service import ProductionLineService

global_dashboard_bp = Blueprint('global_dashboard_bp', __name__)


def get_db_connection(DBQ):
    conn = pyodbc.connect(
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=' + DBQ + ';'
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

        if line != "" and segment != "":
            selected_line = ProductionLineService.get_by_id(int(line))
            # connect to path of database for the selected line
            try:
                filters = request.json
                conn = get_db_connection(selected_line.database_path)
                cursor = conn.cursor()
                query = 'SELECT SUM(Quantite) AS total_quantity FROM T_operations_validees'
                params = []
                query, params = apply_filters(query, params, filters)
                cursor.execute(query, params)
                row = cursor.fetchone()
                conn.close()
                return jsonify({'total_quantity': row.total_quantity})

            except Exception as e:
                return jsonify({'error': str(e)}), 500
            return jsonify({"message": "Connected to line's database", "data": selected_line}), 200
        elif line == "" and segment != "" and project != "":
            # get all lines of segment data and perform query
            return jsonify({"message": "Line is empty, segment is provided"}), 200
        elif segment == "" and project != "":
            # get data of all lines by project
            return jsonify({"message": "Line is empty, segment is empty, project is provided "}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
