"""
Smarter Health Connection — Pharmacy Management
=================================================
Full CRUD operations for Medicine Inventory.
"""

import tkinter as tk
from tkinter import ttk
from database import Database
from utils import C, F, PageHeader, FormCard, SHCEntry, SHCButton, make_treeview, populate_tree, ask_delete, msg_error, msg_ok


class PharmacyView(tk.Frame):
    def __init__(self, parent, db: Database):
        super().__init__(parent, bg=C["bg"])
        self.db = db

        PageHeader(self, "Pharmacy Management", "Manage medicine inventory and stock").pack(fill="x", padx=20, pady=(20, 10))

        content = tk.Frame(self, bg=C["bg"])
        content.pack(fill="both", expand=True, padx=20, pady=10)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self.mid_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.cat_var = tk.StringVar()
        self.qty_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.expiry_var = tk.StringVar()
        self.sup_var = tk.StringVar()
        self.search_var = tk.StringVar()

        self._build_form(content)
        self._build_table(content)

    def _build_form(self, parent):
        card = FormCard(parent, title="Medicine Details")
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        def add_field(lbl, var, row, values=None):
            tk.Label(card, text=lbl, font=F["label"], bg=C["card"], fg=C["text"]).grid(row=row, column=0, sticky="w", pady=(5, 0))
            e = SHCEntry(card, var, values=values, width=30)
            e.grid(row=row+1, column=0, sticky="ew", pady=(0, 10))

        add_field("Medicine Name *", self.name_var, 0)
        add_field("Category *", self.cat_var, 2, values=["General", "Antibiotic", "Painkiller", "Syrup", "Injection"])
        add_field("Quantity in Stock *", self.qty_var, 4)
        add_field("Unit Price ($) *", self.price_var, 6)
        add_field("Expiry Date (YYYY-MM-DD) *", self.expiry_var, 8)
        add_field("Supplier", self.sup_var, 10)

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

        cols = ("medicine_id", "medicine_name", "category", "quantity", "unit_price", "expiry_date")
        widths = {"medicine_id": 80, "medicine_name": 180, "category": 120, "quantity": 80, "unit_price": 80, "expiry_date": 100}
        
        self.tree_frame, self.tree = make_treeview(right, cols, col_widths=widths)
        self.tree_frame.grid(row=1, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _clear(self):
        self.mid_var.set("")
        self.name_var.set("")
        self.cat_var.set("General")
        self.qty_var.set("")
        self.price_var.set("")
        self.expiry_var.set("")
        self.sup_var.set("")
        self.tree.selection_remove(self.tree.selection())

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])["values"]
        
        self.mid_var.set(item[0])
        self.name_var.set(item[1])
        self.cat_var.set(item[2])
        self.qty_var.set(item[3])
        self.price_var.set(item[4])
        self.expiry_var.set(item[5])

    def refresh(self):
        kw = self.search_var.get().strip()
        rows = self.db.get_medicines(kw)
        
        # Colorize low stock
        self.tree.delete(*self.tree.get_children())
        for i, row in enumerate(rows):
            tag = "danger" if row["quantity"] < 10 else ("even" if i % 2 == 0 else "odd")
            self.tree.insert("", "end", values=[row["medicine_id"], row["medicine_name"], row["category"], 
                                                row["quantity"], row["unit_price"], row["expiry_date"]], tags=(tag,))
        self.tree.tag_configure("danger", background="#FFEbee", foreground="#C62828")

    def _save(self):
        if not all([self.name_var.get(), self.qty_var.get(), self.price_var.get(), self.expiry_var.get()]):
            msg_error("Please fill all required fields (*).")
            return

        try:
            int(self.qty_var.get())
            float(self.price_var.get())
        except ValueError:
            msg_error("Quantity and Price must be valid numbers.")
            return

        mid = self.mid_var.get()
        if mid:
            self.db.update_medicine(
                int(mid), self.name_var.get(), self.cat_var.get(), self.qty_var.get(),
                self.price_var.get(), self.expiry_var.get(), self.sup_var.get()
            )
            msg_ok("Medicine updated.")
        else:
            self.db.create_medicine(
                self.name_var.get(), self.cat_var.get(), self.qty_var.get(),
                self.price_var.get(), self.expiry_var.get(), self.sup_var.get()
            )
            msg_ok("Medicine added.")
        
        self._clear()
        self.refresh()

    def _delete(self):
        mid = self.mid_var.get()
        if not mid:
            msg_error("Please select a medicine to delete.")
            return
        if ask_delete("this medicine"):
            self.db.delete_medicine(int(mid))
            self._clear()
            self.refresh()
            msg_ok("Medicine deleted.")
