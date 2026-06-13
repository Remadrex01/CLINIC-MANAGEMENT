"""Patient management view."""

from __future__ import annotations

import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class PatientsView(ttk.Frame):
    """CRUD panel for patients."""

    def __init__(self, parent: tk.Misc, database) -> None:
        super().__init__(parent)
        self.database = database
        self.selected_patient_id = None
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text="Patient Management", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        form = ttk.Frame(self, padding=12, style="Card.TFrame")
        form.grid(row=1, column=0, sticky="ns", padx=(0, 12))
        form.columnconfigure(0, weight=1)
        ttk.Label(form, text="Add or edit patient", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.fullname_var = tk.StringVar()
        self.gender_var = tk.StringVar(value="Male")
        self.age_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.blood_var = tk.StringVar(value="O+")

        fields = [
            ("Full Name", self.fullname_var),
            ("Gender", self.gender_var),
            ("Age", self.age_var),
            ("Phone", self.phone_var),
            ("Address", self.address_var),
            ("Blood Group", self.blood_var),
        ]
        for index, (label_text, variable) in enumerate(fields):
            ttk.Label(form, text=label_text).grid(row=index + 1, column=0, sticky="w", pady=(0, 4))
            if label_text == "Gender":
                combo = ttk.Combobox(form, textvariable=variable, values=["Male", "Female", "Other"], state="readonly")
                combo.grid(row=index + 2, column=0, sticky="ew", pady=(0, 8))
            elif label_text == "Blood Group":
                combo = ttk.Combobox(form, textvariable=variable, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], state="readonly")
                combo.grid(row=index + 2, column=0, sticky="ew", pady=(0, 8))
            else:
                entry = ttk.Entry(form, textvariable=variable)
                entry.grid(row=index + 2, column=0, sticky="ew", pady=(0, 8))

        actions = ttk.Frame(form)
        actions.grid(row=14, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(actions, text="Save", command=self.save_patient).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Clear", command=self.clear_form).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Delete", command=self.delete_patient).pack(side="left")

        content = ttk.Frame(self)
        content.grid(row=1, column=1, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(content)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.search_var = tk.StringVar()
        ttk.Entry(toolbar, textvariable=self.search_var).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(toolbar, text="Search", command=self.search_patients).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="Export CSV", command=self.export_patients).pack(side="left")

        columns = ("patient_id", "fullname", "gender", "age", "phone", "address", "blood_group")
        self.tree = ttk.Treeview(content, columns=columns, show="headings", height=14)
        for column in columns:
            self.tree.heading(column, text=column.replace("_", " ").title())
            self.tree.column(column, width=110, anchor="w")
        self.tree.grid(row=1, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def refresh(self) -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)
        for patient in self.database.get_patients():
            self.tree.insert("", "end", values=(patient["patient_id"], patient["fullname"], patient["gender"], patient["age"], patient["phone"], patient["address"], patient["blood_group"]))

    def save_patient(self) -> None:
        fullname = self.fullname_var.get().strip()
        gender = self.gender_var.get()
        age = self.age_var.get().strip()
        phone = self.phone_var.get().strip()
        address = self.address_var.get().strip()
        blood_group = self.blood_var.get()
        if not all([fullname, gender, age, phone, address, blood_group]):
            messagebox.showerror("Validation", "Please complete all patient fields")
            return
        if self.selected_patient_id is None:
            self.database.create_patient(fullname, gender, int(age), phone, address, blood_group)
            messagebox.showinfo("Success", "Patient added")
        else:
            self.database.update_patient(self.selected_patient_id, fullname, gender, int(age), phone, address, blood_group)
            messagebox.showinfo("Success", "Patient updated")
        self.clear_form()
        self.refresh()

    def clear_form(self) -> None:
        self.fullname_var.set("")
        self.gender_var.set("Male")
        self.age_var.set("")
        self.phone_var.set("")
        self.address_var.set("")
        self.blood_var.set("O+")
        self.selected_patient_id = None

    def on_select(self, event) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0], "values")
        self.selected_patient_id = values[0]
        self.fullname_var.set(values[1])
        self.gender_var.set(values[2])
        self.age_var.set(values[3])
        self.phone_var.set(values[4])
        self.address_var.set(values[5])
        self.blood_var.set(values[6])

    def delete_patient(self) -> None:
        if self.selected_patient_id is None:
            messagebox.showwarning("Select patient", "Choose a patient from the list first")
            return
        self.database.delete_patient(self.selected_patient_id)
        self.clear_form()
        self.refresh()

    def search_patients(self) -> None:
        keyword = self.search_var.get().strip()
        for row in self.tree.get_children():
            self.tree.delete(row)
        for patient in self.database.search_patients(keyword):
            self.tree.insert("", "end", values=(patient["patient_id"], patient["fullname"], patient["gender"], patient["age"], patient["phone"], patient["address"], patient["blood_group"]))

    def export_patients(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="patients.csv")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["patient_id", "fullname", "gender", "age", "phone", "address", "blood_group"])
            for patient in self.database.get_patients():
                writer.writerow([patient["patient_id"], patient["fullname"], patient["gender"], patient["age"], patient["phone"], patient["address"], patient["blood_group"]])
        messagebox.showinfo("Export complete", f"Patient records exported to {os.path.basename(path)}")
