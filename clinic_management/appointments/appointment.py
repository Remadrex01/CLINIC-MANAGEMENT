"""
Appointment Management View
============================
Full CRUD panel for managing patient appointments:
book, edit, cancel, and view scheduled appointments.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


class AppointmentView(ttk.Frame):
    """
    CRUD panel for Appointments.

    Layout
    ------
    Left column  : Form card (patient, doctor, date, time, status)
    Right column : Toolbar + Treeview
    """

    STATUSES = ["Scheduled", "Completed", "Cancelled", "No-Show", "Rescheduled"]

    def __init__(self, parent: tk.Misc, database) -> None:
        super().__init__(parent)
        self.database = database
        self.selected_appointment_id: int | None = None
        self._build_ui()
        self.refresh()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        ttk.Label(
            self,
            text="Appointment Management",
            font=("Segoe UI", 16, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        form = ttk.Frame(self, padding=16, style="Card.TFrame")
        form.grid(row=1, column=0, sticky="ns", padx=(0, 16))
        form.columnconfigure(0, weight=1)
        self._build_form(form)

        table_frame = ttk.Frame(self)
        table_frame.grid(row=1, column=1, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(1, weight=1)
        self._build_table(table_frame)

    def _build_form(self, parent: ttk.Frame) -> None:
        ttk.Label(
            parent, text="Book / Edit Appointment", font=("Segoe UI", 11, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        # StringVars — all defined before the field loop
        self.patient_id_var = tk.StringVar()
        self.doctor_id_var  = tk.StringVar()
        self.date_var       = tk.StringVar()
        self.time_var       = tk.StringVar()
        self.status_var     = tk.StringVar(value="Scheduled")

        fields = [
            ("Patient ID",        self.patient_id_var, "entry"),
            ("Doctor ID",         self.doctor_id_var,  "entry"),
            ("Date (YYYY-MM-DD)", self.date_var,        "entry"),
            ("Time (HH:MM)",      self.time_var,        "entry"),
            ("Status",            self.status_var,      "combo"),
        ]

        r = 1
        for label_text, var, widget_type in fields:
            ttk.Label(parent, text=label_text).grid(row=r, column=0, sticky="w", pady=(0, 2))
            r += 1
            if widget_type == "entry":
                ttk.Entry(parent, textvariable=var, width=26).grid(
                    row=r, column=0, sticky="ew", pady=(0, 10)
                )
            else:
                ttk.Combobox(
                    parent,
                    textvariable=var,
                    values=self.STATUSES,
                    state="readonly",
                    width=24,
                ).grid(row=r, column=0, sticky="ew", pady=(0, 10))
            r += 1

        # Hint label
        ttk.Label(
            parent,
            text="Tip: Select a row to edit it.",
            foreground="#94a3b8",
            font=("Segoe UI", 8),
        ).grid(row=r, column=0, sticky="w")
        r += 1

        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=r, column=0, sticky="ew", pady=(16, 0))
        ttk.Button(btn_frame, text="💾  Save",   command=self.save_appointment).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="✖  Clear",   command=self.clear_form).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="🗑  Delete",  command=self.delete_appointment).pack(side="left")

    def _build_table(self, parent: ttk.Frame) -> None:
        toolbar = ttk.Frame(parent)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        ttk.Button(toolbar, text="↺ Refresh", command=self.refresh).pack(side="left", padx=(0, 6))

        columns = (
            "appointment_id", "patient_name", "doctor_name",
            "appointment_date", "appointment_time", "status",
        )
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=18)

        col_widths = {
            "appointment_id":   60,
            "patient_name":    180,
            "doctor_name":     180,
            "appointment_date": 120,
            "appointment_time": 100,
            "status":          120,
        }
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=col_widths.get(col, 120), anchor="w")

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Status colour coding
        self.tree.tag_configure("Scheduled",   foreground="#1e40af")
        self.tree.tag_configure("Completed",   foreground="#166534")
        self.tree.tag_configure("Cancelled",   foreground="#991b1b")
        self.tree.tag_configure("No-Show",     foreground="#92400e")
        self.tree.tag_configure("Rescheduled", foreground="#6b21a8")

    # ── Data operations ───────────────────────────────────────────────────────

    def refresh(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for appt in self.database.get_appointments():
            status = appt["status"]
            self.tree.insert(
                "",
                "end",
                values=(
                    appt["appointment_id"],
                    appt["patient_name"],
                    appt["doctor_name"],
                    appt["appointment_date"],
                    appt["appointment_time"],
                    status,
                ),
                tags=(status,),
            )

    def save_appointment(self) -> None:
        patient_id_str = self.patient_id_var.get().strip()
        doctor_id_str  = self.doctor_id_var.get().strip()
        date           = self.date_var.get().strip()
        time           = self.time_var.get().strip()
        status         = self.status_var.get()

        if not all([patient_id_str, doctor_id_str, date, time, status]):
            messagebox.showerror("Validation Error", "Please complete all appointment fields.")
            return

        try:
            patient_id = int(patient_id_str)
            doctor_id  = int(doctor_id_str)
        except ValueError:
            messagebox.showerror("Validation Error", "Patient ID and Doctor ID must be whole numbers.")
            return

        if self.selected_appointment_id is None:
            self.database.create_appointment(patient_id, doctor_id, date, time, status)
            messagebox.showinfo("Success", "Appointment booked successfully.")
        else:
            self.database.update_appointment(
                self.selected_appointment_id, patient_id, doctor_id, date, time, status
            )
            messagebox.showinfo("Success", "Appointment updated successfully.")

        self.clear_form()
        self.refresh()

    def clear_form(self) -> None:
        self.patient_id_var.set("")
        self.doctor_id_var.set("")
        self.date_var.set("")
        self.time_var.set("")
        self.status_var.set("Scheduled")
        self.selected_appointment_id = None
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def on_select(self, _event: object = None) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0], "values")
        self.selected_appointment_id = values[0]
        # We only have patient_name and doctor_name in the tree, not IDs
        # Set date, time, status which are directly editable
        self.date_var.set(values[3])
        self.time_var.set(values[4])
        self.status_var.set(values[5])

    def delete_appointment(self) -> None:
        if self.selected_appointment_id is None:
            messagebox.showwarning("No Selection", "Please select an appointment from the table first.")
            return
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Delete appointment #{self.selected_appointment_id}?\nThis cannot be undone.",
        ):
            return
        self.database.delete_appointment(self.selected_appointment_id)
        self.clear_form()
        self.refresh()
