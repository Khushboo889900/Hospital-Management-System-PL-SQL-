# Hospital Management System — Flask + MySQL

A student project with a graphical dashboard, patient directory, doctor directory, appointments, billing, medical records, and SQL reports.

## 1. Requirements
- Python 3.10 or newer
- MySQL Server running locally
- MySQL Workbench (for executing SQL)
- A web browser

## 2. Create the database
Open MySQL Workbench, connect to your MySQL server, open `schema.sql`, and execute it.
If you already created the six tables from the earlier instructions, you can skip the schema script; the table names and columns should match.

## 3. Configure the MySQL password
Open `app.py` and update `DB_CONFIG`:
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_MYSQL_PASSWORD",
    "database": "hospital_management",
}
```
Replace `YOUR_MYSQL_PASSWORD` with the password you use for your local MySQL account. Do not share this password.

## 4. Install Python packages
Open Command Prompt or the terminal in this project folder:
```bash
python -m venv .venv
```
Activate the environment:
- Windows Command Prompt: `.venv\\Scripts\\activate`
- Windows PowerShell: `.venv\\Scripts\\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

Then install packages:
```bash
python -m pip install -r requirements.txt
```

## 5. Run the website
```bash
python app.py
```
Open this address in your browser:
`http://127.0.0.1:5000`

Keep the terminal window open while using the website. Press `Ctrl+C` in the terminal to stop the server.

## 6. Pages
- `/` — dashboard metrics and recent records
- `/patients` — add, search, and delete patients
- `/doctors` — add doctors
- `/appointments` — create appointments and update their status
- `/billing` — create bills and mark them paid
- `/medical-records` — view medical records
- `/reports` — reports grouped by specialization and payment status

## Troubleshooting
- **Access denied:** check username/password in `app.py`.
- **Unknown database:** run `CREATE DATABASE hospital_management;`.
- **Table doesn't exist / unknown column:** ensure all six tables use the column names in `schema.sql`.
- **Cannot book appointments:** create at least one patient and one doctor first.
- **Port already in use:** change the last line to `app.run(debug=True, port=5001)` and open `http://127.0.0.1:5001`.

This is a learning/demo project. Use fictional sample data only; do not enter real patient medical information into an unsecured student app. For production use, add authentication, authorization, CSRF protection, secure secret management, audit logging, backups, and privacy controls.
