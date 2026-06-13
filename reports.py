"""
Smarter Health Connection — Reports Module
============================================
Export capabilities.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import Database
from utils import C, F, PageHeader, FormCard, SHCButton, msg_ok, msg_error
import csv


class ReportsView(tk.Frame):
    def __init__(self, parent, db: Database):
        super().__init__(parent, bg=C["bg"])
        self.db = db

        PageHeader(self, "Reports & Analytics", "Export clinic data to CSV/Excel").pack(fill="x", padx=20, pady=(20, 10))

        content = tk.Frame(self, bg=C["bg"])
        content.pack(fill="both", expand=True, padx=20, pady=10)

        card = FormCard(content, title="Data Export")
        card.pack(anchor="nw")

        tk.Label(card, text="Select Module to Export:", font=F["label"], bg=C["card"], fg=C["text"]).pack(anchor="w", pady=(0, 10))

        self.module_var = tk.StringVar(value="Patients")
        modules = ["Patients", "Doctors", "Appointments", "Pharmacy", "Billing"]
        cb = ttk.Combobox(card, textvariable=self.module_var, values=modules, state="readonly", width=30, font=F["body"])
        cb.pack(anchor="w", pady=(0, 20))

        btns = tk.Frame(card, bg=C["card"])
        btns.pack(anchor="w")

        SHCButton(btns, "Export CSV (Excel)", self._export_csv, style="success", width=20).pack(side="left", padx=5)
        SHCButton(btns, "Export PDF", self._export_pdf, style="primary", width=20).pack(side="left", padx=5)

    def _export_csv(self):
        mod = self.module_var.get()
        
        if mod == "Patients":
            data = self.db.get_patients()
            cols = ["patient_id", "fullname", "age", "gender", "phone", "email", "address", "blood_group", "registration_date"]
        elif mod == "Doctors":
            data = self.db.get_doctors()
            cols = ["doctor_id", "fullname", "specialization", "phone", "email", "availability", "license_no"]
        elif mod == "Appointments":
            data = self.db.get_appointments()
            cols = ["appointment_id", "patient_name", "doctor_name", "appointment_date", "appointment_time", "status"]
        elif mod == "Pharmacy":
            data = self.db.get_medicines()
            cols = ["medicine_id", "medicine_name", "category", "quantity", "unit_price", "expiry_date", "supplier"]
        elif mod == "Billing":
            data = self.db.get_bills()
            cols = ["bill_id", "patient_name", "total_amount", "paid_amount", "payment_status", "created_at"]
        else:
            return

        if not data:
            msg_error(f"No {mod} data found to export.")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], title=f"Save {mod} Report")
        if not filepath:
            return

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                for row in data:
                    writer.writerow([row[c] for c in cols])
            msg_ok(f"{mod} data exported successfully to:\n{filepath}")
        except Exception as e:
            msg_error(f"Failed to export data: {e}")

    def _export_pdf(self):
        msg_ok("PDF Export functionality requires external libraries (e.g. ReportLab). Simulated export success.")
