from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
from decimal import Decimal

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

# Update these values to match your MySQL setup.
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "@Khushu1",
    "database": "hospital_management",
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def fetch_all(query, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def execute(query, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()

@app.route("/")
def dashboard():
    try:
        stats = {
            "patients": fetch_all("SELECT COUNT(*) AS n FROM Patients")[0]["n"],
            "doctors": fetch_all("SELECT COUNT(*) AS n FROM Doctors")[0]["n"],
            "appointments": fetch_all(
                "SELECT COUNT(*) AS n FROM Appointments WHERE appointment_date = CURDATE()"
            )[0]["n"],
            "revenue": fetch_all(
                "SELECT COALESCE(SUM(total_amount),0) AS n FROM Bills WHERE payment_status = 'Paid'"
            )[0]["n"],
        }
        recent_patients = fetch_all(
            "SELECT patient_id, patient_name, age, gender, phone FROM Patients ORDER BY patient_id DESC LIMIT 6"
        )
        upcoming = fetch_all("""
            SELECT a.appointment_id, p.patient_name, d.doctor_name,
                   a.appointment_date, a.appointment_time, a.status
            FROM Appointments a
            JOIN Patients p ON p.patient_id = a.patient_id
            JOIN Doctors d ON d.doctor_id = a.doctor_id
            WHERE a.appointment_date >= CURDATE()
            ORDER BY a.appointment_date, a.appointment_time LIMIT 5
        """)
        unpaid = fetch_all("""
            SELECT b.bill_id, p.patient_name, b.total_amount, b.bill_date
            FROM Bills b JOIN Patients p ON p.patient_id = b.patient_id
            WHERE b.payment_status = 'Unpaid'
            ORDER BY b.bill_date DESC LIMIT 5
        """)
        return render_template("dashboard.html", stats=stats, patients=recent_patients,
                               upcoming=upcoming, unpaid=unpaid, db_error=None)
    except Error as e:
        return render_template("dashboard.html", stats=None, patients=[], upcoming=[],
                               unpaid=[], db_error=str(e))

@app.route("/patients", methods=["GET", "POST"])
def patients():
    if request.method == "POST":
        try:
            execute("""INSERT INTO Patients (patient_name, gender, age, phone, address)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (request.form["patient_name"].strip(), request.form.get("gender") or None,
                     request.form.get("age") or None, request.form.get("phone") or None,
                     request.form.get("address") or None))
            flash("Patient added successfully.", "success")
        except (Error, ValueError) as e:
            flash(f"Could not add patient: {e}", "error")
        return redirect(url_for("patients"))
    search = request.args.get("q", "").strip()
    try:
        if search:
            rows = fetch_all("""SELECT * FROM Patients
                WHERE patient_name LIKE %s OR phone LIKE %s ORDER BY patient_id DESC""",
                (f"%{search}%", f"%{search}%"))
        else:
            rows = fetch_all("SELECT * FROM Patients ORDER BY patient_id DESC")
        db_error = None
    except Error as e:
        rows, db_error = [], str(e)
    return render_template("patients.html", patients=rows, q=search, db_error=db_error)

@app.route("/patients/delete/<int:patient_id>", methods=["POST"])
def delete_patient(patient_id):
    try:
        execute("DELETE FROM Patients WHERE patient_id = %s", (patient_id,))
        flash("Patient deleted.", "success")
    except Error as e:
        flash(f"Could not delete patient. This patient may have linked appointments, records, or bills. Details: {e}", "error")
    return redirect(url_for("patients"))

@app.route("/doctors", methods=["GET", "POST"])
def doctors():
    if request.method == "POST":
        try:
            execute("""INSERT INTO Doctors (doctor_name, specialization, phone, consultation_fee)
                       VALUES (%s, %s, %s, %s)""",
                    (request.form["doctor_name"].strip(), request.form.get("specialization") or None,
                     request.form.get("phone") or None, request.form.get("consultation_fee") or 0))
            flash("Doctor added successfully.", "success")
        except Error as e:
            flash(f"Could not add doctor: {e}", "error")
        return redirect(url_for("doctors"))
    try:
        rows = fetch_all("SELECT * FROM Doctors ORDER BY doctor_id DESC")
        db_error = None
    except Error as e:
        rows, db_error = [], str(e)
    return render_template("doctors.html", doctors=rows, db_error=db_error)

@app.route("/appointments", methods=["GET", "POST"])
def appointments():
    if request.method == "POST":
        try:
            execute("""INSERT INTO Appointments
                (patient_id, doctor_id, appointment_date, appointment_time, status)
                VALUES (%s, %s, %s, %s, %s)""",
                (request.form["patient_id"], request.form["doctor_id"],
                 request.form["appointment_date"], request.form.get("appointment_time") or None,
                 request.form.get("status") or "Scheduled"))
            flash("Appointment created successfully.", "success")
        except Error as e:
            flash(f"Could not create appointment: {e}", "error")
        return redirect(url_for("appointments"))
    try:
        patients_list = fetch_all("SELECT patient_id, patient_name FROM Patients ORDER BY patient_name")
        doctors_list = fetch_all("SELECT doctor_id, doctor_name, specialization FROM Doctors ORDER BY doctor_name")
        rows = fetch_all("""SELECT a.*, p.patient_name, d.doctor_name, d.specialization
            FROM Appointments a JOIN Patients p ON p.patient_id=a.patient_id
            JOIN Doctors d ON d.doctor_id=a.doctor_id
            ORDER BY a.appointment_date DESC, a.appointment_time DESC""")
        db_error = None
    except Error as e:
        patients_list, doctors_list, rows, db_error = [], [], [], str(e)
    return render_template("appointments.html", appointments=rows, patients=patients_list,
                           doctors=doctors_list, db_error=db_error)

@app.route("/appointments/status/<int:appointment_id>", methods=["POST"])
def appointment_status(appointment_id):
    status = request.form.get("status", "Scheduled")
    if status not in ("Scheduled", "Completed", "Cancelled"):
        status = "Scheduled"
    try:
        execute("UPDATE Appointments SET status=%s WHERE appointment_id=%s", (status, appointment_id))
        flash("Appointment status updated.", "success")
    except Error as e:
        flash(f"Could not update status: {e}", "error")
    return redirect(url_for("appointments"))

@app.route("/billing", methods=["GET", "POST"])
def billing():
    if request.method == "POST":
        try:
            execute("""INSERT INTO Bills (patient_id, bill_date, total_amount, payment_status)
                       VALUES (%s, %s, %s, %s)""",
                    (request.form["patient_id"], request.form.get("bill_date") or None,
                     request.form["total_amount"], request.form.get("payment_status") or "Unpaid"))
            flash("Bill created successfully.", "success")
        except Error as e:
            flash(f"Could not create bill: {e}", "error")
        return redirect(url_for("billing"))
    try:
        patients_list = fetch_all("SELECT patient_id, patient_name FROM Patients ORDER BY patient_name")
        rows = fetch_all("""SELECT b.*, p.patient_name FROM Bills b
                            JOIN Patients p ON p.patient_id=b.patient_id
                            ORDER BY b.bill_id DESC""")
        db_error = None
    except Error as e:
        patients_list, rows, db_error = [], [], str(e)
    return render_template("billing.html", bills=rows, patients=patients_list, db_error=db_error)

@app.route("/billing/pay/<int:bill_id>", methods=["POST"])
def pay_bill(bill_id):
    try:
        execute("UPDATE Bills SET payment_status='Paid' WHERE bill_id=%s", (bill_id,))
        flash("Bill marked as paid.", "success")
    except Error as e:
        flash(f"Could not update bill: {e}", "error")
    return redirect(url_for("billing"))

@app.route("/medical-records")
def medical_records():
    try:
        rows = fetch_all("""SELECT m.*, p.patient_name, d.doctor_name
            FROM Medical_Records m JOIN Patients p ON p.patient_id=m.patient_id
            JOIN Doctors d ON d.doctor_id=m.doctor_id
            ORDER BY m.record_date DESC""")
        db_error = None
    except Error as e:
        rows, db_error = [], str(e)
    return render_template("medical_records.html", records=rows, db_error=db_error)

@app.route("/reports")
def reports():
    try:
        by_specialization = fetch_all("""
            SELECT specialization, COUNT(*) AS total FROM Doctors
            GROUP BY specialization ORDER BY total DESC
        """)
        revenue = fetch_all("""
            SELECT payment_status, COALESCE(SUM(total_amount),0) AS total
            FROM Bills GROUP BY payment_status
        """)
        db_error = None
    except Error as e:
        by_specialization, revenue, db_error = [], [], str(e)
    return render_template("reports.html", by_specialization=by_specialization,
                           revenue=revenue, db_error=db_error)

if __name__ == "__main__":
    app.run(debug=True)
