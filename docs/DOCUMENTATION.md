# ClinicCare Pro — Full Technical Documentation

> **Version:** 2.0.0 | **Python:** 3.8+ | **Database:** SQLite 3 | **GUI:** Tkinter

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Project Structure](#3-project-structure)
4. [Module Reference](#4-module-reference)
   - [app.py — Main Application](#41-apppy--main-application)
   - [database/db.py — Data Layer](#42-databasedbpy--data-layer)
   - [authentication/auth.py — Auth Panel](#43-authenticationauthpy--authentication)
   - [dashboard/dashboard.py — Dashboard](#44-dashboarddashboardpy--dashboard)
   - [patients/patients.py — Patients](#45-patientspatientspy--patients)
   - [doctors/doctor.py — Doctors](#46-doctorsdoctorpy--doctors)
   - [appointments/appointment.py — Appointments](#47-appointmentsappointmentpy--appointments)
   - [pharmacy/pharmacy.py — Pharmacy](#48-pharmacypharmacypy--pharmacy)
   - [billing/billing.py — Billing](#49-billingbillingpy--billing)
   - [reports/reports.py — Reports](#410-reportsreportspy--reports)
   - [utils/theme.py — ThemeManager](#411-utilsthemepy--thememanager)
5. [Database Schema](#5-database-schema)
6. [Data Flow](#6-data-flow)
7. [Structured Programming Principles](#7-structured-programming-principles)
8. [Security Features](#8-security-features)
9. [Testing](#9-testing)
10. [Future Enhancements](#10-future-enhancements)

---

## 1. Project Overview

**ClinicCare Pro** (formerly *Smarter Health Connection*) is a desktop clinic management system built with Python and Tkinter. It targets peripheral health units in Sierra Leone with the goal of digitising patient flow, doctor management, appointments, pharmacy inventory, and billing.

| Property | Value |
|---|---|
| Language | Python 3.8+ |
| GUI Framework | Tkinter / ttk |
| Database | SQLite 3 (file-based, zero-config) |
| Architecture | Modular MVC-style packages |
| Entry Point | `main.py` |
| SDG Alignment | SDG 3 — Good Health and Well-being |

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────┐
│                  main.py (entry point)               │
│        Python version check → DPI awareness          │
│                ClinicManagementApp()                 │
└────────────────────────┬────────────────────────────┘
                         │
          ┌──────────────▼──────────────┐
          │   clinic_management/app.py   │
          │   ClinicManagementApp(tk.Tk) │
          │  ┌─────────┐ ┌───────────┐  │
          │  │ Header  │ │  Sidebar  │  │
          │  └─────────┘ └─────┬─────┘  │
          │                    │ navigate│
          │  ┌─────────────────▼──────┐  │
          │  │     Content Frame       │  │
          │  │  (lazy view mounting)   │  │
          │  └────────────────────────┘  │
          └──────────────┬───────────────┘
                         │
          ┌──────────────▼───────────────────────────────┐
          │           Module Views (ttk.Frame)            │
          │  Dashboard │ Patients │ Doctors │ Appointments│
          │  Pharmacy  │ Billing  │ Reports │             │
          └──────────────┬───────────────────────────────┘
                         │ reads / writes
          ┌──────────────▼───────────────┐
          │     ClinicDatabase (db.py)    │
          │     SQLite3  ←→  clinic.db   │
          └──────────────────────────────┘
```

### Navigation Model
Views are **created lazily** the first time a nav item is clicked and then cached. Navigation calls `view.grid_remove()` / `view.grid()` to show/hide — views are never destroyed, so their local state (search text, selections) is preserved between visits.

---

## 3. Project Structure

```
Structure Programming/                 ← project root
│
├── main.py                            ← RUN THIS to launch the app
├── run.bat                            ← Double-click launcher (Windows)
├── setup.bat                          ← First-time setup + launcher
├── requirements.txt                   ← Optional Python dependencies
├── README.md                          ← Project overview
├── LICENSE                            ← MIT License
│
├── clinic_management/                 ← Main Python package
│   ├── __init__.py                    ← Exports ClinicManagementApp
│   ├── app.py                         ← ClinicManagementApp (main window)
│   │
│   ├── authentication/
│   │   ├── __init__.py
│   │   ├── auth.py                    ← Login + Register panel
│   │   └── login.py                   ← Legacy stub (superseded)
│   │
│   ├── dashboard/
│   │   ├── __init__.py
│   │   └── dashboard.py               ← Overview stat cards
│   │
│   ├── patients/
│   │   ├── __init__.py
│   │   └── patients.py                ← Patient CRUD + export
│   │
│   ├── doctors/
│   │   ├── __init__.py
│   │   └── doctor.py                  ← Doctor CRUD + export
│   │
│   ├── appointments/
│   │   ├── __init__.py
│   │   └── appointment.py             ← Appointment CRUD
│   │
│   ├── pharmacy/
│   │   ├── __init__.py
│   │   └── pharmacy.py                ← Medicine inventory + low-stock alerts
│   │
│   ├── billing/
│   │   ├── __init__.py
│   │   └── billing.py                 ← Billing + payment tracking
│   │
│   ├── reports/
│   │   ├── __init__.py
│   │   └── reports.py                 ← Analytics + billing ledger
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py                      ← ClinicDatabase (all SQL)
│   │   └── schema.sql                 ← Table DDL
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── theme.py                   ← ThemeManager (light/dark)
│   │
│   └── assets/
│       ├── icons/
│       └── images/
│
├── tests/
│   └── test_clinic_system.py          ← pytest test suite
│
└── docs/
    ├── DOCUMENTATION.md               ← This file (technical reference)
    ├── INSTALLATION_GUIDE.md          ← Step-by-step setup
    └── USER_MANUAL.md                 ← End-user workflow guide
```

---

## 4. Module Reference

### 4.1 `app.py` — Main Application

**Class:** `ClinicManagementApp(tk.Tk)`

The top-level window. Responsibilities:
- Bootstrap `ClinicDatabase`
- Show `AuthenticationPanel` on launch
- On login success, build the main shell (header + sidebar + content pane + status bar)
- Lazy-create and cache module views via `_navigate(key)`
- Provide logout, theme toggle, fullscreen (F11), and graceful close

**Key Methods:**

| Method | Description |
|---|---|
| `_configure_window()` | Sets geometry, min-size, centres on screen, binds F11/Escape |
| `_show_auth_screen()` | Renders the login/register card over a decorative canvas |
| `_on_authenticated(user)` | Called by auth panel; stores user, builds main shell |
| `_build_main_shell()` | Creates header, sidebar, content frame, status bar |
| `_navigate(key)` | Swaps visible view, highlights active nav button |
| `_create_view(key)` | Factory — instantiates the correct `ttk.Frame` subclass |
| `_tick_clock()` | Updates the status-bar clock every second via `after(1000, …)` |

---

### 4.2 `database/db.py` — Data Layer

**Class:** `ClinicDatabase`

All SQL is encapsulated here. The UI never writes SQL directly.

**Constructor:** `ClinicDatabase(db_path=None)`
- Default path: `<cwd>/clinic_management/clinic.db`
- Runs `schema.sql` via `executescript` (idempotent — `CREATE TABLE IF NOT EXISTS`)
- Creates default admin on first run

**Methods:**

| Category | Method | Returns |
|---|---|---|
| Auth | `authenticate_user(username, password)` | `sqlite3.Row` or `None` |
| Auth | `register_user(fullname, username, email, phone, password, role)` | `int` (new user_id) |
| Auth | `create_user(...)` | `int` |
| Patients | `create_patient(fullname, gender, age, phone, address, blood_group)` | `int` |
| Patients | `get_patients()` | `list[Row]` |
| Patients | `update_patient(patient_id, ...)` | `None` |
| Patients | `delete_patient(patient_id)` | `None` |
| Patients | `search_patients(keyword)` | `list[Row]` |
| Doctors | `create_doctor(fullname, specialization, phone, email)` | `int` |
| Doctors | `get_doctors()` | `list[Row]` |
| Doctors | `update_doctor(doctor_id, ...)` | `None` |
| Doctors | `delete_doctor(doctor_id)` | `None` |
| Doctors | `search_doctors(keyword)` | `list[Row]` |
| Appointments | `create_appointment(patient_id, doctor_id, date, time, status)` | `int` |
| Appointments | `get_appointments()` | `list[Row]` (with JOINed names) |
| Appointments | `update_appointment(appointment_id, ...)` | `None` |
| Appointments | `delete_appointment(appointment_id)` | `None` |
| Pharmacy | `create_medicine(name, quantity, price, expiry_date)` | `int` |
| Pharmacy | `get_medicines()` | `list[Row]` |
| Pharmacy | `update_medicine(medicine_id, ...)` | `None` |
| Pharmacy | `delete_medicine(medicine_id)` | `None` |
| Pharmacy | `search_medicines(keyword)` | `list[Row]` |
| Billing | `create_bill(patient_id, amount, payment_status)` | `int` |
| Billing | `get_billing()` | `list[Row]` (with JOINed patient name) |
| Dashboard | `get_dashboard_stats()` | `dict[str, int\|float]` |

**Password Hashing:**
- Uses `bcrypt` if installed (recommended)
- Falls back to `sha256` (hashlib) if `bcrypt` is not available

---

### 4.3 `authentication/auth.py` — Authentication

**Class:** `AuthenticationPanel(ttk.Frame)`

Embeds inside the login card. Switches between Login and Register modes dynamically. Calls `on_authenticated(user_row)` callback on success.

---

### 4.4 `dashboard/dashboard.py` — Dashboard

**Class:** `DashboardView(ttk.Frame)`

Shows 5 stat cards: Total Patients, Total Doctors, Appointments Today, Revenue Today, Low Stock Alerts. Pulls data from `get_dashboard_stats()`.

---

### 4.5 `patients/patients.py` — Patients

**Class:** `PatientsView(ttk.Frame)`

Full CRUD for patient records. Features:
- Add / Edit form with Gender and Blood Group dropdowns
- Search by name, phone, or address
- CSV export via `filedialog.asksaveasfilename`
- Row click → auto-populates form for editing

---

### 4.6 `doctors/doctor.py` — Doctors

**Class:** `DoctorsView(ttk.Frame)`

Full CRUD for doctors. Features:
- Fields: Full Name, Specialization, Phone, Email
- Search by name, specialization, or email
- CSV export
- Alternating row colours (even/odd)
- Enter key triggers search

---

### 4.7 `appointments/appointment.py` — Appointments

**Class:** `AppointmentView(ttk.Frame)`

Full CRUD for appointments. Features:
- Fields: Patient ID, Doctor ID, Date, Time, Status
- Status dropdown: Scheduled / Completed / Cancelled / No-Show / Rescheduled
- Colour-coded status tags in the Treeview

---

### 4.8 `pharmacy/pharmacy.py` — Pharmacy

**Class:** `PharmacyView(ttk.Frame)`

Medicine inventory management. Features:
- Fields: Medicine Name, Quantity, Unit Price, Expiry Date
- Low-stock threshold: items with `quantity < 10` highlighted red
- Low-stock counter shown in the toolbar
- Warning shown in the form when editing a low-stock item
- Search and CSV export

---

### 4.9 `billing/billing.py` — Billing

**Class:** `BillingView(ttk.Frame)`

Patient billing records. Features:
- Fields: Patient ID, Amount, Payment Status (Pending/Paid/Partial/Waived)
- Colour-coded payment status (green = Paid, amber = Pending, etc.)
- Running total of collected revenue shown in the toolbar
- CSV export

---

### 4.10 `reports/reports.py` — Reports

**Class:** `ReportsView(ttk.Frame)`

Read-only analytics panel. Features:
- 5 coloured stat cards (same data as Dashboard)
- Full billing ledger with colour-coded payment status
- Summary line: total billed, collected, pending, record count
- Refresh button

---

### 4.11 `utils/theme.py` — ThemeManager

**Class:** `ThemeManager`

Manages light ↔ dark theme switching for all `ttk` widgets via `ttk.Style`. Called from `ClinicManagementApp._toggle_theme()`.

---

## 5. Database Schema

```sql
-- Users (clinic staff accounts)
CREATE TABLE IF NOT EXISTS users (
    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname      TEXT NOT NULL,
    username      TEXT UNIQUE NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    phone         TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL,          -- Administrator|Doctor|Nurse|Receptionist|Pharmacist
    date_created  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Patients
CREATE TABLE IF NOT EXISTS patients (
    patient_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname          TEXT NOT NULL,
    gender            TEXT NOT NULL,      -- Male|Female|Other
    age               INTEGER NOT NULL,
    phone             TEXT NOT NULL,
    address           TEXT NOT NULL,
    blood_group       TEXT NOT NULL,      -- A+|A-|B+|B-|AB+|AB-|O+|O-
    registration_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Doctors
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname       TEXT NOT NULL,
    specialization TEXT NOT NULL,
    phone          TEXT NOT NULL,
    email          TEXT NOT NULL
);

-- Appointments
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id       INTEGER NOT NULL REFERENCES patients(patient_id),
    doctor_id        INTEGER NOT NULL REFERENCES doctors(doctor_id),
    appointment_date TEXT NOT NULL,
    appointment_time TEXT NOT NULL,
    status           TEXT NOT NULL DEFAULT 'Scheduled'
);

-- Pharmacy / Medicine Inventory
CREATE TABLE IF NOT EXISTS pharmacy (
    medicine_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_name TEXT NOT NULL,
    quantity      INTEGER NOT NULL,
    price         REAL NOT NULL,
    expiry_date   TEXT NOT NULL
);

-- Billing
CREATE TABLE IF NOT EXISTS billing (
    bill_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id     INTEGER NOT NULL REFERENCES patients(patient_id),
    amount         REAL NOT NULL,
    payment_status TEXT NOT NULL DEFAULT 'Pending',
    payment_date   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. Data Flow

```
User Action (button click / form submit)
        │
        ▼
View method (e.g. PatientsView.save_patient())
        │  validates input
        ▼
ClinicDatabase method (e.g. create_patient(...))
        │  executes parameterised SQL
        ▼
SQLite WAL journal → clinic.db file
        │
        ▼
View.refresh() reloads from DB → Treeview updated
```

---

## 7. Structured Programming Principles

| Principle | Implementation |
|---|---|
| **Modularity** | Each feature is a separate sub-package with `__init__.py` |
| **Single Responsibility** | Views handle UI only; `ClinicDatabase` handles all SQL |
| **Sequence** | Validation → DB write → refresh — always in this order |
| **Selection** | `if/elif/else` in every `save_*()` to distinguish create vs update |
| **Iteration** | `for` loops populate Treeviews; `rglob` in tests |
| **Type Casting** | `int()` / `float()` on all numeric inputs, wrapped in `try/except` |
| **Error Handling** | `try/except ValueError` guards every numeric field |
| **Constants** | Colours, thresholds, status lists defined at module top |
| **Documentation** | Every class and method has a docstring |
| **Data Structures** | `dict` for patient records, `list[sqlite3.Row]` from DB |

---

## 8. Security Features

| Feature | Detail |
|---|---|
| Password hashing | `bcrypt` (if installed) or `sha256` fallback |
| Input validation | All fields validated before any DB write |
| Parameterised queries | No string formatting in SQL — eliminates SQL injection |
| Confirmation dialogs | All deletes require `messagebox.askyesno` |
| Role storage | Role stored in `users` table; used for future RBAC |
| Session-only data | SQLite file; no network exposure |

---

## 9. Testing

Run the test suite from the project root:

```bash
python -m pytest tests/ -v
```

**Test file:** `tests/test_clinic_system.py`

| Test | What it verifies |
|---|---|
| `test_database_round_trip` | Create patient → read back → assert name and ID match |
| `test_ui_modules_import` | All key classes import without error |

---

## 10. Future Enhancements

| Priority | Feature |
|---|---|
| High | Role-Based Access Control (restrict views by `user.role`) |
| High | Persistent session (remember-me token stored in file) |
| Medium | PDF report generation (ReportLab or WeasyPrint) |
| Medium | Patient Queue Tracker with triage priority |
| Medium | SMS notifications via Twilio API |
| Low | Cloud sync (REST API backend + SQLite mirror) |
| Low | Mobile companion app (Kivy or React Native) |
| Low | AI diagnosis assistant (LLM integration) |
