"""Theme helpers for the clinic desktop UI."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class ThemeManager:
    """Simple dark/light theme manager for the Tkinter UI."""

    def __init__(self, root: tk.Misc) -> None:
        self.root = root
        self.current_mode = "light"
        self.style = ttk.Style(root)
        self._configure_styles()

    def _configure_styles(self) -> None:
        self.style.theme_use("clam")
        self.style.configure("Card.TFrame", background="#ffffff")
        self.style.configure("Sidebar.TFrame", background="#0f172a")
        self.style.configure("Header.TLabel", background="#f8fafc", foreground="#0f172a", font=("Segoe UI", 12, "bold"))
        self.style.configure("Muted.TLabel", foreground="#64748b")

    def toggle(self) -> str:
        self.current_mode = "dark" if self.current_mode == "light" else "light"
        self.apply(self.current_mode)
        return self.current_mode

    def apply(self, mode: str) -> None:
        self.current_mode = mode
        if mode == "dark":
            self.root.configure(background="#0f172a")
            self.style.configure("TFrame", background="#0f172a")
            self.style.configure("TLabel", background="#0f172a", foreground="#f8fafc")
            self.style.configure("TEntry", fieldbackground="#1e293b", foreground="#f8fafc")
            self.style.configure("TCombobox", fieldbackground="#1e293b", foreground="#f8fafc")
            self.style.configure("Card.TFrame", background="#111827")
            self.style.configure("Sidebar.TFrame", background="#020617")
            self.style.configure("Header.TLabel", background="#111827", foreground="#f8fafc")
            self.style.configure("Muted.TLabel", foreground="#cbd5e1")
        else:
            self.root.configure(background="#f8fafc")
            self.style.configure("TFrame", background="#f8fafc")
            self.style.configure("TLabel", background="#f8fafc", foreground="#0f172a")
            self.style.configure("TEntry", fieldbackground="#ffffff", foreground="#0f172a")
            self.style.configure("TCombobox", fieldbackground="#ffffff", foreground="#0f172a")
            self.style.configure("Card.TFrame", background="#ffffff")
            self.style.configure("Sidebar.TFrame", background="#0f172a")
            self.style.configure("Header.TLabel", background="#ffffff", foreground="#0f172a")
            self.style.configure("Muted.TLabel", foreground="#64748b")
