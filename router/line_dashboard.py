from flask import Blueprint, request, jsonify
import pyodbc
from datetime import datetime

line_dashboard_bp = Blueprint('line_dashboard_bp', __name__)


# Function to get database connection
def get_db_connection():
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
                '((FORMAT(Date_validation, \'HH\') BETWEEN 22 AND 23) OR (FORMAT(Date_validation, \'HH\') BETWEEN 00 AND 06))')

    # Join shift conditions with OR if multiple shifts are included
    if shift_conditions:
        query += ' AND (' + ' OR '.join(shift_conditions) + ')'

    return query, params


# API endpoint to retrieve total quantity
@line_dashboard_bp.route('/api/line-dashboard/total-quantity', methods=['POST'])
def total_quantity():
    try:
        filters = request.json
        conn = get_db_connection()
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


# API endpoint to retrieve box count
@line_dashboard_bp.route('/api/line-dashboard/box-count', methods=['POST'])
def box_count():
    try:
        filters = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        query = 'SELECT COUNT(N_etiquette) AS box_count FROM T_operations_validees'
        params = []
        query, params = apply_filters(query, params, filters)
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()
        return jsonify({'box_count': row.box_count})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API endpoint to retrieve average quantity
@line_dashboard_bp.route('/api/line-dashboard/average-quantity', methods=['POST'])
def average_quantity():
    try:
        filters = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        query = 'SELECT AVG(Quantite) AS average_quantity FROM T_operations_validees'
        params = []
        query, params = apply_filters(query, params, filters)
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()
        return jsonify({'average_quantity': row.average_quantity})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API endpoint to retrieve count by code fournisseur
@line_dashboard_bp.route('/api/line-dashboard/count-by-code-fournisseur', methods=['POST'])
def count_by_code_fournisseur():
    try:
        filters = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        query = '''
            SELECT Code_fournisseur, COUNT(N_etiquette) AS box_count
            FROM T_operations_validees
        '''
        params = []
        query, params = apply_filters(query, params, filters)
        query += ' GROUP BY Code_fournisseur'
        cursor.execute(query, params)
        rows = cursor.fetchall()
        data = [{'Code_fournisseur': row.Code_fournisseur, 'box_count': row.box_count} for row in rows]
        conn.close()
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API endpoint to retrieve count by hour
@line_dashboard_bp.route('/api/line-dashboard/count-by-hour', methods=['POST'])
def count_by_hour():
    try:
        filters = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        query = '''
            SELECT FORMAT(Date_validation, 'HH') AS hour, COUNT(N_etiquette) AS box_count
            FROM T_operations_validees
        '''
        params = []
        query, params = apply_filters(query, params, filters)
        query += ' GROUP BY FORMAT(Date_validation, \'HH\')'
        cursor.execute(query, params)
        rows = cursor.fetchall()
        data = [{'hour': row.hour, 'box_count': row.box_count} for row in rows]
        conn.close()
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API endpoint to retrieve quantity by hour
@line_dashboard_bp.route('/api/line-dashboard/quantity-by-hour', methods=['POST'])
def quantity_by_hour_endpoint():
    try:
        filters = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        query = '''
            SELECT FORMAT(Date_validation, 'HH') AS hour, SUM(Quantite) AS total_quantity
            FROM T_operations_validees
        '''
        params = []
        query, params = apply_filters(query, params, filters)
        query += ' GROUP BY FORMAT(Date_validation, \'HH\') ORDER BY FORMAT(Date_validation, \'HH\') '
        cursor.execute(query, params)
        rows = cursor.fetchall()
        data = [{'hour': row.hour, 'total_quantity': row.total_quantity} for row in rows]
        conn.close()
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@line_dashboard_bp.route('/api/line-dashboard/hour-produits', methods=['POST'])
def hour_produits():
    try:
        filters = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        query = '''
            SELECT FORMAT(Date_validation, 'HH') AS hour, SUM(Quantite) AS total_quantity
            FROM T_operations_validees
        '''
        params = []
        query, params = apply_filters(query, params, filters)
        query += ' GROUP BY FORMAT(Date_validation, \'HH\') ORDER BY FORMAT(Date_validation, \'HH\')'
        cursor.execute(query, params)
        rows = cursor.fetchall()
        data = [{'hour': row.hour, 'total_quantity': row.total_quantity} for row in rows]
        conn.close()
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@line_dashboard_bp.route('/api/line-dashboard/productive-hours', methods=['POST'])
def productive_hours():
    try:
        filters = request.json
        temps_game = filters.get('temps_game', 0)
        start_time = filters.get('from')
        end_time = filters.get('to')
        vsm = filters.get('vsm')
        if not start_time or not end_time:
            return jsonify({'error': 'start and end times are required'}), 400

        start_time = datetime.strptime(start_time, '%Y/%m/%d %H:%M')
        end_time = datetime.strptime(end_time, '%Y/%m/%d %H:%M')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Calculate total time in hours
        total_time = ((end_time - start_time).total_seconds() / 3600)

        query = '''
            SELECT SUM(Quantite) as total_quantity 
            FROM T_operations_validees
        '''
        params = []
        query, params = apply_filters(query, params, filters)
        cursor.execute(query, params)
        rows = cursor.fetchall()

        total_quantity = rows[0].total_quantity or 0

        # Calculate productive hours
        productive_hours = (total_quantity * temps_game) / vsm if temps_game else 0
        efficiency = (total_quantity * temps_game) / (vsm * total_time) * 100
        expected = (vsm * total_time) / temps_game
        conn.close()

        return jsonify({'posted_hours': total_time,
                        'productive_hours': productive_hours,
                        'total_quantity': total_quantity,
                        'efficiency': efficiency,
                        'expected': expected
                        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@line_dashboard_bp.route('/api/line-dashboard/sum-by-code-fournisseur', methods=['POST'])
def sum_by_code_fournisseur():
    try:
        filters = request.json
        conn = get_db_connection()
        cursor = conn.cursor()

        query = '''
            SELECT Code_fournisseur, SUM(Quantite) AS total_quantity
            FROM T_operations_validees
        '''
        params = []
        query, params = apply_filters(query, params, filters)
        query += ' GROUP BY Code_fournisseur'
        cursor.execute(query, params)
        rows = cursor.fetchall()

        data = [{'Code_fournisseur': row.Code_fournisseur, 'total_quantity': row.total_quantity} for row in rows]

        conn.close()

        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@line_dashboard_bp.route('/api/line-dashboard/total-quantity-current', methods=['POST'])
def total_quantity_current():
    try:
        filters = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        query = 'SELECT SUM(Quantite_en_cours) AS total_quantity FROM T_operations_en_cours'
        # params = []
        # query, params = apply_filters(query, params, filters)
        cursor.execute(query)
        row = cursor.fetchone()
        conn.close()
        print(len(row))
        return jsonify({'total_quantity': row.total_quantity})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
