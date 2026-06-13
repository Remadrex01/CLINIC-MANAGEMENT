"""
Pharmacy (Medicine Inventory) Management View
=============================================
Full CRUD panel for managing medicine stock: add, edit, delete, search,
and export. Highlights low-stock items automatically.
"""

from __future__ import annotations

import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

LOW_STOCK_THRESHOLD = 10  # items below this quantity are flagged


class PharmacyView(ttk.Frame):
    """
    CRUD panel for the Medicine / Pharmacy Inventory.

    Layout
    ------
    Left column  : Form card (medicine_name, quantity, price, expiry_date)
    Right column : Toolbar (search, export) + Treeview table
    """

    def __init__(self, parent: tk.Misc, database) -> None:
        super().__init__(parent)
        self.database = database
        self.selected_medicine_id: int | None = None
        self._build_ui()
        self.refresh()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        ttk.Label(
            self,
            text="Pharmacy — Medicine Inventory",
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
            parent, text="Add / Edit Medicine", font=("Segoe UI", 11, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        # StringVars — all defined before the field loop
        self.medicine_name_var = tk.StringVar()
        self.quantity_var      = tk.StringVar()
        self.price_var         = tk.StringVar()
        self.expiry_date_var   = tk.StringVar()

        fields = [
            ("Medicine Name",         self.medicine_name_var, "entry"),
            ("Quantity (units)",      self.quantity_var,      "entry"),
            ("Unit Price (USD)",      self.price_var,         "entry"),
            ("Expiry Date (YYYY-MM-DD)", self.expiry_date_var, "entry"),
        ]

        r = 1
        for label_text, var, _ in fields:
            ttk.Label(parent, text=label_text).grid(row=r, column=0, sticky="w", pady=(0, 2))
            r += 1
            ttk.Entry(parent, textvariable=var, width=26).grid(
                row=r, column=0, sticky="ew", pady=(0, 10)
            )
            r += 1

        # Low-stock warning label
        self._stock_label = ttk.Label(parent, text="", foreground="#ef4444", wraplength=200)
        self._stock_label.grid(row=r, column=0, sticky="w", pady=(0, 6))
        r += 1

        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=r, column=0, sticky="ew", pady=(12, 0))
        ttk.Button(btn_frame, text="💾  Save",   command=self.save_medicine).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="✖  Clear",   command=self.clear_form).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="🗑  Delete",  command=self.delete_medicine).pack(side="left")

    def _build_table(self, parent: ttk.Frame) -> None:
        toolbar = ttk.Frame(parent)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=28)
        search_entry.pack(side="left", padx=(0, 6))
        search_entry.bind("<Return>", lambda _e: self.search_medicines())

        ttk.Button(toolbar, text="🔍 Search",     command=self.search_medicines).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="↺ Refresh",     command=self.refresh).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="📤 Export CSV", command=self.export_medicines).pack(side="left")

        # Low stock counter
        self._low_stock_label = ttk.Label(
            toolbar, text="", foreground="#ef4444", font=("Segoe UI", 9, "bold")
        )
        self._low_stock_label.pack(side="right")

        columns = ("medicine_id", "medicine_name", "quantity", "price", "expiry_date")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=18)

        col_widths = {
            "medicine_id":   60,
            "medicine_name": 220,
            "quantity":       80,
            "price":         100,
            "expiry_date":   130,
        }
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=col_widths.get(col, 120), anchor="w")

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.tree.tag_configure("low_stock", background="#fef2f2", foreground="#991b1b")
        self.tree.tag_configure("even",      background="#f8fafc")

    # ── Data operations ───────────────────────────────────────────────────────

    def refresh(self) -> None:
        self._populate(self.database.get_medicines())

    def _populate(self, rows) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        low_stock_count = 0
        for i, med in enumerate(rows):
            qty = med["quantity"]
            is_low = qty < LOW_STOCK_THRESHOLD
            if is_low:
                low_stock_count += 1
            tag = "low_stock" if is_low else ("even" if i % 2 == 0 else "")
            self.tree.insert(
                "",
                "end",
                values=(
                    med["medicine_id"],
                    med["medicine_name"],
                    qty,
                    f"${med['price']:.2f}",
                    med["expiry_date"],
                ),
                tags=(tag,),
            )

        if low_stock_count:
            self._low_stock_label.configure(
                text=f"⚠  {low_stock_count} low-stock item(s)"
            )
        else:
            self._low_stock_label.configure(text="✓ All stock adequate")

    def save_medicine(self) -> None:
        name        = self.medicine_name_var.get().strip()
        qty_str     = self.quantity_var.get().strip()
        price_str   = self.price_var.get().strip()
        expiry      = self.expiry_date_var.get().strip()

        if not all([name, qty_str, price_str, expiry]):
            messagebox.showerror("Validation Error", "Please complete all medicine fields.")
            return

        try:
            quantity = int(qty_str)
            if quantity < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Validation Error", "Quantity must be a positive whole number.")
            return

        try:
            price = float(price_str)
            if price < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Validation Error", "Price must be a positive number.")
            return

        if self.selected_medicine_id is None:
            self.database.create_medicine(name, quantity, price, expiry)
            messagebox.showinfo("Success", f"Medicine '{name}' added successfully.")
        else:
            self.database.update_medicine(self.selected_medicine_id, name, quantity, price, expiry)
            messagebox.showinfo("Success", f"Medicine '{name}' updated successfully.")

        self.clear_form()
        self.refresh()

    def clear_form(self) -> None:
        self.medicine_name_var.set("")
        self.quantity_var.set("")
        self.price_var.set("")
        self.expiry_date_var.set("")
        self.selected_medicine_id = None
        self._stock_label.configure(text="")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def on_select(self, _event: object = None) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0], "values")
        self.selected_medicine_id = values[0]
        self.medicine_name_var.set(values[1])
        self.quantity_var.set(values[2])
        self.price_var.set(str(values[3]).replace("$", ""))
        self.expiry_date_var.set(values[4])

        # Warn if stock is low
        try:
            qty = int(values[2])
            if qty < LOW_STOCK_THRESHOLD:
                self._stock_label.configure(
                    text=f"⚠ Low stock: only {qty} unit(s) remaining."
                )
            else:
                self._stock_label.configure(text="")
        except (ValueError, IndexError):
            pass

    def delete_medicine(self) -> None:
        if self.selected_medicine_id is None:
            messagebox.showwarning("No Selection", "Please select a medicine from the table first.")
            return
        name = self.medicine_name_var.get()
        if not messagebox.askyesno(
            "Confirm Delete", f"Delete '{name}' from inventory?\nThis cannot be undone."
        ):
            return
        self.database.delete_medicine(self.selected_medicine_id)
        self.clear_form()
        self.refresh()

    def search_medicines(self) -> None:
        keyword = self.search_var.get().strip()
        if not keyword:
            self.refresh()
            return
        self._populate(self.database.search_medicines(keyword))

    def export_medicines(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile="pharmacy_inventory.csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        )
        if not path:
            return
        rows = self.database.get_medicines()
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["medicine_id", "medicine_name", "quantity", "price", "expiry_date"])
            for med in rows:
                writer.writerow([
                    med["medicine_id"], med["medicine_name"],
                    med["quantity"], med["price"], med["expiry_date"]
                ])
        messagebox.showinfo(
            "Export Complete", f"Exported {len(rows)} record(s) to '{os.path.basename(path)}'."
        )
