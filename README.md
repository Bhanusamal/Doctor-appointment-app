# Doctor Appointment Booking – Prototype

Minimal doctor appointment booking webapp: HTML/CSS/JS frontend, Flask backend, MySQL (PyMySQL).

## Features

- **Login / Register** – Session-based auth, hashed passwords (Werkzeug)
- **Book appointment** – Choose doctor, date, and time slot
- **My appointments** – List and cancel appointments
- **Security** – `SECRET_KEY` for sessions; set `SECRET_KEY` in production

## Setup

1. **Python 3** and **MySQL** installed and running.

2. **Create virtualenv and install dependencies:**
   ```bash
   cd doctor-booking-app
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure MySQL** (optional; defaults: user `root`, no password, DB `doctor_booking`):
   - Create database `doctor_booking` if you prefer to create it yourself.
   - Or set env: `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`.

4. **Initialize database and seed data:**
   ```bash
   set MYSQL_PASSWORD=your_password
   python init_db.py
   ```

5. **Run the app:**
   ```bash
   set MYSQL_PASSWORD=your_password
   python app.py
   ```
   Open http://127.0.0.1:5000 — register a user, then book appointments.

## Project layout

- `app.py` – Flask app, auth, API routes
- `config.py` – Config (DB, SECRET_KEY)
- `init_db.py` – Creates DB/tables and sample doctors & time slots
- `static/` – `login.html`, `dashboard.html`, `styles.css`, `app.js`
