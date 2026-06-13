"""SQLite database layer for the clinic management system."""

from __future__ import annotations

import hashlib
import os
import sqlite3
from pathlib import Path
from typing import Any, Optional

try:
    import bcrypt
except ImportError:
    bcrypt = None


class ClinicDatabase:
    """Manages the SQLite schema and common CRUD operations."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = db_path or os.path.join(os.getcwd(), "clinic_management", "clinic.db")
        self._ensure_directory()
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.initialize_schema()
        self.create_default_admin()

    def _ensure_directory(self) -> None:
        directory = Path(self.db_path).parent
        directory.mkdir(parents=True, exist_ok=True)

    def initialize_schema(self) -> None:
        schema_path = Path(__file__).resolve().parent / "schema.sql"
        with schema_path.open("r", encoding="utf-8") as handle:
            self.connection.executescript(handle.read())
        self.connection.commit()

    def create_default_admin(self) -> None:
        existing = self.connection.execute(
            "SELECT user_id FROM users WHERE username = ?", ("admin",)
        ).fetchone()
        if existing:
            return
        self.create_user(
            fullname="System Administrator",
            username="admin",
            email="admin@clinic.local",
            phone="0000000000",
            password="admin123",
            role="Administrator",
        )

    def _hash_password(self, password: str) -> str:
        if bcrypt is not None:
            return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _verify_password(self, password: str, password_hash: str) -> bool:
        if bcrypt is not None and password_hash.startswith("$2"):
            return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
        return hashlib.sha256(password.encode("utf-8")).hexdigest() == password_hash

    def create_user(self, fullname: str, username: str, email: str, phone: str, password: str, role: str) -> int:
        cursor = self.connection.execute(
            "INSERT INTO users (fullname, username, email, phone, password_hash, role) VALUES (?, ?, ?, ?, ?, ?)",
            (fullname, username, email, phone, self._hash_password(password), role),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def authenticate_user(self, username: str, password: str) -> Optional[sqlite3.Row]:
        row = self.connection.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if row and self._verify_password(password, row["password_hash"]):
            return row
        return None

    def register_user(self, fullname: str, username: str, email: str, phone: str, password: str, role: str) -> int:
        return self.create_user(fullname, username, email, phone, password, role)

    def create_patient(self, fullname: str, gender: str, age: int, phone: str, address: str, blood_group: str) -> int:
        cursor = self.connection.execute(
            "INSERT INTO patients (fullname, gender, age, phone, address, blood_group) VALUES (?, ?, ?, ?, ?, ?)",
            (fullname, gender, age, phone, address, blood_group),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get_patients(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            "SELECT * FROM patients ORDER BY patient_id DESC"
        ).fetchall()

    def update_patient(self, patient_id: int, fullname: str, gender: str, age: int, phone: str, address: str, blood_group: str) -> None:
        self.connection.execute(
            "UPDATE patients SET fullname = ?, gender = ?, age = ?, phone = ?, address = ?, blood_group = ? WHERE patient_id = ?",
            (fullname, gender, age, phone, address, blood_group, patient_id),
        )
        self.connection.commit()

    def delete_patient(self, patient_id: int) -> None:
        self.connection.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,))
        self.connection.commit()

    def search_patients(self, keyword: str) -> list[sqlite3.Row]:
        term = f"%{keyword}%"
        return self.connection.execute(
            "SELECT * FROM patients WHERE fullname LIKE ? OR phone LIKE ? OR address LIKE ? ORDER BY patient_id DESC",
            (term, term, term),
        ).fetchall()

    def create_doctor(self, fullname: str, specialization: str, phone: str, email: str) -> int:
        cursor = self.connection.execute(
            "INSERT INTO doctors (fullname, specialization, phone, email) VALUES (?, ?, ?, ?)",
            (fullname, specialization, phone, email),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get_doctors(self) -> list[sqlite3.Row]:
        return self.connection.execute("SELECT * FROM doctors ORDER BY doctor_id DESC").fetchall()

    def update_doctor(self, doctor_id: int, fullname: str, specialization: str, phone: str, email: str) -> None:
        self.connection.execute(
            "UPDATE doctors SET fullname = ?, specialization = ?, phone = ?, email = ? WHERE doctor_id = ?",
            (fullname, specialization, phone, email, doctor_id),
        )
        self.connection.commit()

    def delete_doctor(self, doctor_id: int) -> None:
        self.connection.execute("DELETE FROM doctors WHERE doctor_id = ?", (doctor_id,))
        self.connection.commit()

    def search_doctors(self, keyword: str) -> list[sqlite3.Row]:
        term = f"%{keyword}%"
        return self.connection.execute(
            "SELECT * FROM doctors WHERE fullname LIKE ? OR specialization LIKE ? OR email LIKE ? ORDER BY doctor_id DESC",
            (term, term, term),
        ).fetchall()

    def create_appointment(self, patient_id: int, doctor_id: int, appointment_date: str, appointment_time: str, status: str) -> int:
        cursor = self.connection.execute(
            "INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, status) VALUES (?, ?, ?, ?, ?)",
            (patient_id, doctor_id, appointment_date, appointment_time, status),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get_appointments(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            "SELECT a.appointment_id, p.fullname AS patient_name, d.fullname AS doctor_name, a.appointment_date, a.appointment_time, a.status FROM appointments a JOIN patients p ON p.patient_id = a.patient_id JOIN doctors d ON d.doctor_id = a.doctor_id ORDER BY a.appointment_date, a.appointment_time"
        ).fetchall()

    def update_appointment(self, appointment_id: int, patient_id: int, doctor_id: int, appointment_date: str, appointment_time: str, status: str) -> None:
        self.connection.execute(
            "UPDATE appointments SET patient_id = ?, doctor_id = ?, appointment_date = ?, appointment_time = ?, status = ? WHERE appointment_id = ?",
            (patient_id, doctor_id, appointment_date, appointment_time, status, appointment_id),
        )
        self.connection.commit()

    def delete_appointment(self, appointment_id: int) -> None:
        self.connection.execute("DELETE FROM appointments WHERE appointment_id = ?", (appointment_id,))
        self.connection.commit()

    def create_medicine(self, medicine_name: str, quantity: int, price: float, expiry_date: str) -> int:
        cursor = self.connection.execute(
            "INSERT INTO pharmacy (medicine_name, quantity, price, expiry_date) VALUES (?, ?, ?, ?)",
            (medicine_name, quantity, price, expiry_date),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get_medicines(self) -> list[sqlite3.Row]:
        return self.connection.execute("SELECT * FROM pharmacy ORDER BY medicine_id DESC").fetchall()

    def update_medicine(self, medicine_id: int, medicine_name: str, quantity: int, price: float, expiry_date: str) -> None:
        self.connection.execute(
            "UPDATE pharmacy SET medicine_name = ?, quantity = ?, price = ?, expiry_date = ? WHERE medicine_id = ?",
            (medicine_name, quantity, price, expiry_date, medicine_id),
        )
        self.connection.commit()

    def delete_medicine(self, medicine_id: int) -> None:
        self.connection.execute("DELETE FROM pharmacy WHERE medicine_id = ?", (medicine_id,))
        self.connection.commit()

    def search_medicines(self, keyword: str) -> list[sqlite3.Row]:
        term = f"%{keyword}%"
        return self.connection.execute(
            "SELECT * FROM pharmacy WHERE medicine_name LIKE ? ORDER BY medicine_id DESC",
            (term,),
        ).fetchall()

    def create_bill(self, patient_id: int, amount: float, payment_status: str) -> int:
        cursor = self.connection.execute(
            "INSERT INTO billing (patient_id, amount, payment_status) VALUES (?, ?, ?)",
            (patient_id, amount, payment_status),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get_billing(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            "SELECT b.bill_id, p.fullname AS patient_name, b.amount, b.payment_status, b.payment_date FROM billing b JOIN patients p ON p.patient_id = b.patient_id ORDER BY b.bill_id DESC"
        ).fetchall()

    def get_dashboard_stats(self) -> dict[str, int | float]:
        patients = self.connection.execute("SELECT COUNT(*) AS count FROM patients").fetchone()["count"]
        doctors = self.connection.execute("SELECT COUNT(*) AS count FROM doctors").fetchone()["count"]
        appointments = self.connection.execute("SELECT COUNT(*) AS count FROM appointments WHERE appointment_date = date('now')").fetchone()["count"]
        revenue = self.connection.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM billing WHERE payment_date = date('now')").fetchone()["total"]
        medicines = self.connection.execute("SELECT COUNT(*) AS count FROM pharmacy WHERE quantity < 10").fetchone()["count"]
        return {
            "patients": patients,
            "doctors": doctors,
            "appointments": appointments,
            "revenue": revenue,
            "medicines": medicines,
        }

def create_database():
    print("Database initialized successfully")
