CREATE DATABASE IF NOT EXISTS hospital_management;
USE hospital_management;

CREATE TABLE IF NOT EXISTS Patients (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_name VARCHAR(100) NOT NULL,
    gender VARCHAR(10),
    age INT,
    phone VARCHAR(15),
    address VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS Doctors (
    doctor_id INT PRIMARY KEY AUTO_INCREMENT,
    doctor_name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100),
    phone VARCHAR(15),
    consultation_fee DECIMAL(10,2) DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Appointments (
    appointment_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME,
    status VARCHAR(20) DEFAULT 'Scheduled',
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id)
);

CREATE TABLE IF NOT EXISTS Medical_Records (
    record_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    diagnosis VARCHAR(200),
    treatment VARCHAR(200),
    record_date DATE,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id)
);

CREATE TABLE IF NOT EXISTS Prescriptions (
    prescription_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    medicine_name VARCHAR(100),
    dosage VARCHAR(100),
    duration VARCHAR(50),
    prescription_date DATE,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id)
);

CREATE TABLE IF NOT EXISTS Bills (
    bill_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    bill_date DATE,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'Unpaid',
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
);

-- Optional sample data. Run only if your tables are empty.
INSERT INTO Patients (patient_name, gender, age, phone, address)
SELECT 'Aman Sharma', 'Male', 25, '9876500001', 'Mohali'
WHERE NOT EXISTS (SELECT 1 FROM Patients WHERE patient_name='Aman Sharma');

INSERT INTO Doctors (doctor_name, specialization, phone, consultation_fee)
SELECT 'Dr. Raj Mehta', 'Cardiologist', '9876510001', 800.00
WHERE NOT EXISTS (SELECT 1 FROM Doctors WHERE doctor_name='Dr. Raj Mehta');

INSERT INTO Doctors (doctor_name, specialization, phone, consultation_fee)
SELECT 'Dr. Simran Kaur', 'Dermatologist', '9876510002', 600.00
WHERE NOT EXISTS (SELECT 1 FROM Doctors WHERE doctor_name='Dr. Simran Kaur');
