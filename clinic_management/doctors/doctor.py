"""
Doctors Management View
=======================
Full CRUD panel for managing physicians: add, edit, delete, search,
and export to CSV. Inherits from ttk.Frame for seamless embedding.
"""

from __future__ import annotations

import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class DoctorsView(ttk.Frame):
    """
    CRUD panel for Doctors.

    Layout
    ------
    Left column  : Form card (add / edit fields + action buttons)
    Right column : Toolbar (search, export) + Treeview table
    """

    def __init__(self, parent: tk.Misc, database) -> None:
        super().__init__(parent)
        self.database = database
        self.selected_doctor_id: int | None = None
        self._build_ui()
        self.refresh()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        # Page title
        ttk.Label(
            self,
            text="Doctor Management",
            font=("Segoe UI", 16, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        # Left: form card
        form = ttk.Frame(self, padding=16, style="Card.TFrame")
        form.grid(row=1, column=0, sticky="ns", padx=(0, 16))
        form.columnconfigure(0, weight=1)
        self._build_form(form)

        # Right: table area
        table_frame = ttk.Frame(self)
        table_frame.grid(row=1, column=1, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(1, weight=1)
        self._build_table(table_frame)

    def _build_form(self, parent: ttk.Frame) -> None:
        """Render the data-entry form inside *parent*."""
        ttk.Label(
            parent,
            text="Add / Edit Doctor",
            font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        # StringVars
        self.fullname_var    = tk.StringVar()
        self.specialty_var   = tk.StringVar()
        self.phone_var       = tk.StringVar()
        self.email_var       = tk.StringVar()

        field_defs = [
            ("Full Name",       self.fullname_var,  "entry"),
            ("Specialization",  self.specialty_var, "entry"),
            ("Phone",           self.phone_var,     "entry"),
            ("Email",           self.email_var,     "entry"),
        ]

        row = 1
        for label_text, var, widget_type in field_defs:
            ttk.Label(parent, text=label_text).grid(
                row=row, column=0, sticky="w", pady=(0, 2)
            )
            row += 1
            if widget_type == "entry":
                entry = ttk.Entry(parent, textvariable=var, width=26)
                entry.grid(row=row, column=0, sticky="ew", pady=(0, 10))
            row += 1

        # Action buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=row, column=0, sticky="ew", pady=(12, 0))

        ttk.Button(btn_frame, text="💾  Save",   command=self.save_doctor).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(btn_frame, text="✖  Clear",   command=self.clear_form).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(btn_frame, text="🗑  Delete",  command=self.delete_doctor).pack(
            side="left"
        )

    def _build_table(self, parent: ttk.Frame) -> None:
        """Render toolbar + Treeview table inside *parent*."""
        # Toolbar
        toolbar = ttk.Frame(parent)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=(0, 6))
        search_entry.bind("<Return>", lambda _e: self.search_doctors())

        ttk.Button(toolbar, text="🔍 Search",     command=self.search_doctors).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(toolbar, text="↺ Refresh",     command=self.refresh).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(toolbar, text="📤 Export CSV", command=self.export_doctors).pack(
            side="left"
        )

        # Treeview
        columns = ("doctor_id", "fullname", "specialization", "phone", "email")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=18)

        col_widths = {
            "doctor_id":      60,
            "fullname":      200,
            "specialization": 180,
            "phone":         120,
            "email":         200,
        }
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=col_widths.get(col, 120), anchor="w")

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.tag_configure("even", background="#f8fafc")

    # ── Data operations ───────────────────────────────────────────────────────

    def refresh(self) -> None:
        """Reload all doctor records from the database into the Treeview."""
        self._populate(self.database.get_doctors())

    def _populate(self, rows) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, doc in enumerate(rows):
            tag = "even" if i % 2 == 0 else ""
            self.tree.insert(
                "",
                "end",
                values=(
                    doc["doctor_id"],
                    doc["fullname"],
                    doc["specialization"],
                    doc["phone"],
                    doc["email"],
                ),
                tags=(tag,),
            )

    def save_doctor(self) -> None:
        """Validate inputs, then create or update the selected doctor."""
        fullname  = self.fullname_var.get().strip()
        specialty = self.specialty_var.get().strip()
        phone     = self.phone_var.get().strip()
        email     = self.email_var.get().strip()

        if not all([fullname, specialty, phone, email]):
            messagebox.showerror("Validation Error", "Please complete all doctor fields.")
            return

        if self.selected_doctor_id is None:
            self.database.create_doctor(fullname, specialty, phone, email)
            messagebox.showinfo("Success", f"Doctor '{fullname}' added successfully.")
        else:
            self.database.update_doctor(self.selected_doctor_id, fullname, specialty, phone, email)
            messagebox.showinfo("Success", f"Doctor '{fullname}' updated successfully.")

        self.clear_form()
        self.refresh()

    def clear_form(self) -> None:
        """Reset all form fields and deselect any tree selection."""
        self.fullname_var.set("")
        self.specialty_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.selected_doctor_id = None
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def on_select(self, _event: object = None) -> None:
        """Populate the form when the user clicks a row in the tree."""
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0], "values")
        self.selected_doctor_id  = values[0]
        self.fullname_var.set(values[1])
        self.specialty_var.set(values[2])
        self.phone_var.set(values[3])
        self.email_var.set(values[4])

    def delete_doctor(self) -> None:
        """Delete the currently selected doctor after confirmation."""
        if self.selected_doctor_id is None:
            messagebox.showwarning("No Selection", "Please select a doctor from the table first.")
            return
        name = self.fullname_var.get()
        if not messagebox.askyesno(
            "Confirm Delete", f"Permanently delete Dr. '{name}'?\nThis cannot be undone."
        ):
            return
        self.database.delete_doctor(self.selected_doctor_id)
        self.clear_form()
        self.refresh()

    def search_doctors(self) -> None:
        """Filter the table by keyword (name, specialization, or email)."""
        keyword = self.search_var.get().strip()
        if not keyword:
            self.refresh()
            return
        self._populate(self.database.search_doctors(keyword))

    def export_doctors(self) -> None:
        """Export the current doctor list to a CSV file."""
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile="doctors.csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        )
        if not path:
            return
        rows = self.database.get_doctors()
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["doctor_id", "fullname", "specialization", "phone", "email"])
            for doc in rows:
                writer.writerow(
                    [doc["doctor_id"], doc["fullname"], doc["specialization"], doc["phone"], doc["email"]]
                )
        messagebox.showinfo(
            "Export Complete", f"Exported {len(rows)} record(s) to '{os.path.basename(path)}'."
        )
