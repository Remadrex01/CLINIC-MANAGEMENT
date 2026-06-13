"""Pharmarcy Management view"""

from __future__ import annotations
import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class pharmacyView(ttk.frame):
    
    """CRUD Panel for Pharmacy."""
    def __init__(self, parents: tk.Misc, database) -> None:
        super().__init__(parents)
        self.database = database
        self.selected_pharmacy_id = None
        self._build_ui()
        self.refresh()
    def _build_ui(self) -> None:
        self.column.configure(1, weight=1)
        ttk.Label(self, text="Pharmacy Management", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
        form = ttk.Frame(self, padding=12, style="Card.TFrame")
        form.grid(row=1, column=0, sticky="ns", padx=(0, 12))
        form.columnconfigure(0, weight=1)
        ttk.Label(form, text="Add or edit pharmacy", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.name_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        
        fields = [
            ("Name", self.name_var),
            ("Address", self.address_var),
            ("Phone", self.phone_var),
            ("Email", self.email_var),
            ("Opening Hours", self.opening_hours_var),
            
        ]
        for index, (label_text, variable) in enumerate(fields):
            ttk.Label(form, text=label_text).grid(row=index + 1, column=0, sticky="w", pady=(0, 4))
            entry = ttk.Entry(form, textvariable=variable)
            entry.grid(row=index + 2, column=0, sticky="ew", pady=(0, 8))
        actions = ttk.Frame(form)
        actions.grid(row=10, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(actions, text="Save", command=self.save_pharmacy).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Clear", command=self.clear_form).pack(side="left", padx=(0, 6))
    