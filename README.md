# ClinicCare Pro — Smarter Health Connection

> A professional desktop clinic management system built with Python, Tkinter, and SQLite.  
> Designed for peripheral health units in Sierra Leone — aligned with **SDG 3: Good Health and Well-being**.

---

## 🚀 Quick Start (30 seconds)

```powershell
# From the project folder:
python main.py
```

**Default login:** `admin` / `admin123`

Or double-click **`run.bat`** (Windows).

---

## ✨ Features

| Module | Capability |
|---|---|
| 🔐 Authentication | Login, Registration, Role-Based Access, Show/Hide Password |
| 📊 Dashboard | Live stat cards — Patients, Doctors, Appointments, Revenue, Low Stock |
| 🧑 Patients | Full CRUD, search by name/phone/address, CSV export |
| 👨‍⚕️ Doctors | Full CRUD, search by name/specialization/email, CSV export |
| 📅 Appointments | Book, edit, cancel; colour-coded status (Scheduled/Completed/Cancelled…) |
| 💊 Pharmacy | Medicine inventory, low-stock alerts (< 10 units), search, CSV export |
| 💳 Billing | Create bills, track payment status, live revenue totals, CSV export |
| 📊 Reports | Analytics panel — stat cards + full billing ledger with summary |

**UI Highlights:**
- 🌙 Light / Dark theme toggle
- ⌨️ F11 fullscreen, Escape exits fullscreen
- ⏱ Live clock in status bar
- Lazy navigation (views cached, never rebuilt on revisit)
- Colour-coded Treeview rows per status/priority

---

## 🗂 Project Structure

```
Structure Programming/
├── main.py                        ← Entry point (run this)
├── run.bat                        ← Windows one-click launcher
├── setup.bat                      ← First-time setup + launch
├── requirements.txt               ← Optional dependencies
│
├── clinic_management/
│   ├── app.py                     ← Main window (ClinicManagementApp)
│   ├── authentication/auth.py     ← Login + Register panel
│   ├── dashboard/dashboard.py     ← Overview stat cards
│   ├── patients/patients.py       ← Patient CRUD + CSV export
│   ├── doctors/doctor.py          ← Doctor CRUD + CSV export
│   ├── appointments/appointment.py← Appointment CRUD
│   ├── pharmacy/pharmacy.py       ← Medicine inventory + alerts
│   ├── billing/billing.py         ← Billing + payment tracking
│   ├── reports/reports.py         ← Analytics + billing ledger
│   ├── database/db.py             ← All SQL (ClinicDatabase class)
│   ├── database/schema.sql        ← SQLite schema
│   └── utils/theme.py             ← Light/dark ThemeManager
│
├── tests/
│   └── test_clinic_system.py      ← pytest test suite
│
└── docs/
    ├── DOCUMENTATION.md           ← Full technical reference
    ├── INSTALLATION_GUIDE.md      ← Step-by-step setup guide
    └── USER_MANUAL.md             ← End-user workflow guide
```

---

## 🛠 Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.8+ |
| GUI | Tkinter + ttk (stdlib — no install needed) |
| Database | SQLite 3 (stdlib — no install needed) |
| Password Hashing | bcrypt (optional) or sha256 fallback |
| Image Handling | Pillow (optional) |

**Zero mandatory external dependencies** — runs out of the box with any Python 3.8+ installation.

---

## 📋 System Requirements

| Requirement | Minimum |
|---|---|
| Python | 3.8+ |
| OS | Windows 10/11, macOS 12+, Ubuntu 20.04+ |
| RAM | 512 MB |
| Display | 1024 × 660 px |

---

## 🧪 Running Tests

```powershell
python -m pytest tests/ -v
```

---

## 📖 Documentation

| Document | Location |
|---|---|
| Installation Guide | [`docs/INSTALLATION_GUIDE.md`](docs/INSTALLATION_GUIDE.md) |
| User Manual | [`docs/USER_MANUAL.md`](docs/USER_MANUAL.md) |
| Technical Reference | [`docs/DOCUMENTATION.md`](docs/DOCUMENTATION.md) |

---

## 🎓 Academic Context

| Property | Value |
|---|---|
| Degree | Bachelor of Science — Computer Science / IT |
| Course | Structured Programming / Software Engineering |
| Academic Year | 2025 / 2026 |
| SDG Alignment | SDG 3 — Good Health and Well-being |
| Country Context | Sierra Leone — Peripheral Health Units |

### Structured Programming Principles Demonstrated

1. **Modularity** — each feature is a separate Python sub-package
2. **Single Responsibility** — views handle UI; `ClinicDatabase` handles all SQL
3. **Selection** — `if/elif/else` in every `save_*()` for create vs update
4. **Iteration** — `for` loops populate all Treeview tables
5. **Type Casting** — `int()` / `float()` with `try/except` on all inputs
6. **Error Handling** — `try/except` + `messagebox.showerror` feedback
7. **Constants** — colours, thresholds, status lists at module top
8. **Documentation** — docstrings on every class and method
9. **Data Structures** — `dict` for records, `list[sqlite3.Row]` from DB

---

## 🔐 Default Credentials

| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | Administrator |

Change the default password after first login.

---

## 📄 License

MIT License — see [`LICENSE`](LICENSE) for details.

---

**Version:** 2.0.0 | **Last Updated:** June 2026 | **Status:** ✅ Production Ready
