"""
Smarter Health Connection — Shared UI Utilities
================================================
Colors, fonts, reusable widget classes, and helper functions.
All UI files import from this module.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

# ── Color palette ────────────────────────────────────────────────────────────

C = {
    "primary":       "#1565C0",
    "primary_dk":    "#0D47A1",
    "primary_lt":    "#1976D2",
    "accent":        "#00ACC1",
    "sidebar":       "#0D1B3E",
    "sidebar_hover": "#1A2E5A",
    "sidebar_active":"#1565C0",
    "sidebar_text":  "#B0BEC5",
    "sidebar_atxt":  "#FFFFFF",
    "bg":            "#EEF1F7",
    "card":          "#FFFFFF",
    "header":        "#FFFFFF",
    "text":          "#1A202C",
    "text2":         "#718096",
    "border":        "#E2E8F0",
    "input_bg":      "#F7FAFC",
    "success":       "#2E7D32",
    "success_lt":    "#43A047",
    "warning":       "#E65100",
    "warning_lt":    "#EF6C00",
    "danger":        "#C62828",
    "danger_lt":     "#E53E3E",
    "info":          "#1565C0",
    "row_even":      "#F7FAFC",
    "white":         "#FFFFFF",
    # stat card colors
    "stat1":         "#1565C0",
    "stat2":         "#00838F",
    "stat3":         "#6A1B9A",
    "stat4":         "#2E7D32",
    "stat5":         "#C62828",
    "stat6":         "#E65100",
}

# ── Fonts ────────────────────────────────────────────────────────────────────

F = {
    "title":    ("Segoe UI", 22, "bold"),
    "heading":  ("Segoe UI", 15, "bold"),
    "sub":      ("Segoe UI", 12, "bold"),
    "body":     ("Segoe UI", 10),
    "small":    ("Segoe UI", 9),
    "btn":      ("Segoe UI", 10, "bold"),
    "nav":      ("Segoe UI", 10),
    "label":    ("Segoe UI", 10),
    "mono":     ("Consolas", 10),
}

# ── Message helpers ──────────────────────────────────────────────────────────

def ask_delete(what: str = "this record") -> bool:
    return messagebox.askyesno(
        "Confirm Deletion",
        f"Are you sure you want to permanently delete {what}?\n\nThis cannot be undone.",
        icon="warning",
    )


def msg_error(msg: str, title: str = "Error") -> None:
    messagebox.showerror(title, msg)


def msg_ok(msg: str, title: str = "Success") -> None:
    messagebox.showinfo(title, msg)


def msg_warn(msg: str, title: str = "Warning") -> None:
    messagebox.showwarning(title, msg)


# ── Styled Treeview ──────────────────────────────────────────────────────────

def configure_treeview_style() -> None:
    """Call once at app start to configure global Treeview style."""
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("SHC.Treeview",
                 rowheight=32, font=F["body"],
                 background=C["white"], fieldbackground=C["white"],
                 foreground=C["text"])
    s.configure("SHC.Treeview.Heading",
                 font=F["btn"],
                 background=C["primary"], foreground=C["white"],
                 relief="flat", padding=(8, 6))
    s.map("SHC.Treeview.Heading",
          background=[("active", C["primary_dk"])])
    s.map("SHC.Treeview",
          background=[("selected", C["primary"])],
          foreground=[("selected", C["white"])])


def make_treeview(parent: tk.Widget, columns: tuple, heights: int = 14,
                  col_widths: dict | None = None) -> tuple[tk.Frame, ttk.Treeview]:
    """
    Return (container_frame, treeview) ready for grid/pack.
    The container already includes vertical + horizontal scrollbars.
    """
    frame = tk.Frame(parent, bg=C["white"])
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    vsb = ttk.Scrollbar(frame, orient="vertical")
    hsb = ttk.Scrollbar(frame, orient="horizontal")
    tree = ttk.Treeview(frame, columns=columns, show="headings",
                        height=heights, style="SHC.Treeview",
                        yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)

    col_widths = col_widths or {}
    for col in columns:
        label = col.replace("_", " ").title()
        tree.heading(col, text=label)
        tree.column(col, width=col_widths.get(col, 120), anchor="w", minwidth=50)

    tree.tag_configure("even", background=C["row_even"])
    tree.tag_configure("odd",  background=C["white"])

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")

    return frame, tree


def populate_tree(tree: ttk.Treeview, rows: list, cols: list) -> None:
    """Clear and repopulate tree with rows (list of sqlite3.Row or dict)."""
    tree.delete(*tree.get_children())
    for i, row in enumerate(rows):
        tag = "even" if i % 2 == 0 else "odd"
        tree.insert("", "end", values=[row[c] for c in cols], tags=(tag,))


# ── Reusable widget classes ──────────────────────────────────────────────────

class SHCButton(tk.Button):
    """Styled button with hover effect. style: primary|danger|success|secondary|warning"""
    _STYLES = {
        "primary":   (C["primary"],   C["white"], C["primary_dk"]),
        "danger":    (C["danger"],    C["white"], C["danger_lt"]),
        "success":   (C["success"],   C["white"], C["success_lt"]),
        "secondary": ("#607D8B",      C["white"], "#455A64"),
        "warning":   (C["warning"],   C["white"], C["warning_lt"]),
        "outline":   (C["white"],     C["primary"], C["bg"]),
    }

    def __init__(self, parent, text, command, style="primary", padx=16, pady=8, **kw):
        bg, fg, hover = self._STYLES.get(style, self._STYLES["primary"])
        super().__init__(parent, text=text, command=command,
                         font=F["btn"], bg=bg, fg=fg,
                         activebackground=hover, activeforeground=fg,
                         relief="flat", bd=0, padx=padx, pady=pady,
                         cursor="hand2", **kw)
        self._bg = bg
        self._hover = hover
        self.bind("<Enter>", lambda _e: self.config(bg=self._hover))
        self.bind("<Leave>", lambda _e: self.config(bg=self._bg))


class SHCEntry(tk.Frame):
    """
    Styled entry with optional icon label and placeholder text.
    Wraps tk.Entry or ttk.Combobox in a border frame.
    """

    def __init__(self, parent, variable: tk.StringVar, icon: str = "",
                 show: str = "", values: list | None = None,
                 width: int = 28, **kw):
        super().__init__(parent, bg=C["white"], highlightbackground=C["border"],
                         highlightthickness=1, **kw)
        if icon:
            tk.Label(self, text=icon, font=("Segoe UI", 12),
                     bg=C["white"], fg=C["text2"]).pack(side="left", padx=(10, 4), pady=6)

        if values is not None:
            self._widget = ttk.Combobox(self, textvariable=variable,
                                        values=values, font=F["body"],
                                        state="readonly", width=width)
        else:
            self._widget = tk.Entry(self, textvariable=variable,
                                    font=F["body"], bg=C["input_bg"],
                                    fg=C["text"], relief="flat", bd=0,
                                    show=show, width=width)
        self._widget.pack(side="left", fill="x", expand=True, pady=6, padx=(4, 8))

    def get(self) -> str:
        return self._widget.get()

    def focus(self):
        self._widget.focus()


class LabeledField(tk.Frame):
    """A (label, entry) pair used inside form cards."""

    def __init__(self, parent, label: str, variable: tk.StringVar,
                 icon: str = "", show: str = "", values: list | None = None,
                 row: int = 0, column: int = 0, colspan: int = 1, **kw):
        super().__init__(parent, bg=C["card"], **kw)
        tk.Label(self, text=label, font=F["label"],
                 bg=C["card"], fg=C["text"], anchor="w").pack(anchor="w", pady=(6, 2))
        self.entry = SHCEntry(self, variable, icon=icon, show=show, values=values)
        self.entry.pack(fill="x")

    def get(self) -> str:
        return self.entry.get()


class StatCard(tk.Frame):
    """Coloured dashboard stat card."""

    def __init__(self, parent, title: str, value, icon: str, color: str, **kw):
        super().__init__(parent, bg=color, padx=20, pady=16, **kw)
        tk.Label(self, text=icon, font=("Segoe UI", 26),
                 bg=color, fg=C["white"]).pack(anchor="w")
        self._val = tk.Label(self, text=str(value), font=("Segoe UI", 22, "bold"),
                              bg=color, fg=C["white"])
        self._val.pack(anchor="w", pady=(4, 2))
        tk.Label(self, text=title, font=("Segoe UI", 9),
                 bg=color, fg="#BBDEFB").pack(anchor="w")

    def set(self, value) -> None:
        self._val.config(text=str(value))


class PageHeader(tk.Frame):
    """Standard page header: title + optional subtitle + divider."""

    def __init__(self, parent, title: str, subtitle: str = "", **kw):
        super().__init__(parent, bg=C["bg"], **kw)
        tk.Label(self, text=title, font=F["heading"],
                 bg=C["bg"], fg=C["primary"]).pack(anchor="w")
        if subtitle:
            tk.Label(self, text=subtitle, font=F["small"],
                     bg=C["bg"], fg=C["text2"]).pack(anchor="w", pady=(1, 0))
        tk.Frame(self, height=2, bg=C["primary"]).pack(fill="x", pady=(8, 0))


class FormCard(tk.Frame):
    """White rounded-look card used in form panels."""

    def __init__(self, parent, title: str = "", **kw):
        super().__init__(parent, bg=C["card"], padx=16, pady=16, **kw)
        if title:
            tk.Label(self, text=title, font=F["sub"],
                     bg=C["card"], fg=C["primary"]).pack(anchor="w", pady=(0, 12))
        tk.Frame(self, height=1, bg=C["border"]).pack(fill="x", pady=(0, 12))


class SectionDivider(tk.Frame):
    """A thin horizontal divider."""

    def __init__(self, parent, **kw):
        super().__init__(parent, height=1, bg=C["border"], **kw)
