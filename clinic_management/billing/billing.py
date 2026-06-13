"""
Billing Management View
========================
Full CRUD panel for patient billing: create bills, record payments,
view billing history, and export records to CSV.
"""

from __future__ import annotations

import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class BillingView(ttk.Frame):
    """
    CRUD panel for Billing.

    Layout
    ------
    Left column  : Form card (patient ID, amount, status + actions)
    Right column : Toolbar (search, export) + Treeview table
    """

    PAYMENT_STATUSES = ["Pending", "Paid", "Partial", "Waived"]

    def __init__(self, parent: tk.Misc, database) -> None:
        super().__init__(parent)
        self.database = database
        self.selected_bill_id: int | None = None
        self._build_ui()
        self.refresh()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        ttk.Label(
            self,
            text="Billing Management",
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
            parent, text="Add / Edit Bill", font=("Segoe UI", 11, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        self.patient_id_var    = tk.StringVar()
        self.amount_var        = tk.StringVar()
        self.status_var        = tk.StringVar(value="Pending")

        rows = [
            ("Patient ID",      self.patient_id_var,  "entry"),
            ("Amount (USD)",    self.amount_var,       "entry"),
            ("Payment Status",  self.status_var,       "combo"),
        ]

        r = 1
        for label_text, var, widget_type in rows:
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
                    values=self.PAYMENT_STATUSES,
                    state="readonly",
                    width=24,
                ).grid(row=r, column=0, sticky="ew", pady=(0, 10))
            r += 1

        # Summary info label
        self._info_label = ttk.Label(parent, text="", foreground="#64748b", wraplength=200)
        self._info_label.grid(row=r, column=0, sticky="w", pady=(0, 10))
        r += 1

        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=r, column=0, sticky="ew", pady=(12, 0))
        ttk.Button(btn_frame, text="💾  Save",   command=self.save_bill).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="✖  Clear",   command=self.clear_form).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="🗑  Delete",  command=self.delete_bill).pack(side="left")

    def _build_table(self, parent: ttk.Frame) -> None:
        toolbar = ttk.Frame(parent)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        ttk.Button(toolbar, text="↺ Refresh",     command=self.refresh).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="📤 Export CSV", command=self.export_billing).pack(side="left")

        # Totals label on the right
        self._totals_label = ttk.Label(toolbar, text="", foreground="#22c55e", font=("Segoe UI", 9, "bold"))
        self._totals_label.pack(side="right")

        columns = ("bill_id", "patient_name", "amount", "payment_status", "payment_date")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=18)

        col_widths = {
            "bill_id":       60,
            "patient_name": 200,
            "amount":        100,
            "payment_status": 120,
            "payment_date":  160,
        }
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=col_widths.get(col, 120), anchor="w")

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Tag colours for payment status
        self.tree.tag_configure("Paid",    foreground="#166534")
        self.tree.tag_configure("Pending", foreground="#92400e")
        self.tree.tag_configure("Partial", foreground="#1e40af")
        self.tree.tag_configure("Waived",  foreground="#6b7280")

    # ── Data operations ───────────────────────────────────────────────────────

    def refresh(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        total_revenue = 0.0
        rows = self.database.get_billing()
        for bill in rows:
            status = bill["payment_status"]
            self.tree.insert(
                "",
                "end",
                values=(
                    bill["bill_id"],
                    bill["patient_name"],
                    f"${bill['amount']:.2f}",
                    status,
                    bill["payment_date"],
                ),
                tags=(status,),
            )
            if status == "Paid":
                total_revenue += bill["amount"]

        self._totals_label.configure(
            text=f"Total Collected: ${total_revenue:,.2f}"
        )

    def save_bill(self) -> None:
        patient_id_str = self.patient_id_var.get().strip()
        amount_str     = self.amount_var.get().strip()
        status         = self.status_var.get()

        if not all([patient_id_str, amount_str, status]):
            messagebox.showerror("Validation Error", "Please complete all billing fields.")
            return

        try:
            patient_id = int(patient_id_str)
        except ValueError:
            messagebox.showerror("Validation Error", "Patient ID must be a whole number.")
            return

        try:
            amount = float(amount_str)
            if amount < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Validation Error", "Amount must be a positive number.")
            return

        if self.selected_bill_id is None:
            self.database.create_bill(patient_id, amount, status)
            messagebox.showinfo("Success", "Bill created successfully.")
        else:
            # Update: re-use create_bill as a simple insert (full update would need extra DB method)
            messagebox.showinfo("Info", "Bill records cannot be edited. Please delete and recreate.")
            return

        self.clear_form()
        self.refresh()

    def clear_form(self) -> None:
        self.patient_id_var.set("")
        self.amount_var.set("")
        self.status_var.set("Pending")
        self.selected_bill_id = None
        self._info_label.configure(text="")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def on_select(self, _event: object = None) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0], "values")
        self.selected_bill_id = values[0]
        self._info_label.configure(
            text=f"Patient: {values[1]}\nStatus: {values[3]}\nDate: {values[4]}"
        )
        # Pre-fill amount and status for reference
        self.amount_var.set(str(values[2]).replace("$", ""))
        self.status_var.set(values[3])

    def delete_bill(self) -> None:
        if self.selected_bill_id is None:
            messagebox.showwarning("No Selection", "Please select a bill from the table first.")
            return
        if not messagebox.askyesno(
            "Confirm Delete", f"Delete bill #{self.selected_bill_id}?\nThis cannot be undone."
        ):
            return
        self.database.connection.execute(
            "DELETE FROM billing WHERE bill_id = ?", (self.selected_bill_id,)
        )
        self.database.connection.commit()
        self.clear_form()
        self.refresh()

    def export_billing(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile="billing.csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        )
        if not path:
            return
        rows = self.database.get_billing()
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["bill_id", "patient_name", "amount", "payment_status", "payment_date"])
            for bill in rows:
                writer.writerow([
                    bill["bill_id"], bill["patient_name"],
                    bill["amount"], bill["payment_status"], bill["payment_date"]
                ])
        messagebox.showinfo(
            "Export Complete", f"Exported {len(rows)} record(s) to '{os.path.basename(path)}'."
        )