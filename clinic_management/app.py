"""
ClinicCare Pro — Main Application Window
=========================================
Entry point for the Tkinter desktop application.

Author   : ClinicCare Pro Dev Team
Version  : 2.0.0
Python   : 3.8+
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from clinic_management.authentication.auth import AuthenticationPanel
from clinic_management.billing.billing import BillingView
from clinic_management.appointments.appointment import AppointmentView
from clinic_management.dashboard.dashboard import DashboardView
from clinic_management.database.db import ClinicDatabase
from clinic_management.doctors.doctor import DoctorsView
from clinic_management.patients.patients import PatientsView
from clinic_management.pharmacy.pharmacy import PharmacyView
from clinic_management.reports.reports import ReportsView
from clinic_management.utils.theme import ThemeManager

# ──────────────────────────────────────────────────────────────────────────────
# Palette constants — dark sidebar, clean content area
# ──────────────────────────────────────────────────────────────────────────────
SIDEBAR_BG   = "#0f172a"   # Deep navy
SIDEBAR_FG   = "#cbd5e1"   # Muted slate
ACTIVE_BG    = "#1e40af"   # Vivid blue highlight
ACTIVE_FG    = "#ffffff"
HEADER_BG    = "#1e293b"   # Dark slate header
CONTENT_BG   = "#f1f5f9"   # Light grey content
ACCENT       = "#3b82f6"   # Brand blue
DANGER       = "#ef4444"
SUCCESS      = "#22c55e"
WARNING      = "#f59e0b"

# Navigation items: (display label, icon character, view_key)
NAV_ITEMS = [
    ("Dashboard",    "⊞", "dashboard"),
    ("Patients",     "🧑", "patients"),
    ("Doctors",      "👨‍⚕️", "doctors"),
    ("Appointments", "📅", "appointments"),
    ("Pharmacy",     "💊", "pharmacy"),
    ("Billing",      "💳", "billing"),
    ("Reports",      "📊", "reports"),
]


class ClinicManagementApp(tk.Tk):
    """
    Top-level Tkinter window for ClinicCare Pro.

    Responsibilities
    ----------------
    - Bootstrap the SQLite database.
    - Show the authentication screen; on success load the main shell.
    - Render a fixed sidebar for navigation and a content frame that
      hot-swaps module views without destroying them (lazy creation).
    - Provide a status bar with the logged-in user's name and role.
    - Support light / dark theme toggling via ThemeManager.
    """

    # ── Construction ──────────────────────────────────────────────────────────

    def __init__(self) -> None:
        super().__init__()

        # Core state
        self._current_user: Optional[object] = None
        self._active_nav: Optional[str] = None
        self._views: dict[str, ttk.Frame] = {}
        self._nav_buttons: dict[str, tk.Button] = {}

        # Database (initialises schema + default admin on first run)
        self.db = ClinicDatabase()

        # Theme manager
        self.theme = ThemeManager(self)

        # Configure root window
        self._configure_window()

        # Start on the authentication screen
        self._show_auth_screen()

    def _configure_window(self) -> None:
        """Set title, geometry, icon, and global key-bindings."""
        self.title("ClinicCare Pro — Smarter Health Connection")
        self.geometry("1280x780")
        self.minsize(1024, 660)
        self.configure(bg=CONTENT_BG)

        # Centre on screen
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - 1280) // 2
        y = (screen_h - 780) // 2
        self.geometry(f"1280x780+{x}+{y}")

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<F11>", lambda _e: self._toggle_fullscreen())
        self.bind("<Escape>", lambda _e: self.attributes("-fullscreen", False))
        self._fullscreen = False

    # ── Authentication screen ─────────────────────────────────────────────────

    def _show_auth_screen(self) -> None:
        """
        Display a centred, card-style login / register panel.
        Destroys itself and launches the main shell on success.
        """
        # Clear any existing children
        for widget in self.winfo_children():
            widget.destroy()

        # Full-window gradient canvas background
        canvas = tk.Canvas(self, bg=SIDEBAR_BG, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        # Decorative circles for visual interest
        canvas.create_oval(-120, -120, 340, 340, fill="#1e293b", outline="")
        canvas.create_oval(900, 500, 1400, 1000, fill="#172554", outline="")

        # Centred white card
        card_frame = tk.Frame(canvas, bg="white", bd=0)
        card_frame.place(relx=0.5, rely=0.5, anchor="center", width=420)

        # Brand strip at top of card
        brand = tk.Frame(card_frame, bg=ACTIVE_BG, height=6)
        brand.pack(fill="x")

        inner = tk.Frame(card_frame, bg="white", padx=36, pady=32)
        inner.pack(fill="both", expand=True)

        # App title
        tk.Label(
            inner,
            text="ClinicCare Pro",
            font=("Segoe UI", 22, "bold"),
            fg=SIDEBAR_BG,
            bg="white",
        ).pack(anchor="w")
        tk.Label(
            inner,
            text="Smarter Health Connection",
            font=("Segoe UI", 10),
            fg="#64748b",
            bg="white",
        ).pack(anchor="w", pady=(0, 24))

        # Separator
        ttk.Separator(inner, orient="horizontal").pack(fill="x", pady=(0, 24))

        # Embed the AuthenticationPanel (handles login + register tabs)
        auth_panel = AuthenticationPanel(inner, self.db, self._on_authenticated)
        auth_panel.pack(fill="both", expand=True)

        # Footer
        tk.Label(
            inner,
            text="© 2026 ClinicCare Pro  |  v2.0.0",
            font=("Segoe UI", 8),
            fg="#94a3b8",
            bg="white",
        ).pack(pady=(20, 0))

    def _on_authenticated(self, user: object) -> None:
        """Called by AuthenticationPanel after a successful login."""
        self._current_user = user
        self._build_main_shell()

    # ── Main shell ────────────────────────────────────────────────────────────

    def _build_main_shell(self) -> None:
        """
        Construct the persistent application shell:
        - Header bar (logo + user info + theme toggle + logout)
        - Sidebar navigation (collapsible items)
        - Content pane (lazy-loaded module views)
        - Status bar
        """
        for widget in self.winfo_children():
            widget.destroy()

        self._views.clear()
        self._nav_buttons.clear()

        # ── Outer layout: header / body / statusbar ──────────────────────────
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        header = self._build_header()
        header.grid(row=0, column=0, sticky="ew")

        body = tk.Frame(self, bg=CONTENT_BG)
        body.grid(row=1, column=0, sticky="nsew")
        body.rowconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        sidebar = self._build_sidebar(body)
        sidebar.grid(row=0, column=0, sticky="ns")

        self._content_frame = tk.Frame(body, bg=CONTENT_BG)
        self._content_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self._content_frame.rowconfigure(0, weight=1)
        self._content_frame.columnconfigure(0, weight=1)

        statusbar = self._build_statusbar()
        statusbar.grid(row=2, column=0, sticky="ew")

        # Navigate to Dashboard by default
        self._navigate("dashboard")

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self) -> tk.Frame:
        """Top header bar with branding, user info and controls."""
        header = tk.Frame(self, bg=HEADER_BG, height=56)
        header.pack_propagate(False)

        # Left: logo + app name
        left = tk.Frame(header, bg=HEADER_BG)
        left.pack(side="left", padx=20, fill="y")
        tk.Label(
            left,
            text="🏥",
            font=("Segoe UI", 18),
            bg=HEADER_BG,
            fg="white",
        ).pack(side="left", pady=10)
        tk.Label(
            left,
            text="  ClinicCare Pro",
            font=("Segoe UI", 13, "bold"),
            bg=HEADER_BG,
            fg="white",
        ).pack(side="left")

        # Separator
        tk.Frame(header, bg="#334155", width=1).pack(side="left", fill="y", padx=16, pady=10)

        # Section title label (updated on navigation)
        self._section_label = tk.Label(
            header,
            text="Dashboard",
            font=("Segoe UI", 11),
            bg=HEADER_BG,
            fg="#94a3b8",
        )
        self._section_label.pack(side="left")

        # Right: user info, theme, logout
        right = tk.Frame(header, bg=HEADER_BG)
        right.pack(side="right", padx=20, fill="y")

        # Logout button
        self._make_header_btn(right, "⇤  Logout", self._logout).pack(
            side="right", padx=(8, 0), pady=10
        )

        # Theme toggle
        self._make_header_btn(right, "◑ Theme", self._toggle_theme).pack(
            side="right", padx=(0, 4), pady=10
        )

        # Separator
        tk.Frame(right, bg="#334155", width=1).pack(side="right", fill="y", padx=12, pady=10)

        # User chip
        user = self._current_user
        role_text = user["role"] if user else "Unknown"
        name_text = user["fullname"] if user else "Guest"
        tk.Label(
            right,
            text=f"👤  {name_text}",
            font=("Segoe UI", 10, "bold"),
            bg=HEADER_BG,
            fg="white",
        ).pack(side="right", pady=10)
        tk.Label(
            right,
            text=f"  {role_text}  ",
            font=("Segoe UI", 8),
            bg=ACTIVE_BG,
            fg="white",
            padx=6,
            pady=2,
        ).pack(side="right", pady=10)

        return header

    def _make_header_btn(self, parent: tk.Frame, text: str, cmd) -> tk.Button:
        """Flat, ghost-style header action button."""
        btn = tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 9),
            bg=HEADER_BG,
            fg="#94a3b8",
            activebackground="#334155",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=cmd,
        )
        btn.bind("<Enter>", lambda _e: btn.configure(fg="white"))
        btn.bind("<Leave>", lambda _e: btn.configure(fg="#94a3b8"))
        return btn

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self, parent: tk.Frame) -> tk.Frame:
        """
        Fixed-width dark sidebar with labelled navigation items.
        Each item highlights when active and shows a left accent bar.
        """
        sidebar = tk.Frame(parent, bg=SIDEBAR_BG, width=220)
        sidebar.pack_propagate(False)

        # App version tag
        ver_frame = tk.Frame(sidebar, bg=SIDEBAR_BG)
        ver_frame.pack(fill="x", pady=(16, 8))
        tk.Label(
            ver_frame,
            text="NAVIGATION",
            font=("Segoe UI", 8, "bold"),
            bg=SIDEBAR_BG,
            fg="#475569",
        ).pack(padx=20, anchor="w")

        # Nav items
        for label, icon, key in NAV_ITEMS:
            self._build_nav_item(sidebar, label, icon, key)

        # Bottom: version number
        tk.Frame(sidebar, bg="#1e293b", height=1).pack(fill="x", side="bottom", pady=0)
        tk.Label(
            sidebar,
            text="ClinicCare Pro  v2.0.0",
            font=("Segoe UI", 8),
            bg=SIDEBAR_BG,
            fg="#334155",
        ).pack(side="bottom", pady=10)

        return sidebar

    def _build_nav_item(
        self, parent: tk.Frame, label: str, icon: str, key: str
    ) -> None:
        """Create a single sidebar navigation button with hover and active states."""
        container = tk.Frame(parent, bg=SIDEBAR_BG, cursor="hand2")
        container.pack(fill="x")

        # Active accent strip on the left
        accent = tk.Frame(container, width=4, bg=SIDEBAR_BG)
        accent.pack(side="left", fill="y")

        # Icon + label
        btn = tk.Button(
            container,
            text=f"  {icon}   {label}",
            font=("Segoe UI", 10),
            bg=SIDEBAR_BG,
            fg=SIDEBAR_FG,
            activebackground="#1e293b",
            activeforeground="white",
            relief="flat",
            bd=0,
            anchor="w",
            padx=12,
            pady=12,
            cursor="hand2",
            command=lambda k=key: self._navigate(k),
        )
        btn.pack(side="left", fill="x", expand=True)

        # Hover effects
        def _on_enter(_e: object, b=btn, a=accent) -> None:
            if self._active_nav != key:
                b.configure(bg="#1e293b", fg="white")
                a.configure(bg="#334155")

        def _on_leave(_e: object, b=btn, a=accent) -> None:
            if self._active_nav != key:
                b.configure(bg=SIDEBAR_BG, fg=SIDEBAR_FG)
                a.configure(bg=SIDEBAR_BG)

        btn.bind("<Enter>", _on_enter)
        btn.bind("<Leave>", _on_leave)
        container.bind("<Enter>", _on_enter)
        container.bind("<Leave>", _on_leave)

        # Store references so we can highlight the active one
        self._nav_buttons[key] = (btn, accent)

    # ── Navigation ────────────────────────────────────────────────────────────

    def _navigate(self, key: str) -> None:
        """
        Switch the content area to the requested view.

        Views are created lazily on first access and then simply
        shown/hidden rather than destroyed, preserving their state.
        """
        # Deactivate old button
        if self._active_nav and self._active_nav in self._nav_buttons:
            old_btn, old_accent = self._nav_buttons[self._active_nav]
            old_btn.configure(bg=SIDEBAR_BG, fg=SIDEBAR_FG)
            old_accent.configure(bg=SIDEBAR_BG)

        self._active_nav = key

        # Activate new button
        btn, accent = self._nav_buttons[key]
        btn.configure(bg=ACTIVE_BG, fg=ACTIVE_FG)
        accent.configure(bg=ACCENT)

        # Update section label in header
        label_map = {item[2]: item[0] for item in NAV_ITEMS}
        self._section_label.configure(text=f"› {label_map.get(key, key.title())}")

        # Hide all existing views
        for view in self._views.values():
            view.grid_remove()

        # Lazy-create the requested view if needed
        if key not in self._views:
            self._views[key] = self._create_view(key)

        # Show the requested view
        view = self._views[key]
        view.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)

        # Refresh data-driven views whenever they are shown
        if hasattr(view, "refresh"):
            view.refresh()

    def _create_view(self, key: str) -> ttk.Frame:
        """Factory: instantiate and return the correct view for *key*."""
        view_map = {
            "dashboard":    lambda: DashboardView(self._content_frame, self.db),
            "patients":     lambda: PatientsView(self._content_frame, self.db),
            "doctors":      lambda: DoctorsView(self._content_frame, self.db),
            "appointments": lambda: AppointmentView(self._content_frame, self.db),
            "pharmacy":     lambda: PharmacyView(self._content_frame, self.db),
            "billing":      lambda: BillingView(self._content_frame, self.db),
            "reports":      lambda: ReportsView(self._content_frame, self.db),
        }
        factory = view_map.get(key)
        if factory is None:
            placeholder = ttk.Frame(self._content_frame)
            ttk.Label(placeholder, text=f"Module '{key}' not found.", font=("Segoe UI", 13)).pack(pady=40)
            return placeholder
        return factory()

    # ── Status bar ────────────────────────────────────────────────────────────

    def _build_statusbar(self) -> tk.Frame:
        """Thin status bar at the very bottom of the window."""
        bar = tk.Frame(self, bg=HEADER_BG, height=26)
        bar.pack_propagate(False)

        import datetime
        now = datetime.datetime.now().strftime("%A, %d %B %Y  •  %H:%M")
        self._status_time = tk.Label(
            bar,
            text=now,
            font=("Segoe UI", 8),
            bg=HEADER_BG,
            fg="#64748b",
        )
        self._status_time.pack(side="right", padx=16)
        self._tick_clock()

        tk.Label(
            bar,
            text="● Connected  |  SQLite Database",
            font=("Segoe UI", 8),
            bg=HEADER_BG,
            fg="#22c55e",
        ).pack(side="left", padx=16)

        return bar

    def _tick_clock(self) -> None:
        """Update the clock in the status bar every second."""
        import datetime
        now = datetime.datetime.now().strftime("%A, %d %B %Y  •  %H:%M:%S")
        if hasattr(self, "_status_time") and self._status_time.winfo_exists():
            self._status_time.configure(text=now)
            self.after(1000, self._tick_clock)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _toggle_theme(self) -> None:
        mode = self.theme.toggle()
        # Persist sidebar / header colours which theme manager doesn't touch
        # (they use native tk.Frame, not ttk)

    def _toggle_fullscreen(self) -> None:
        self._fullscreen = not self._fullscreen
        self.attributes("-fullscreen", self._fullscreen)

    def _logout(self) -> None:
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self._current_user = None
            self._views.clear()
            self._nav_buttons.clear()
            self._show_auth_screen()

    def _on_close(self) -> None:
        if messagebox.askyesno("Exit", "Are you sure you want to exit ClinicCare Pro?"):
            try:
                self.db.connection.close()
            except Exception:
                pass
            self.destroy()
