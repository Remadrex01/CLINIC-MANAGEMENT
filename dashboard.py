"""
Smarter Health Connection — Dashboard Module
==============================================
Main dashboard view showing statistics cards.
"""

import tkinter as tk
from tkinter import ttk
from database import Database
from utils import C, F, PageHeader, StatCard


class DashboardView(tk.Frame):
    def __init__(self, parent, db: Database):
        super().__init__(parent, bg=C["bg"])
        self.db = db

        PageHeader(self, "Dashboard", "Overview of clinic operations").pack(fill="x", padx=20, pady=(20, 10))

        self.cards_frame = tk.Frame(self, bg=C["bg"])
        self.cards_frame.pack(fill="x", padx=20, pady=10)
        
        # We will keep references to update them
        self.cards = {}
        self._build_cards()

    def _build_cards(self):
        # Layout grid 3 columns
        for i in range(3):
            self.cards_frame.grid_columnconfigure(i, weight=1)

        self.cards["patients"] = StatCard(self.cards_frame, "Total Patients", 0, "🧑", C["stat1"])
        self.cards["patients"].grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.cards["doctors"] = StatCard(self.cards_frame, "Total Doctors", 0, "👨‍⚕️", C["stat2"])
        self.cards["doctors"].grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.cards["appointments"] = StatCard(self.cards_frame, "Today's Appointments", 0, "📅", C["stat3"])
        self.cards["appointments"].grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        self.cards["bills"] = StatCard(self.cards_frame, "Total Bills", 0, "🧾", C["stat4"])
        self.cards["bills"].grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.cards["revenue"] = StatCard(self.cards_frame, "Total Revenue ($)", 0, "💵", C["stat5"])
        self.cards["revenue"].grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.cards["low_stock"] = StatCard(self.cards_frame, "Low Stock Alerts", 0, "⚠️", C["stat6"])
        self.cards["low_stock"].grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

    def refresh(self):
        """Called whenever the view is shown to refresh stats."""
        stats = self.db.get_stats()
        self.cards["patients"].set(stats["patients"])
        self.cards["doctors"].set(stats["doctors"])
        self.cards["appointments"].set(stats["appointments"])
        self.cards["bills"].set(stats["bills"])
        self.cards["revenue"].set(f"{stats['revenue']:,.2f}")
        self.cards["low_stock"].set(stats["low_stock"])
