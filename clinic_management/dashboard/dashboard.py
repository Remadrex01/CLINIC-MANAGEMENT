"""Dashboard landing page for the clinic system."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class DashboardView(ttk.Frame):
    """Shows summary cards and current clinic performance."""

    def __init__(self, parent: tk.Misc, database) -> None:
        super().__init__(parent)
        self.database = database
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        ttk.Label(self, text="Dashboard Overview", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 16))
        ttk.Label(self, text="A live view of patients, doctors, appointments, billing, and stock.", foreground="#64748b").grid(row=1, column=0, sticky="w", pady=(0, 12))

        cards = ttk.Frame(self)
        cards.grid(row=2, column=0, sticky="ew")
        cards.columnconfigure((0, 1, 2, 3, 4), weight=1)
        self.card_frames = []
        for index, title in enumerate(["Total Patients", "Total Doctors", "Appointments Today", "Revenue Today", "Low Stock Alerts"]):
            card = ttk.Frame(cards, padding=12, style="Card.TFrame")
            card.grid(row=0, column=index, padx=6, pady=6, sticky="nsew")
            ttk.Label(card, text=title, font=("Segoe UI", 10, "bold")).pack(anchor="w")
            value_label = ttk.Label(card, text="0", font=("Segoe UI", 18, "bold"))
            value_label.pack(anchor="w", pady=(6, 0))
            self.card_frames.append(value_label)

        self.activity = ttk.Label(self, text="", justify="left", wraplength=700)
        self.activity.grid(row=3, column=0, sticky="w", pady=(20, 0))

    def refresh(self) -> None:
        stats = self.database.get_dashboard_stats()
        values = [stats["patients"], stats["doctors"], stats["appointments"], f"${stats['revenue']:.2f}", stats["medicines"]]
        for label, value in zip(self.card_frames, values):
            label.configure(text=str(value))
        self.activity.configure(text="ClinicCare Pro is ready. Use the navigation menu to manage patients, doctors, appointments, pharmacy stock, billing, and detailed reports.")
