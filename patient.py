"""
Smarter Health Connection — Patient Management
================================================
Full CRUD operations for Patients.
"""

import tkinter as tk
from tkinter import ttk
from database import Database
from utils import C, F, PageHeader, FormCard, SHCEntry, SHCButton, make_treeview, populate_tree, ask_delete, msg_error, msg_ok


class PatientView(tk.Frame):
    def __init__(self, parent, db: Database):
        super().__init__(parent, bg=C["bg"])
        self.db = db

        PageHeader(self, "Patient Management", "Manage patient records").pack(fill="x", padx=20, pady=(20, 10))

        content = tk.Frame(self, bg=C["bg"])
        content.pack(fill="both", expand=True, padx=20, pady=10)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        # Form Variables
        self.pid_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.gender_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.blood_var = tk.StringVar()
        self.emg_var = tk.StringVar()
        self.search_var = tk.StringVar()

        self._build_form(content)
        self._build_table(content)

    def _build_form(self, parent):
        card = FormCard(parent, title="Patient Details")
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        def add_field(lbl, var, row, values=None):
            tk.Label(card, text=lbl, font=F["label"], bg=C["card"], fg=C["text"]).grid(row=row, column=0, sticky="w", pady=(5, 0))
            e = SHCEntry(card, var, values=values, width=30)
            e.grid(row=row+1, column=0, sticky="ew", pady=(0, 10))

        add_field("Full Name *", self.name_var, 0)
        add_field("Age *", self.age_var, 2)
        add_field("Gender *", self.gender_var, 4, values=["Male", "Female", "Other"])
        add_field("Phone *", self.phone_var, 6)
        add_field("Email", self.email_var, 8)
        add_field("Address *", self.address_var, 10)
        add_field("Blood Group", self.blood_var, 12, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"])
        add_field("Emergency Contact", self.emg_var, 14)

        btns = tk.Frame(card, bg=C["card"])
        btns.grid(row=16, column=0, pady=(15, 0), sticky="ew")
        SHCButton(btns, "Save", self._save, style="success", width=12).pack(side="left", padx=2)
        SHCButton(btns, "Clear", self._clear, style="secondary", width=12).pack(side="left", padx=2)
        SHCButton(btns, "Delete", self._delete, style="danger", width=12).pack(side="left", padx=2)

    def _build_table(self, parent):
        right = tk.Frame(parent, bg=C["bg"])
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        # Toolbar
        tb = tk.Frame(right, bg=C["bg"])
        tb.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        search_entry = SHCEntry(tb, self.search_var, icon="🔍", width=40)
        search_entry.pack(side="left")
        search_entry._widget.bind("<Return>", lambda e: self.refresh())
        SHCButton(tb, "Search", self.refresh, style="primary").pack(side="left", padx=5)

        # Table
        cols = ("patient_id", "fullname", "age", "gender", "phone", "address", "registration_date")
        widths = {"patient_id": 80, "fullname": 180, "age": 50, "gender": 80, "phone": 120, "address": 200, "registration_date": 140}
        
        self.tree_frame, self.tree = make_treeview(right, cols, col_widths=widths)
        self.tree_frame.grid(row=1, column=0, sticky="nsew")
        
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _clear(self):
        self.pid_var.set("")
        self.name_var.set("")
        self.age_var.set("")
        self.gender_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.address_var.set("")
        self.blood_var.set("Unknown")
        self.emg_var.set("")
        self.tree.selection_remove(self.tree.selection())

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])["values"]
        pid = item[0]
        
        row = self.db.get_patient(pid)
        if row:
            self.pid_var.set(row["patient_id"])
            self.name_var.set(row["fullname"])
            self.age_var.set(row["age"])
            self.gender_var.set(row["gender"])
            self.phone_var.set(row["phone"])
            self.email_var.set(row["email"])
            self.address_var.set(row["address"])
            self.blood_var.set(row["blood_group"])
            self.emg_var.set(row["emergency_contact"])

    def refresh(self):
        kw = self.search_var.get().strip()
        rows = self.db.get_patients(kw)
        populate_tree(self.tree, rows, ["patient_id", "fullname", "age", "gender", "phone", "address", "registration_date"])

    def _save(self):
        name = self.name_var.get().strip()
        age = self.age_var.get().strip()
        gender = self.gender_var.get().strip()
        phone = self.phone_var.get().strip()
        addr = self.address_var.get().strip()

        if not all([name, age, gender, phone, addr]):
            msg_error("Please fill all required fields (*).")
            return

        try:
            int(age)
        except ValueError:
            msg_error("Age must be a valid number.")
            return

        pid = self.pid_var.get()
        if pid:
            self.db.update_patient(
                int(pid), name, gender, age, phone, self.email_var.get().strip(),
                addr, self.blood_var.get().strip(), self.emg_var.get().strip()
            )
            msg_ok("Patient updated successfully.")
        else:
            self.db.create_patient(
                name, gender, age, phone, self.email_var.get().strip(),
                addr, self.blood_var.get().strip(), self.emg_var.get().strip()
            )
            msg_ok("Patient added successfully.")
        
        self._clear()
        self.refresh()

    def _delete(self):
        pid = self.pid_var.get()
        if not pid:
            msg_error("Please select a patient to delete.")
            return
        if ask_delete("this patient"):
            self.db.delete_patient(int(pid))
            self._clear()
            self.refresh()
            msg_ok("Patient deleted.")
