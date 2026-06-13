"""
Reports & Analytics View
=========================
Read-only summary panel showing key clinic statistics, billing totals,
patient distribution, and top doctors. Refreshes on every navigation.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class ReportsView(ttk.Frame):
    """
    Analytics and reporting panel.

    Shows:
    - Overview stat cards (patients, doctors, appointments, revenue)
    - Billing breakdown by payment status
    - Full billing ledger in a Treeview
    - Low-stock pharmacy alerts
    """

    def __init__(self, parent: tk.Misc, database) -> None:
        super().__init__(parent)
        self.database = database
        self._build_ui()
        self.refresh()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Page title
        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        ttk.Label(
            header,
            text="Reports & Analytics",
            font=("Segoe UI", 16, "bold"),
        ).pack(side="left")
        ttk.Button(header, text="↺  Refresh", command=self.refresh).pack(
            side="right", padx=(0, 4)
        )

        # ── Stat cards row ────────────────────────────────────────────────────
        cards_frame = ttk.Frame(self)
        cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        cards_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)

        card_defs = [
            ("Total Patients",      "#3b82f6", "patients"),
            ("Total Doctors",       "#8b5cf6", "doctors"),
            ("Today's Appointments","#f59e0b", "appointments"),
            ("Today's Revenue",     "#22c55e", "revenue"),
            ("Low Stock Alerts",    "#ef4444", "medicines"),
        ]
        self._stat_labels: dict[str, tk.Label] = {}
        for col, (title, colour, key) in enumerate(card_defs):
            card = tk.Frame(
                cards_frame,
                bg=colour,
                padx=16,
                pady=14,
                bd=0,
            )
            card.grid(row=0, column=col, padx=6, sticky="nsew")
            tk.Label(card, text=title, bg=colour, fg="white",
                     font=("Segoe UI", 9, "bold")).pack(anchor="w")
            val = tk.Label(card, text="—", bg=colour, fg="white",
                           font=("Segoe UI", 22, "bold"))
            val.pack(anchor="w", pady=(6, 0))
            self._stat_labels[key] = val

        # ── Billing ledger ────────────────────────────────────────────────────
        ledger_frame = ttk.LabelFrame(self, text="  Billing Ledger", padding=8)
        ledger_frame.grid(row=2, column=0, sticky="nsew")
        ledger_frame.columnconfigure(0, weight=1)
        ledger_frame.rowconfigure(0, weight=1)

        columns = ("bill_id", "patient_name", "amount", "payment_status", "payment_date")
        self.tree = ttk.Treeview(ledger_frame, columns=columns, show="headings", height=14)

        col_widths = {
            "bill_id":        60,
            "patient_name":  200,
            "amount":        100,
            "payment_status": 120,
            "payment_date":  160,
        }
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=col_widths.get(col, 120), anchor="w")

        scrollbar = ttk.Scrollbar(ledger_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.tag_configure("Paid",    foreground="#166534")
        self.tree.tag_configure("Pending", foreground="#92400e")
        self.tree.tag_configure("Partial", foreground="#1e40af")
        self.tree.tag_configure("Waived",  foreground="#6b7280")

        # Summary row at bottom
        self._summary_label = ttk.Label(
            self, text="", font=("Segoe UI", 9), foreground="#64748b"
        )
        self._summary_label.grid(row=3, column=0, sticky="w", pady=(8, 0))

    # ── Data refresh ──────────────────────────────────────────────────────────

    def refresh(self) -> None:
        """Reload all stats and the billing ledger from the database."""
        self._refresh_stats()
        self._refresh_ledger()

    def _refresh_stats(self) -> None:
        stats = self.database.get_dashboard_stats()
        self._stat_labels["patients"].configure(text=str(stats["patients"]))
        self._stat_labels["doctors"].configure(text=str(stats["doctors"]))
        self._stat_labels["appointments"].configure(text=str(stats["appointments"]))
        self._stat_labels["revenue"].configure(text=f"${stats['revenue']:,.2f}")
        self._stat_labels["medicines"].configure(text=str(stats["medicines"]))

    def _refresh_ledger(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        total = paid = pending = 0.0
        rows = self.database.get_billing()
        for bill in rows:
            status = bill["payment_status"]
            amount = bill["amount"]
            total += amount
            if status == "Paid":
                paid += amount
            elif status == "Pending":
                pending += amount

            self.tree.insert(
                "",
                "end",
                values=(
                    bill["bill_id"],
                    bill["patient_name"],
                    f"${amount:,.2f}",
                    status,
                    bill["payment_date"],
                ),
                tags=(status,),
            )

        self._summary_label.configure(
            text=(
                f"Total billed: ${total:,.2f}  •  "
                f"Collected: ${paid:,.2f}  •  "
                f"Pending: ${pending:,.2f}  •  "
                f"Records: {len(rows)}"
            )
        )
