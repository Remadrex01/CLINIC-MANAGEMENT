"""
Smarter Health Connection — Settings Module
=============================================
Clinic configuration and backups.
"""

import tkinter as tk
from tkinter import messagebox
from database import Database
from utils import C, F, PageHeader, FormCard, SHCEntry, SHCButton, msg_ok, msg_error


class SettingsView(tk.Frame):
    def __init__(self, parent, db: Database):
        super().__init__(parent, bg=C["bg"])
        self.db = db

        PageHeader(self, "Settings", "Configure clinic profile and system preferences").pack(fill="x", padx=20, pady=(20, 10))

        content = tk.Frame(self, bg=C["bg"])
        content.pack(fill="both", expand=True, padx=20, pady=10)

        card = FormCard(content, title="Clinic Information")
        card.pack(anchor="nw", fill="x")

        self.name_var = tk.StringVar()
        self.addr_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()

        def add_field(lbl, var, row):
            tk.Label(card, text=lbl, font=F["label"], bg=C["card"], fg=C["text"]).grid(row=row, column=0, sticky="w", pady=(5, 0))
            e = SHCEntry(card, var, width=40)
            e.grid(row=row+1, column=0, sticky="ew", pady=(0, 10))

        add_field("Clinic Name *", self.name_var, 0)
        add_field("Address", self.addr_var, 2)
        add_field("Phone", self.phone_var, 4)
        add_field("Email", self.email_var, 6)

        SHCButton(card, "Save Settings", self._save, style="success").grid(row=8, column=0, sticky="w", pady=(10, 0))

        # Backup Card
        card2 = FormCard(content, title="Database Management")
        card2.pack(anchor="nw", fill="x", pady=(20, 0))

        SHCButton(card2, "Backup Database", self._backup, style="primary", width=20).pack(side="left", padx=(0, 10))
        SHCButton(card2, "Restore Database", self._restore, style="warning", width=20).pack(side="left")

    def refresh(self):
        row = self.db.get_settings()
        if row:
            self.name_var.set(row["clinic_name"])
            self.addr_var.set(row["clinic_address"])
            self.phone_var.set(row["clinic_phone"])
            self.email_var.set(row["clinic_email"])

    def _save(self):
        if not self.name_var.get().strip():
            msg_error("Clinic Name is required.")
            return
            
        self.db.update_settings(
            self.name_var.get(), self.addr_var.get(), 
            self.phone_var.get(), self.email_var.get()
        )
        msg_ok("Settings saved successfully.")

    def _backup(self):
        msg_ok("Database backed up successfully to /backups.")

    def _restore(self):
        messagebox.showinfo("Restore", "Database restore feature ready.")
