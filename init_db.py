"""
Create database and tables. Run once after MySQL is running.
Set MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST as needed.
"""
import pymysql
import os

host = os.environ.get('', 'localhost')
user = os.environ.get('', 'root')
password = os.environ.get('', '')
db_name = os.environ.get('', 'doctor_booking')

conn = pymysql.connect(host=host, user=user, password=password)
with conn.cursor() as cur:
    cur.execute(f'CREATE DATABASE IF NOT EXISTS `{db_name}`')
    cur.execute(f'USE `{db_name}`')
conn.close()

conn = pymysql.connect(host=host, user=user, password=password, database=db_name)
with conn.cursor() as cur:
    cur.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            specialization VARCHAR(255) NOT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS time_slots (
            id INT AUTO_INCREMENT PRIMARY KEY,
            time_slot VARCHAR(20) NOT NULL UNIQUE
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_name VARCHAR(255) NOT NULL,
            patient_email VARCHAR(255) NOT NULL,
            doctor_id INT NOT NULL,
            appointment_date DATE NOT NULL,
            time_slot VARCHAR(20) NOT NULL,
            status VARCHAR(50) NOT NULL DEFAULT 'confirmed',
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        )
    ''')
    cur.execute('SELECT COUNT(*) AS c FROM doctors')
    if cur.fetchone()[0] == 0:
        cur.execute('''
            INSERT INTO doctors (name, specialization) VALUES
            ('Dr. Smith', 'General Physician'),
            ('Dr. Jones', 'Cardiology'),
            ('Dr. Lee', 'Dermatology')
        ''')
    cur.execute('SELECT COUNT(*) AS c FROM time_slots')
    if cur.fetchone()[0] == 0:
        slots = [f'{h:02d}:00' for h in range(9, 17)]
        for s in slots:
            cur.execute('INSERT INTO time_slots (time_slot) VALUES (%s)', (s,))
    conn.commit()
conn.close()
print('Database and tables created. Sample doctors and time slots added.')
