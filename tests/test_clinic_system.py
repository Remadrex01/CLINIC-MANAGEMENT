"""
ClinicCare Pro — Test Suite
============================
Runs with: python -m pytest tests/ -v

Tests cover:
- Database round-trips for all major entities
- UI module imports
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from clinic_management.database.db import ClinicDatabase


# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture
def db():
    """Provide a fresh in-memory-ish database for each test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield ClinicDatabase(str(Path(tmpdir) / "test_clinic.db"))


# ── Database tests ────────────────────────────────────────────────────────────

def test_default_admin_created(db):
    """A default admin account should exist immediately after DB creation."""
    user = db.authenticate_user("admin", "admin123")
    assert user is not None
    assert user["role"] == "Administrator"


def test_patient_create_and_read(db):
    pid = db.create_patient("Jane Doe", "Female", 32, "555-0100", "12 Main St", "O+")
    patients = db.get_patients()
    assert pid > 0
    assert any(p["fullname"] == "Jane Doe" for p in patients)


def test_patient_update(db):
    pid = db.create_patient("John Smith", "Male", 45, "555-0200", "5 Oak Ave", "A+")
    db.update_patient(pid, "John Smith Jr.", "Male", 46, "555-0201", "5 Oak Ave", "A+")
    patients = db.get_patients()
    updated = next(p for p in patients if p["patient_id"] == pid)
    assert updated["fullname"] == "John Smith Jr."
    assert updated["age"] == 46


def test_patient_delete(db):
    pid = db.create_patient("Delete Me", "Male", 20, "000", "Nowhere", "B-")
    db.delete_patient(pid)
    patients = db.get_patients()
    assert not any(p["patient_id"] == pid for p in patients)


def test_patient_search(db):
    db.create_patient("Alice Kamara", "Female", 28, "077-111", "Freetown", "AB+")
    results = db.search_patients("Kamara")
    assert len(results) >= 1
    assert results[0]["fullname"] == "Alice Kamara"


def test_doctor_create_and_read(db):
    did = db.create_doctor("Dr. Kofi", "Paediatrics", "077-999", "kofi@clinic.sl")
    doctors = db.get_doctors()
    assert did > 0
    assert any(d["fullname"] == "Dr. Kofi" for d in doctors)


def test_doctor_update(db):
    did = db.create_doctor("Dr. A", "General", "000", "a@clinic.sl")
    db.update_doctor(did, "Dr. A Updated", "Surgery", "111", "a2@clinic.sl")
    doctors = db.get_doctors()
    updated = next(d for d in doctors if d["doctor_id"] == did)
    assert updated["specialization"] == "Surgery"


def test_doctor_delete(db):
    did = db.create_doctor("Dr. Delete", "General", "000", "del@clinic.sl")
    db.delete_doctor(did)
    doctors = db.get_doctors()
    assert not any(d["doctor_id"] == did for d in doctors)


def test_appointment_create_and_read(db):
    pid = db.create_patient("Appt Patient", "Male", 30, "111", "Main St", "O+")
    did = db.create_doctor("Appt Doctor", "General", "222", "doc@clinic.sl")
    aid = db.create_appointment(pid, did, "2026-07-01", "09:00", "Scheduled")
    appts = db.get_appointments()
    assert aid > 0
    assert any(a["appointment_id"] == aid for a in appts)


def test_medicine_create_and_read(db):
    mid = db.create_medicine("Paracetamol 500mg", 100, 0.50, "2027-01-01")
    medicines = db.get_medicines()
    assert mid > 0
    assert any(m["medicine_name"] == "Paracetamol 500mg" for m in medicines)


def test_medicine_low_stock_flag(db):
    db.create_medicine("Low Stock Drug", 5, 1.00, "2027-06-01")
    stats = db.get_dashboard_stats()
    assert stats["medicines"] >= 1  # at least one low-stock item


def test_bill_create_and_read(db):
    pid = db.create_patient("Bill Patient", "Female", 25, "333", "Hill Rd", "B+")
    bid = db.create_bill(pid, 75.00, "Paid")
    bills = db.get_billing()
    assert bid > 0
    assert any(b["bill_id"] == bid for b in bills)


def test_dashboard_stats(db):
    db.create_patient("Stats Patient", "Male", 40, "444", "Valley", "A-")
    db.create_doctor("Stats Doctor", "ENT", "555", "ent@clinic.sl")
    stats = db.get_dashboard_stats()
    assert stats["patients"] >= 1
    assert stats["doctors"] >= 1
    assert "revenue" in stats
    assert "medicines" in stats


def test_register_and_authenticate_user(db):
    db.register_user("Nurse Joy", "njoy", "joy@clinic.sl", "066-111", "Secret99!", "Nurse")
    user = db.authenticate_user("njoy", "Secret99!")
    assert user is not None
    assert user["role"] == "Nurse"


def test_wrong_password_rejected(db):
    result = db.authenticate_user("admin", "wrongpassword")
    assert result is None


# ── Import / UI tests ─────────────────────────────────────────────────────────

def test_ui_modules_import():
    """All view classes must be importable without errors."""
    from clinic_management import ClinicManagementApp
    from clinic_management.authentication.auth import AuthenticationPanel
    from clinic_management.dashboard.dashboard import DashboardView
    from clinic_management.patients.patients import PatientsView
    from clinic_management.doctors.doctor import DoctorsView
    from clinic_management.appointments.appointment import AppointmentView
    from clinic_management.pharmacy.pharmacy import PharmacyView
    from clinic_management.billing.billing import BillingView
    from clinic_management.reports.reports import ReportsView

    assert all([
        ClinicManagementApp,
        AuthenticationPanel,
        DashboardView,
        PatientsView,
        DoctorsView,
        AppointmentView,
        PharmacyView,
        BillingView,
        ReportsView,
    ])
