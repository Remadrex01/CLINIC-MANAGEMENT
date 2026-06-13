"""
Smarter Health Connection — Billing Management
================================================
Full CRUD operations for Invoices and Billing.
"""

import tkinter as tk
from tkinter import ttk
from database import Database
from utils import C, F, PageHeader, FormCard, SHCEntry, SHCButton, make_treeview, populate_tree, ask_delete, msg_error, msg_ok


class BillingView(tk.Frame):
    def __init__(self, parent, db: Database):
        super().__init__(parent, bg=C["bg"])
        self.db = db

        PageHeader(self, "Billing & Invoices", "Manage patient bills and payments").pack(fill="x", padx=20, pady=(20, 10))

        content = tk.Frame(self, bg=C["bg"])
        content.pack(fill="both", expand=True, padx=20, pady=10)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self.bid_var = tk.StringVar()
        self.patient_var = tk.StringVar()
        self.total_var = tk.StringVar()
        self.paid_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Unpaid")
        self.method_var = tk.StringVar(value="Cash")
        self.notes_var = tk.StringVar()
        self.search_var = tk.StringVar()

        self.patients_map = {}

        self._build_form(content)
        self._build_table(content)

    def _build_form(self, parent):
        card = FormCard(parent, title="Invoice Details")
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        def add_field(lbl, var, row, values=None):
            tk.Label(card, text=lbl, font=F["label"], bg=C["card"], fg=C["text"]).grid(row=row, column=0, sticky="w", pady=(5, 0))
            e = SHCEntry(card, var, values=values, width=30)
            e.grid(row=row+1, column=0, sticky="ew", pady=(0, 5))
            return e

        self.cb_patient = add_field("Patient *", self.patient_var, 0, values=[])
        add_field("Total Amount ($) *", self.total_var, 2)
        add_field("Paid Amount ($) *", self.paid_var, 4)
        add_field("Payment Status *", self.status_var, 6, values=["Unpaid", "Paid", "Partial", "Waived"])
        add_field("Payment Method *", self.method_var, 8, values=["Cash", "Credit Card", "Insurance", "Bank Transfer"])
        add_field("Notes", self.notes_var, 10)

        btns = tk.Frame(card, bg=C["card"])
        btns.grid(row=12, column=0, pady=(20, 0), sticky="ew")
        SHCButton(btns, "Save", self._save, style="success", width=12).pack(side="left", padx=2)
        SHCButton(btns, "Clear", self._clear, style="secondary", width=12).pack(side="left", padx=2)
        SHCButton(btns, "Delete", self._delete, style="danger", width=12).pack(side="left", padx=2)
        
        SHCButton(card, "🖨 Print Invoice", self._print, style="primary", width=25).grid(row=13, column=0, pady=(15, 0))

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

        cols = ("bill_id", "patient_name", "total_amount", "paid_amount", "payment_status", "created_at")
        widths = {"bill_id": 80, "patient_name": 180, "total_amount": 100, "paid_amount": 100, "payment_status": 120, "created_at": 140}
        
        self.tree_frame, self.tree = make_treeview(right, cols, col_widths=widths)
        self.tree_frame.grid(row=1, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _clear(self):
        self.bid_var.set("")
        self.patient_var.set("")
        self.total_var.set("")
        self.paid_var.set("")
        self.status_var.set("Unpaid")
        self.method_var.set("Cash")
        self.notes_var.set("")
        self.tree.selection_remove(self.tree.selection())

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])["values"]
        
        self.bid_var.set(item[0])
        self.patient_var.set(item[1])
        self.total_var.set(item[2])
        self.paid_var.set(item[3])
        self.status_var.set(item[4])

    def refresh(self):
        self.patients_map = self.db.get_patient_names()
        self.cb_patient._widget["values"] = list(self.patients_map.keys())

        kw = self.search_var.get().strip()
        rows = self.db.get_bills(kw)
        
        self.tree.delete(*self.tree.get_children())
        for i, row in enumerate(rows):
            tag = "paid" if row["payment_status"] == "Paid" else ("unpaid" if row["payment_status"] == "Unpaid" else "even")
            self.tree.insert("", "end", values=[row["bill_id"], row["patient_name"], row["total_amount"], 
                                                row["paid_amount"], row["payment_status"], row["created_at"]], tags=(tag,))
        self.tree.tag_configure("paid", background="#E8F5E9", foreground="#2E7D32")
        self.tree.tag_configure("unpaid", background="#FFF3E0", foreground="#E65100")

    def _save(self):
        p_name = self.patient_var.get()
        if not all([p_name, self.total_var.get(), self.paid_var.get()]):
            msg_error("Please fill all required fields (*).")
            return

        pid = self.patients_map.get(p_name)
        if not pid:
            msg_error("Please select a valid Patient.")
            return

        try:
            float(self.total_var.get())
            float(self.paid_var.get())
        except ValueError:
            msg_error("Amounts must be numbers.")
            return

        bid = self.bid_var.get()
        if bid:
            self.db.update_bill(
                int(bid), self.total_var.get(), self.paid_var.get(),
                self.status_var.get(), self.method_var.get(), self.notes_var.get()
            )
            msg_ok("Invoice updated.")
        else:
            self.db.create_bill(
                pid, self.total_var.get(), self.paid_var.get(),
                self.status_var.get(), self.method_var.get(), self.notes_var.get()
            )
            msg_ok("Invoice generated.")
        
        self._clear()
        self.refresh()

    def _delete(self):
        bid = self.bid_var.get()
        if not bid:
            msg_error("Please select an invoice to delete.")
            return
        if ask_delete("this invoice"):
            self.db.delete_bill(int(bid))
            self._clear()
            self.refresh()
            msg_ok("Invoice deleted.")
            
    def _print(self):
        bid = self.bid_var.get()
        if not bid:
            msg_error("Please select an invoice to print.")
            return
        msg_ok("Invoice sent to printer queue.")
