"""
Smarter Health Connection — Database Layer
==========================================
Manages all SQLite tables with complete CRUD operations.
No external dependencies — uses Python stdlib sqlite3 only.
"""

from __future__ import annotations

import hashlib
import os
import sqlite3
from pathlib import Path
from typing import Optional


# Database stored inside clinic_management subfolder
_BASE_DIR = Path(__file__).resolve().parent
DB_PATH = str(_BASE_DIR / "clinic_management" / "smarter_health.db")


class Database:
    """
    Central database access object.
    Tables: users, patients, doctors, appointments, pharmacy, billing, clinic_settings.
    Pass the path argument to override the default location (useful in tests).
    """

    def __init__(self, db_path: str = DB_PATH) -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()
        self._seed_defaults()

    # ── Schema ──────────────────────────────────────────────────────────────

    def _create_tables(self) -> None:
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname      TEXT    NOT NULL,
                username      TEXT    UNIQUE NOT NULL,
                email         TEXT    UNIQUE NOT NULL,
                phone         TEXT    NOT NULL,
                gender        TEXT    NOT NULL DEFAULT 'Not Specified',
                dob           TEXT    NOT NULL DEFAULT '',
                address       TEXT    NOT NULL DEFAULT '',
                role          TEXT    NOT NULL DEFAULT 'Receptionist',
                password_hash TEXT    NOT NULL,
                created_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS patients (
                patient_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname          TEXT    NOT NULL,
                gender            TEXT    NOT NULL,
                age               INTEGER NOT NULL,
                phone             TEXT    NOT NULL,
                email             TEXT    NOT NULL DEFAULT '',
                address           TEXT    NOT NULL,
                blood_group       TEXT    NOT NULL DEFAULT 'Unknown',
                emergency_contact TEXT    NOT NULL DEFAULT '',
                registration_date TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS doctors (
                doctor_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname       TEXT NOT NULL,
                specialization TEXT NOT NULL,
                phone          TEXT NOT NULL,
                email          TEXT NOT NULL,
                availability   TEXT NOT NULL DEFAULT 'Available',
                license_no     TEXT NOT NULL DEFAULT '',
                created_at     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id       INTEGER NOT NULL,
                doctor_id        INTEGER NOT NULL,
                appointment_date TEXT    NOT NULL,
                appointment_time TEXT    NOT NULL,
                reason           TEXT    NOT NULL DEFAULT '',
                status           TEXT    NOT NULL DEFAULT 'Pending',
                notes            TEXT    NOT NULL DEFAULT '',
                created_at       TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id)  REFERENCES doctors(doctor_id)   ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS pharmacy (
                medicine_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                medicine_name TEXT    NOT NULL,
                category      TEXT    NOT NULL DEFAULT 'General',
                quantity      INTEGER NOT NULL DEFAULT 0,
                unit_price    REAL    NOT NULL DEFAULT 0.0,
                expiry_date   TEXT    NOT NULL,
                supplier      TEXT    NOT NULL DEFAULT '',
                created_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS billing (
                bill_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id     INTEGER NOT NULL,
                total_amount   REAL    NOT NULL DEFAULT 0.0,
                paid_amount    REAL    NOT NULL DEFAULT 0.0,
                payment_status TEXT    NOT NULL DEFAULT 'Unpaid',
                payment_method TEXT    NOT NULL DEFAULT 'Cash',
                notes          TEXT    NOT NULL DEFAULT '',
                created_at     TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS clinic_settings (
                id             INTEGER PRIMARY KEY DEFAULT 1,
                clinic_name    TEXT NOT NULL DEFAULT 'Smarter Health Connection',
                clinic_address TEXT NOT NULL DEFAULT '',
                clinic_phone   TEXT NOT NULL DEFAULT '',
                clinic_email   TEXT NOT NULL DEFAULT '',
                theme          TEXT NOT NULL DEFAULT 'light'
            );
        """)
        self.conn.commit()

    def _seed_defaults(self) -> None:
        if not self.conn.execute("SELECT 1 FROM users WHERE username='admin'").fetchone():
            self.conn.execute(
                "INSERT INTO users (fullname,username,email,phone,role,password_hash) VALUES (?,?,?,?,?,?)",
                ("System Administrator", "admin", "admin@clinic.local",
                 "0000000000", "Administrator", self._hash("admin123")),
            )
        if not self.conn.execute("SELECT 1 FROM clinic_settings WHERE id=1").fetchone():
            self.conn.execute("INSERT INTO clinic_settings (id) VALUES (1)")
        self.conn.commit()

    # ── Hashing ─────────────────────────────────────────────────────────────

    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    # ── Authentication ──────────────────────────────────────────────────────

    def authenticate(self, username: str, password: str) -> Optional[sqlite3.Row]:
        row = self.conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if row and row["password_hash"] == self._hash(password):
            return row
        return None

    def create_user(self, fullname, username, email, phone, gender, dob, address, role, password):
        try:
            self.conn.execute(
                "INSERT INTO users (fullname,username,email,phone,gender,dob,address,role,password_hash)"
                " VALUES (?,?,?,?,?,?,?,?,?)",
                (fullname, username, email, phone, gender, dob, address, role, self._hash(password)),
            )
            self.conn.commit()
            return True, "Account created successfully."
        except sqlite3.IntegrityError as exc:
            msg = str(exc)
            if "username" in msg:
                return False, "Username already exists."
            if "email" in msg:
                return False, "Email already registered."
            return False, msg

    def update_password(self, user_id: int, new_password: str) -> None:
        self.conn.execute(
            "UPDATE users SET password_hash = ? WHERE user_id = ?",
            (self._hash(new_password), user_id),
        )
        self.conn.commit()

    # ── Patients ─────────────────────────────────────────────────────────────

    def create_patient(self, fullname, gender, age, phone, email, address, blood_group, emergency_contact) -> int:
        cur = self.conn.execute(
            "INSERT INTO patients (fullname,gender,age,phone,email,address,blood_group,emergency_contact)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (fullname, gender, int(age), phone, email, address, blood_group, emergency_contact),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def get_patients(self, keyword: str = "") -> list:
        if keyword:
            kw = f"%{keyword}%"
            return self.conn.execute(
                "SELECT * FROM patients WHERE fullname LIKE ? OR phone LIKE ? OR address LIKE ?"
                " ORDER BY patient_id DESC",
                (kw, kw, kw),
            ).fetchall()
        return self.conn.execute("SELECT * FROM patients ORDER BY patient_id DESC").fetchall()

    def get_patient(self, patient_id: int) -> Optional[sqlite3.Row]:
        return self.conn.execute("SELECT * FROM patients WHERE patient_id=?", (patient_id,)).fetchone()

    def update_patient(self, patient_id, fullname, gender, age, phone, email, address, blood_group, emergency_contact) -> None:
        self.conn.execute(
            "UPDATE patients SET fullname=?,gender=?,age=?,phone=?,email=?,address=?,blood_group=?,emergency_contact=?"
            " WHERE patient_id=?",
            (fullname, gender, int(age), phone, email, address, blood_group, emergency_contact, patient_id),
        )
        self.conn.commit()

    def delete_patient(self, patient_id: int) -> None:
        self.conn.execute("DELETE FROM patients WHERE patient_id=?", (patient_id,))
        self.conn.commit()

    def count_patients(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]

    def get_patient_names(self) -> dict:
        rows = self.conn.execute("SELECT patient_id, fullname FROM patients ORDER BY fullname").fetchall()
        return {r["fullname"]: r["patient_id"] for r in rows}

    # ── Doctors ──────────────────────────────────────────────────────────────

    def create_doctor(self, fullname, specialization, phone, email, availability, license_no) -> int:
        cur = self.conn.execute(
            "INSERT INTO doctors (fullname,specialization,phone,email,availability,license_no)"
            " VALUES (?,?,?,?,?,?)",
            (fullname, specialization, phone, email, availability, license_no),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def get_doctors(self, keyword: str = "") -> list:
        if keyword:
            kw = f"%{keyword}%"
            return self.conn.execute(
                "SELECT * FROM doctors WHERE fullname LIKE ? OR specialization LIKE ? OR email LIKE ?"
                " ORDER BY doctor_id DESC",
                (kw, kw, kw),
            ).fetchall()
        return self.conn.execute("SELECT * FROM doctors ORDER BY doctor_id DESC").fetchall()

    def get_doctor(self, doctor_id: int) -> Optional[sqlite3.Row]:
        return self.conn.execute("SELECT * FROM doctors WHERE doctor_id=?", (doctor_id,)).fetchone()

    def update_doctor(self, doctor_id, fullname, specialization, phone, email, availability, license_no) -> None:
        self.conn.execute(
            "UPDATE doctors SET fullname=?,specialization=?,phone=?,email=?,availability=?,license_no=?"
            " WHERE doctor_id=?",
            (fullname, specialization, phone, email, availability, license_no, doctor_id),
        )
        self.conn.commit()

    def delete_doctor(self, doctor_id: int) -> None:
        self.conn.execute("DELETE FROM doctors WHERE doctor_id=?", (doctor_id,))
        self.conn.commit()

    def count_doctors(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]

    def get_doctor_names(self) -> dict:
        rows = self.conn.execute("SELECT doctor_id, fullname FROM doctors ORDER BY fullname").fetchall()
        return {r["fullname"]: r["doctor_id"] for r in rows}

    # ── Appointments ─────────────────────────────────────────────────────────

    def create_appointment(self, patient_id, doctor_id, date, time, reason, status="Pending") -> int:
        cur = self.conn.execute(
            "INSERT INTO appointments (patient_id,doctor_id,appointment_date,appointment_time,reason,status)"
            " VALUES (?,?,?,?,?,?)",
            (patient_id, doctor_id, date, time, reason, status),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def get_appointments(self, keyword: str = "") -> list:
        base = (
            "SELECT a.*, p.fullname AS patient_name, d.fullname AS doctor_name"
            " FROM appointments a"
            " JOIN patients p ON p.patient_id = a.patient_id"
            " JOIN doctors  d ON d.doctor_id  = a.doctor_id"
        )
        if keyword:
            kw = f"%{keyword}%"
            return self.conn.execute(
                base + " WHERE p.fullname LIKE ? OR d.fullname LIKE ? OR a.status LIKE ?"
                       " ORDER BY a.appointment_date DESC",
                (kw, kw, kw),
            ).fetchall()
        return self.conn.execute(base + " ORDER BY a.appointment_date DESC").fetchall()

    def update_appointment(self, appt_id, patient_id, doctor_id, date, time, reason, status, notes) -> None:
        self.conn.execute(
            "UPDATE appointments SET patient_id=?,doctor_id=?,appointment_date=?,appointment_time=?,"
            "reason=?,status=?,notes=? WHERE appointment_id=?",
            (patient_id, doctor_id, date, time, reason, status, notes, appt_id),
        )
        self.conn.commit()

    def delete_appointment(self, appt_id: int) -> None:
        self.conn.execute("DELETE FROM appointments WHERE appointment_id=?", (appt_id,))
        self.conn.commit()

    def count_appointments_today(self) -> int:
        return self.conn.execute(
            "SELECT COUNT(*) FROM appointments WHERE appointment_date = date('now')"
        ).fetchone()[0]

    # ── Pharmacy ─────────────────────────────────────────────────────────────

    def create_medicine(self, name, category, quantity, unit_price, expiry_date, supplier) -> int:
        cur = self.conn.execute(
            "INSERT INTO pharmacy (medicine_name,category,quantity,unit_price,expiry_date,supplier)"
            " VALUES (?,?,?,?,?,?)",
            (name, category, int(quantity), float(unit_price), expiry_date, supplier),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def get_medicines(self, keyword: str = "") -> list:
        if keyword:
            kw = f"%{keyword}%"
            return self.conn.execute(
                "SELECT * FROM pharmacy WHERE medicine_name LIKE ? OR category LIKE ?"
                " ORDER BY medicine_id DESC",
                (kw, kw),
            ).fetchall()
        return self.conn.execute("SELECT * FROM pharmacy ORDER BY medicine_id DESC").fetchall()

    def update_medicine(self, med_id, name, category, quantity, unit_price, expiry_date, supplier) -> None:
        self.conn.execute(
            "UPDATE pharmacy SET medicine_name=?,category=?,quantity=?,unit_price=?,expiry_date=?,supplier=?"
            " WHERE medicine_id=?",
            (name, category, int(quantity), float(unit_price), expiry_date, supplier, med_id),
        )
        self.conn.commit()

    def delete_medicine(self, med_id: int) -> None:
        self.conn.execute("DELETE FROM pharmacy WHERE medicine_id=?", (med_id,))
        self.conn.commit()

    def count_low_stock(self, threshold: int = 10) -> int:
        return self.conn.execute(
            "SELECT COUNT(*) FROM pharmacy WHERE quantity < ?", (threshold,)
        ).fetchone()[0]

    # ── Billing ──────────────────────────────────────────────────────────────

    def create_bill(self, patient_id, total_amount, paid_amount, payment_status, payment_method, notes) -> int:
        cur = self.conn.execute(
            "INSERT INTO billing (patient_id,total_amount,paid_amount,payment_status,payment_method,notes)"
            " VALUES (?,?,?,?,?,?)",
            (patient_id, float(total_amount), float(paid_amount), payment_status, payment_method, notes),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def get_bills(self, keyword: str = "") -> list:
        base = (
            "SELECT b.*, p.fullname AS patient_name FROM billing b"
            " JOIN patients p ON p.patient_id = b.patient_id"
        )
        if keyword:
            kw = f"%{keyword}%"
            return self.conn.execute(
                base + " WHERE p.fullname LIKE ? OR b.payment_status LIKE ? ORDER BY b.bill_id DESC",
                (kw, kw),
            ).fetchall()
        return self.conn.execute(base + " ORDER BY b.bill_id DESC").fetchall()

    def update_bill(self, bill_id, total_amount, paid_amount, payment_status, payment_method, notes) -> None:
        self.conn.execute(
            "UPDATE billing SET total_amount=?,paid_amount=?,payment_status=?,payment_method=?,notes=?"
            " WHERE bill_id=?",
            (float(total_amount), float(paid_amount), payment_status, payment_method, notes, bill_id),
        )
        self.conn.commit()

    def delete_bill(self, bill_id: int) -> None:
        self.conn.execute("DELETE FROM billing WHERE bill_id=?", (bill_id,))
        self.conn.commit()

    def get_total_revenue(self) -> float:
        result = self.conn.execute(
            "SELECT COALESCE(SUM(paid_amount), 0) FROM billing WHERE payment_status = 'Paid'"
        ).fetchone()[0]
        return float(result)

    def count_bills(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM billing").fetchone()[0]

    # ── Settings ─────────────────────────────────────────────────────────────

    def get_settings(self) -> Optional[sqlite3.Row]:
        return self.conn.execute("SELECT * FROM clinic_settings WHERE id=1").fetchone()

    def update_settings(self, clinic_name, clinic_address, clinic_phone, clinic_email) -> None:
        self.conn.execute(
            "UPDATE clinic_settings SET clinic_name=?,clinic_address=?,clinic_phone=?,clinic_email=?"
            " WHERE id=1",
            (clinic_name, clinic_address, clinic_phone, clinic_email),
        )
        self.conn.commit()

    # ── Dashboard stats ───────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        return {
            "patients":     self.count_patients(),
            "doctors":      self.count_doctors(),
            "appointments": self.count_appointments_today(),
            "bills":        self.count_bills(),
            "revenue":      self.get_total_revenue(),
            "low_stock":    self.count_low_stock(),
        }

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass
