"""Appointment Management View"""

from __future__ import annotations
import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class appointmentView(ttk.Frame):
    """CRUD Panel for Appointments."""
    def __init__(self, parents: tk.Misc, database) -> None:
        super().__init__(parents)
        self.database = database
        self.selected_appointment_id = None
        self._build_ui()
        self.refresh()
    def _build_ui(self) -> None:
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text="Appointment Management", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
        form = ttk.Frame(self, padding=12, style="Card.TFrame")
        form.grid(row=1, column=0, sticky="ns", padx=(0, 12))
        form.columnconfigure(0, weight=1)
        ttk.Label(form, text="Add or edit appointment", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.patient_id_var = tk.StringVar()
        self.doctor_id_var = tk.StringVar()
        self.date_var = tk.StringVar()
        
        fields = [
            ("Patient ID", self.patient_id_var),
            ("Doctor ID", self.doctor_id_var),
            ("Date", self.date_var),
            ("Time", self.time_var),
            ("Reason", self.reason_var),
            
        ]
        for index, (label_text, variable) in enumerate(fields):
            ttk.Label(form, text=label_text).grid(row=index + 1, column=0, sticky="w", pady=(0, 4))
            entry = ttk.Entry(form, textvariable=variable)
            entry.grid(row=index + 2, column=0, sticky="ew", pady=(0, 8))
        actions = ttk.Frame(form)
        actions.grid(row=10, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(actions, text="Save", command=self.save_appointment).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Clear", command=self.clear_form).pack(side="left", padx=(0, 6))