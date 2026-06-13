"""
Smarter Health Connection — Doctor Management
================================================
Full CRUD operations for Doctors.
"""

import tkinter as tk
from tkinter import ttk
from database import Database
from utils import C, F, PageHeader, FormCard, SHCEntry, SHCButton, make_treeview, populate_tree, ask_delete, msg_error, msg_ok


class DoctorView(tk.Frame):
    def __init__(self, parent, db: Database):
        super().__init__(parent, bg=C["bg"])
        self.db = db

        PageHeader(self, "Doctor Management", "Manage physician profiles").pack(fill="x", padx=20, pady=(20, 10))

        content = tk.Frame(self, bg=C["bg"])
        content.pack(fill="both", expand=True, padx=20, pady=10)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self.did_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.spec_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.avail_var = tk.StringVar()
        self.license_var = tk.StringVar()
        self.search_var = tk.StringVar()

        self._build_form(content)
        self._build_table(content)

    def _build_form(self, parent):
        card = FormCard(parent, title="Doctor Details")
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        def add_field(lbl, var, row, values=None):
            tk.Label(card, text=lbl, font=F["label"], bg=C["card"], fg=C["text"]).grid(row=row, column=0, sticky="w", pady=(5, 0))
            e = SHCEntry(card, var, values=values, width=30)
            e.grid(row=row+1, column=0, sticky="ew", pady=(0, 10))

        add_field("Full Name *", self.name_var, 0)
        add_field("Specialization *", self.spec_var, 2)
        add_field("Phone *", self.phone_var, 4)
        add_field("Email *", self.email_var, 6)
        add_field("Availability *", self.avail_var, 8, values=["Available", "Unavailable", "On Leave"])
        add_field("License No.", self.license_var, 10)

        btns = tk.Frame(card, bg=C["card"])
        btns.grid(row=12, column=0, pady=(20, 0), sticky="ew")
        SHCButton(btns, "Save", self._save, style="success", width=12).pack(side="left", padx=2)
        SHCButton(btns, "Clear", self._clear, style="secondary", width=12).pack(side="left", padx=2)
        SHCButton(btns, "Delete", self._delete, style="danger", width=12).pack(side="left", padx=2)

    def _build_table(self, parent):
        right = tk.Frame(parent, bg=C["bg"])
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        tb = tk.Frame(right, bg=C["bg"])
        tb.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        search_entry = SHCEntry(tb, self.search_var, icon="🔍", width=40)
        search_entry.pack(side="left")
        search_entry._widget.bind("<Return>", lambda e: self.refresh())
        SHCButton(tb, "Search", self.refresh, style="primary").pack(side="left", padx=5)

        cols = ("doctor_id", "fullname", "specialization", "phone", "email", "availability")
        widths = {"doctor_id": 80, "fullname": 180, "specialization": 150, "phone": 120, "email": 180, "availability": 100}
        
        self.tree_frame, self.tree = make_treeview(right, cols, col_widths=widths)
        self.tree_frame.grid(row=1, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _clear(self):
        self.did_var.set("")
        self.name_var.set("")
        self.spec_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.avail_var.set("Available")
        self.license_var.set("")
        self.tree.selection_remove(self.tree.selection())

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])["values"]
        
        row = self.db.get_doctor(item[0])
        if row:
            self.did_var.set(row["doctor_id"])
            self.name_var.set(row["fullname"])
            self.spec_var.set(row["specialization"])
            self.phone_var.set(row["phone"])
            self.email_var.set(row["email"])
            self.avail_var.set(row["availability"])
            self.license_var.set(row["license_no"])

    def refresh(self):
        kw = self.search_var.get().strip()
        rows = self.db.get_doctors(kw)
        populate_tree(self.tree, rows, ["doctor_id", "fullname", "specialization", "phone", "email", "availability"])

    def _save(self):
        if not all([self.name_var.get(), self.spec_var.get(), self.phone_var.get(), self.email_var.get(), self.avail_var.get()]):
            msg_error("Please fill all required fields (*).")
            return

        did = self.did_var.get()
        if did:
            self.db.update_doctor(
                int(did), self.name_var.get(), self.spec_var.get(), self.phone_var.get(),
                self.email_var.get(), self.avail_var.get(), self.license_var.get()
            )
            msg_ok("Doctor updated successfully.")
        else:
            self.db.create_doctor(
                self.name_var.get(), self.spec_var.get(), self.phone_var.get(),
                self.email_var.get(), self.avail_var.get(), self.license_var.get()
            )
            msg_ok("Doctor added successfully.")
        
        self._clear()
        self.refresh()

    def _delete(self):
        did = self.did_var.get()
        if not did:
            msg_error("Please select a doctor to delete.")
            return
        if ask_delete("this doctor"):
            self.db.delete_doctor(int(did))
            self._clear()
            self.refresh()
            msg_ok("Doctor deleted.")
