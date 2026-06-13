# ClinicCare Pro — User Manual

> **Version:** 2.0.0 | For clinic receptionists, doctors, and administrators

---

## Getting Started

### Launching the Application

**Option 1 — Double-click** `run.bat` in the project folder.  
**Option 2 — Terminal:**
```powershell
python main.py
```

### Default Login

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `admin123` |

> ⚠️ Change the admin password immediately after your first login by registering a new administrator account.

---

## Application Layout

```
┌─────────────────────────────────────────────────────────────┐
│  🏥 ClinicCare Pro  ›  Dashboard          👤 Admin  [Logout]│  ← Header
├───────────┬─────────────────────────────────────────────────┤
│           │                                                  │
│ NAVIGATION│           Content Area                          │
│           │    (active module view shown here)              │
│ ⊞ Dashboard                                                 │
│ 🧑 Patients                                                  │
│ 👨‍⚕️ Doctors                                                   │
│ 📅 Appts                                                     │
│ 💊 Pharmacy                                                  │
│ 💳 Billing                                                   │
│ 📊 Reports                                                   │
│           │                                                  │
├───────────┴─────────────────────────────────────────────────┤
│ ● Connected  |  SQLite Database          Friday, 12 June … │  ← Status bar
└─────────────────────────────────────────────────────────────┘
```

---

## Login & Registration

### Logging In
1. Enter your **Username** and **Password**
2. Optionally check **"Remember me"** (session only)
3. Click **Login**

### Registering a New Account
1. Click the **Register** tab
2. Fill in: Full Name, Username, Email, Phone, Password, Confirm Password
3. Select a **Role** from the dropdown:
   - Administrator — full access
   - Doctor — clinical views
   - Nurse — patient and appointment views
   - Receptionist — registration and appointments
   - Pharmacist — pharmacy and billing
4. Click **Register**
5. Log in with your new credentials

### Forgot Password
Contact the system administrator — they can create a new account for you.

---

## Dashboard

The Dashboard is the first screen after login. It shows:

| Card | What it shows |
|---|---|
| Total Patients | All registered patients |
| Total Doctors | All registered doctors |
| Appointments Today | Appointments scheduled for today |
| Revenue Today | Sum of Paid bills created today |
| Low Stock Alerts | Medicines with fewer than 10 units |

---

## Managing Patients

Navigate to **Patients** in the sidebar.

### Adding a Patient
1. Fill in the **form on the left**:
   - Full Name *(required)*
   - Gender — select from dropdown: Male / Female / Other
   - Age *(required, whole number)*
   - Phone *(required)*
   - Address *(required)*
   - Blood Group — select from dropdown
2. Click **💾 Save**
3. Patient appears in the table on the right

### Editing a Patient
1. Click a patient row in the **table** — form auto-populates
2. Modify any field
3. Click **💾 Save** — record updated

### Deleting a Patient
1. Select the patient row
2. Click **🗑 Delete**
3. Confirm in the dialog

### Searching Patients
1. Type a name, phone number, or address in the search box
2. Click **🔍 Search** or press **Enter**
3. Click **↺ Refresh** to show all patients again

### Exporting to CSV
1. Click **📤 Export CSV**
2. Choose a save location
3. File is saved as `patients.csv`

---

## Managing Doctors

Navigate to **Doctors** in the sidebar.

### Fields
| Field | Description |
|---|---|
| Full Name | Doctor's full legal name |
| Specialization | e.g., General Practice, Paediatrics, Surgery |
| Phone | Contact number |
| Email | Email address |

All CRUD operations (Add / Edit / Delete / Search / Export) work identically to the Patients module.

---

## Managing Appointments

Navigate to **Appointments** in the sidebar.

### Booking an Appointment
1. Enter the **Patient ID** (from the Patients table — column 1)
2. Enter the **Doctor ID** (from the Doctors table — column 1)
3. Enter the **Date** in format `YYYY-MM-DD` (e.g., `2026-07-15`)
4. Enter the **Time** in format `HH:MM` (e.g., `09:30`)
5. Select a **Status**: Scheduled (default)
6. Click **💾 Save**

### Appointment Statuses
| Status | Colour | Meaning |
|---|---|---|
| Scheduled | Blue | Upcoming appointment |
| Completed | Green | Patient was seen |
| Cancelled | Red | Appointment cancelled |
| No-Show | Amber | Patient did not attend |
| Rescheduled | Purple | Moved to another time |

### Updating an Appointment
1. Click the appointment row — date, time, and status populate the form
2. Change the status or timing
3. Click **💾 Save**

---

## Pharmacy — Medicine Inventory

Navigate to **Pharmacy** in the sidebar.

### Adding Medicine
1. Enter: Medicine Name, Quantity, Unit Price (USD), Expiry Date (`YYYY-MM-DD`)
2. Click **💾 Save**

### Low-Stock Alerts
- Medicines with **fewer than 10 units** are highlighted in **red**
- The toolbar shows a count: `⚠ 3 low-stock item(s)`
- When you click a low-stock item to edit it, a warning appears in the form

### Searching Medicine
Type a medicine name in the search box and click **🔍 Search**.

---

## Billing

Navigate to **Billing** in the sidebar.

### Creating a Bill
1. Enter the **Patient ID**
2. Enter the **Amount** (e.g., `45.00`)
3. Select a **Payment Status**:
   - Pending — payment not yet received
   - Paid — full payment received
   - Partial — part-payment received
   - Waived — bill waived (e.g., emergency relief)
4. Click **💾 Save**

### Revenue Tracker
The toolbar shows the **total collected** (sum of all Paid bills):
```
Total Collected: $1,250.00
```

### Deleting a Bill
Select a bill row, then click **🗑 Delete** and confirm.

---

## Reports & Analytics

Navigate to **Reports** in the sidebar.

This is a **read-only** panel showing:
1. **5 stat cards** — same as the Dashboard
2. **Full billing ledger** — all bills with colour-coded status
3. **Summary line** — total billed, collected, pending, and record count

Click **↺ Refresh** to reload the latest data.

---

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `F11` | Toggle fullscreen |
| `Escape` | Exit fullscreen |
| `Enter` (in search box) | Run search |

---

## Theme Toggle

Click **◑ Theme** in the header to switch between **light** and **dark** mode.

---

## Logout

Click **⇤ Logout** in the header. Confirm in the dialog. You will return to the login screen.

---

## Tips & Best Practices

1. **Record Patient IDs** before booking appointments — you'll need them in the Appointment form.
2. **Export regularly** — use CSV export to keep backups of patient and doctor records.
3. **Monitor Low Stock** — check the Pharmacy panel at the start of each clinic day.
4. **Mark Completed appointments** — update status after each consultation for accurate reporting.
5. **Use strong passwords** — register a personal admin account; do not share the default `admin` credentials.

---

*ClinicCare Pro v2.0.0 — Smarter Health Connection*  
*© 2026 — For educational and clinical use*
