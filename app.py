import pymysql
from flask import Flask, request, jsonify, send_from_directory
import os
from config import Config

app = Flask(__name__, static_folder='static')
app.config.from_object(Config)

def get_db():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def index():
    return send_from_directory('static', 'dashboard.html')

@app.route('/api/doctors', methods=['GET'])
def doctors():
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute('SELECT id, name, specialization FROM doctors ORDER BY name')
            rows = cur.fetchall()
        conn.close()
        return jsonify(doctors=rows)
    except Exception as e:
        return jsonify({'error': 'Server error'}), 500

@app.route('/api/doctors', methods=['POST'])
def add_doctor():
    data = request.get_json()
    name = (data.get('name') or '').strip()
    specialization = (data.get('specialization') or '').strip()
    if not name:
        return jsonify({'error': 'Doctor name required'}), 400
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute('INSERT INTO doctors (name, specialization) VALUES (%s, %s)', (name, specialization or 'General'))
            conn.commit()
            doc_id = cur.lastrowid
        conn.close()
        return jsonify({'success': True, 'id': doc_id})
    except Exception as e:
        return jsonify({'error': 'Server error'}), 500

@app.route('/api/slots/<int:doctor_id>')
def slots(doctor_id):
    date = request.args.get('date')
    if not date:
        return jsonify({'error': 'date required'}), 400
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                'SELECT time_slot FROM appointments WHERE doctor_id = %s AND appointment_date = %s AND status = %s',
                (doctor_id, date, 'confirmed')
            )
            booked = {r['time_slot'] for r in cur.fetchall()}
            cur.execute('SELECT time_slot FROM time_slots ORDER BY time_slot')
            all_slots = [r['time_slot'] for r in cur.fetchall()]
        conn.close()
        available = [s for s in all_slots if s not in booked]
        return jsonify(slots=available)
    except Exception as e:
        return jsonify({'error': 'Server error'}), 500

@app.route('/api/appointments', methods=['GET'])
def list_appointments():
    email = (request.args.get('email') or '').strip()
    if not email:
        return jsonify({'error': 'email required'}), 400
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute('''
                SELECT a.id, a.appointment_date, a.time_slot, a.status, a.patient_email,
                       d.name AS doctor_name, d.specialization
                FROM appointments a
                JOIN doctors d ON d.id = a.doctor_id
                WHERE a.patient_email = %s
                ORDER BY a.appointment_date DESC, a.time_slot
            ''', (email,))
            rows = cur.fetchall()
        conn.close()
        for r in rows:
            if r.get('appointment_date'):
                r['appointment_date'] = str(r['appointment_date'])
        return jsonify(appointments=rows)
    except Exception as e:
        return jsonify({'error': 'Server error'}), 500

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    date = (data.get('date') or '').strip()
    time_slot = (data.get('time_slot') or '').strip()
    patient_name = (data.get('patient_name') or '').strip()
    patient_email = (data.get('patient_email') or '').strip()
    if not doctor_id or not date or not time_slot or not patient_name or not patient_email:
        return jsonify({'error': 'doctor, date, time, name and email required'}), 400
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                'SELECT id FROM appointments WHERE doctor_id = %s AND appointment_date = %s AND time_slot = %s AND status = %s',
                (doctor_id, date, time_slot, 'confirmed')
            )
            if cur.fetchone():
                conn.close()
                return jsonify({'error': 'Slot already booked'}), 400
            cur.execute(
                'INSERT INTO appointments (patient_name, patient_email, doctor_id, appointment_date, time_slot, status) VALUES (%s, %s, %s, %s, %s, %s)',
                (patient_name, patient_email, doctor_id, date, time_slot, 'confirmed')
            )
            conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': 'Server error'}), 500

@app.route('/api/appointments/<int:aid>', methods=['DELETE'])
def cancel_appointment(aid):
    email = (request.args.get('email') or (request.get_json() or {}).get('email') or '').strip()
    if not email:
        return jsonify({'error': 'email required to cancel'}), 400
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute('UPDATE appointments SET status = %s WHERE id = %s AND patient_email = %s', ('cancelled', aid, email))
            conn.commit()
            if cur.rowcount == 0:
                conn.close()
                return jsonify({'error': 'Appointment not found or email does not match'}), 404
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
