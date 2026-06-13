# ClinicCare Pro — Installation Guide

> **Estimated setup time:** 5 minutes | **Platform:** Windows 10 / 11

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.8 or higher | Download from python.org |
| Windows | 10 / 11 | macOS / Linux also supported |
| Disk Space | ~20 MB | For app + SQLite database |
| RAM | 512 MB minimum | 1 GB recommended |
| Display | 1024 × 660 minimum | 1280 × 780 recommended |

---

## Option A — Automated Setup (Recommended)

This is the fastest way to get started.

**Step 1:** Open File Explorer and navigate to the project folder:
```
c:\Users\Alice Bangura\Desktop\Structure Programming
```

**Step 2:** Double-click **`setup.bat`**

The script will:
1. ✅ Check that Python is installed
2. ✅ Create a virtual environment (`.venv`)
3. ✅ Install optional dependencies (Pillow, bcrypt)
4. ✅ Launch ClinicCare Pro automatically

**Default login credentials shown on screen:**
```
Username : admin
Password : admin123
```

---

## Option B — Manual Setup

### Step 1: Install Python

1. Go to **https://www.python.org/downloads/**
2. Download **Python 3.8 or higher** (latest stable recommended)
3. Run the installer
4. ⚠️ **Important:** Check **"Add Python to PATH"** during installation
5. Verify installation:
   ```powershell
   python --version
   ```
   Expected output: `Python 3.x.x`

---

### Step 2: Open a Terminal in the Project Folder

Option A — File Explorer:
1. Navigate to the project folder
2. Click the address bar, type `powershell`, press Enter

Option B — VS Code:
1. Open VS Code → File → Open Folder → select the project folder
2. Open Terminal → New Terminal

---

### Step 3: Create a Virtual Environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

You should see `(.venv)` at the start of your prompt.

---

### Step 4: Install Optional Dependencies

The core application has **no required third-party packages** (uses Python stdlib only). These are optional but recommended:

```powershell
pip install pillow bcrypt
```

| Package | Purpose |
|---|---|
| `pillow` | Image display (logos, icons) |
| `bcrypt` | Stronger password hashing |

---

### Step 5: Run the Application

```powershell
python main.py
```

Or double-click **`run.bat`** in File Explorer.

---

## Verifying the Installation

After launching, you should see:
1. A dark splash/login screen titled **"ClinicCare Pro"**
2. Login with `admin` / `admin123`
3. The main dashboard with 5 stat cards

---

## Running the Tests

```powershell
python -m pytest tests/ -v
```

Expected output:
```
tests/test_clinic_system.py::test_database_round_trip  PASSED
tests/test_clinic_system.py::test_ui_modules_import    PASSED
```

---

## Troubleshooting

### ❌ `python` is not recognised
- Python is not on your PATH.
- Re-run the Python installer and check **"Add Python to PATH"**.
- Or use the full path: `C:\Python3x\python.exe main.py`

### ❌ `ModuleNotFoundError: No module named 'tkinter'`
- Tkinter is not installed with your Python build.
- On Windows this is rare — reinstall Python from python.org and ensure the "tcl/tk" option is selected.

### ❌ App opens but shows errors / blank panels
- Make sure you are running from the project **root directory** (where `main.py` is).
- Do not run `python clinic_management/app.py` directly.

### ❌ Database errors on first run
- Delete `clinic_management/clinic.db` if it exists and re-run. The schema will be recreated automatically.

### ❌ `bcrypt` not found warning
- This is non-fatal. The app uses SHA-256 as a fallback. Install with `pip install bcrypt` for production use.

---

## File Locations After Setup

| File | Location |
|---|---|
| SQLite database | `clinic_management/clinic.db` |
| Application logs | Console / terminal output |
| CSV exports | Wherever you choose via the save dialog |

---

## Uninstalling

Simply delete the project folder. No registry entries or system files are modified.

---

*Last updated: June 2026 — ClinicCare Pro v2.0.0*
