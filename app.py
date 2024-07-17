from datetime import datetime
from flask import Flask, jsonify, request
import os
import pyodbc
from flask_cors import CORS
from database import db
from router.global_dashboard import global_dashboard_bp
from router.line_dashboard import line_dashboard_bp
from services.production_line_service import ProductionLineService
from services.project_service import ProjectService
from services.segment_service import SegmentService

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)
CORS(app)

with app.app_context():
    db.create_all()


def get_db_connection():
    conn = pyodbc.connect(
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=./db.accdb;'
    )
    return conn


# Register the blueprint
app.register_blueprint(line_dashboard_bp)
# Register the global dashboard Lines
app.register_blueprint(global_dashboard_bp)

@app.get('/api/count-of-fx')
def getCountOfRef():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT SUM(Quantite) AS sum FROM T_operations_validees')
        rows = cursor.fetchall()
        conn.close()
        return jsonify({'count': rows[0].sum})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/count-of-boxs')
def get_number_of_boxs_by_line():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(N_etiquette) AS total_quantity FROM T_operations_validees')
        rows = cursor.fetchall()
        conn.close()
        return jsonify({'count': rows[0].total_quantity})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/count-of-box-by-ref')
def get_count_by_box():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT Code_fournisseur, COUNT(N_etiquette) AS box_count FROM T_operations_validees GROUP BY Code_fournisseur')
        rows = cursor.fetchall()
        data = [{'Code_fournisseur': row.Code_fournisseur, 'box_count': row.box_count} for row in rows]
        conn.close()
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/count-of-fx-by-ref', methods=['POST'])
def get_count_of_fx_by_ref():
    try:
        filters = request.json
        from_date = filters.get('from', datetime.utcnow().strftime('%d/%m/%Y'))
        to_date = filters.get('to', datetime.utcnow().strftime('%d/%m/%Y'))
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT Code_fournisseur, SUM(Quantite) AS fx_count
            FROM T_operations_validees
            WHERE FORMAT(Date_validation, 'dd/mm/yyyy') BETWEEN ? AND ?
            GROUP BY Code_fournisseur
        ''', [from_date, to_date])
        rows = cursor.fetchall()
        data = [{'Code_fournisseur': row.Code_fournisseur, 'box_count': row.fx_count} for row in rows]
        conn.close()
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# New route for line dashboard
@app.route('/api/line-dashboard')
def line_dashboard():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                line_id,
                SUM(Quantite) AS total_quantity,
                COUNT(N_etiquette) AS box_count,
                AVG(SOME_METRIC) AS average_metric
            FROM T_operations_validees
            GROUP BY line_id
        ''')
        rows = cursor.fetchall()
        data = [{'line_id': row.line_id, 'total_quantity': row.total_quantity, 'box_count': row.box_count,
                 'average_metric': row.average_metric} for row in rows]
        conn.close()
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Routes for production lines **********************
@app.route('/api/production-lines')
def get_all_production_line():
    return ProductionLineService.get_all()


# Routes for segments **********************
@app.route('/api/segments')
def get_all_segments():
    return SegmentService.get_all()


# Routes for projects **********************
@app.route('/api/projects')
def get_all_projects():
    return ProjectService.get_all()


# ***********   filter routes          ***************
@app.route('/api/data-with-filter', methods=['POST'])
def get_data_with_filter():
    try:
        filters = request.json
        project = filters.get('project')
        segment = filters.get('segment')
        line = filters.get('line')
        from_date = filters.get('from')
        to_date = filters.get('to')
        query = 'SELECT * FROM T_operations_validees WHERE 1=1'
        params = []

        if from_date and to_date:
            from_date_formatted = datetime.strptime(from_date, '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M')
            to_date_formatted = datetime.strptime(to_date, '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M')
            query += ' AND Date_validation > ? AND Date_validation < ?'
            params.extend([from_date, to_date])
        elif from_date:
            from_date_formatted = datetime.strptime(from_date, '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M')
            query += ' AND Date_validation > ?'
            params.append(from_date_formatted)
        elif to_date:
            to_date_formatted = datetime.strptime(to_date, '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M')
            query += ' AND Date_validation < ?'
            params.append(to_date_formatted)

        if project:
            query += ' AND project = ?'
            params.append(project)
        if segment:
            query += ' AND segment = ?'
            params.append(segment)
        if line:
            query += ' AND line = ?'
            params.append(line)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        data = [dict(zip([column[0] for column in cursor.description], row)) for row in results]
        cursor.close()
        conn.close()

        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/fx-per-hour-in-shift')
def test():
    current_day = datetime.utcnow().strftime('%d/%m/%Y')
    current_hour = int(datetime.utcnow().strftime('%H')) + 1

    if current_hour in range(6, 14):
        start_hour = '06:00'
        end_hour = '14:00'
    elif current_hour in range(14, 22):
        start_hour = '14:00'
        end_hour = '22:00'
    else:
        start_hour = '22:00'
        end_hour = '06:00'

    start_hour_int = int(start_hour.split(':')[0])
    end_hour_int = int(end_hour.split(':')[0])

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if start_hour_int < end_hour_int:
            cursor.execute('''
                SELECT SUM(Quantite) as count, FORMAT(Date_validation, 'hh') AS hour
                FROM T_operations_validees
                WHERE FORMAT(Date_validation, 'hh') BETWEEN ? AND ?
                AND FORMAT(Date_validation, 'dd/mm/yyyy') = ?
                GROUP BY FORMAT(Date_validation, 'hh')
            ''', (start_hour_int, end_hour_int, current_day))
        else:
            cursor.execute('''
                SELECT SUM(Quantite) as count, FORMAT(Date_validation, 'hh') AS hour
                FROM T_operations_validees
                WHERE (FORMAT(Date_validation, 'hh') >= ? OR FORMAT(Date_validation, 'hh') < ?)
                AND FORMAT(Date_validation, 'dd/mm/yyyy') = ?
                GROUP BY FORMAT(Date_validation, 'hh')
            ''', (start_hour_int, end_hour_int, current_day))

        rows = cursor.fetchall()
        data = [{'count': row.count, 'hour': row.hour} for row in rows]
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        conn.close()


@app.route('/env')
def get_env_variable():
    line_id = os.getenv('lineId', 'Environment variable lineId not set')
    return jsonify({"lineId": line_id})


if __name__ == '__main__':
    app.run(port=3000
            ,debug=True
            )
