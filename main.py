"""
Smarter Health Connection — Application Entry Point
=====================================================
Initializes the database, shows the login screen, and loads the main shell.
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from utils import C, F, configure_treeview_style
from database import Database
from login import LoginWindow

# Module imports
from dashboard import DashboardView
from patient import PatientView
from doctor import DoctorView
from appointment import AppointmentView
from pharmacy import PharmacyView
from billing import BillingView
from reports import ReportsView
from settings import SettingsView


class MainWindow(tk.Tk):
    def __init__(self, user_data, db):
        super().__init__()
        self.user_data = user_data
        self.db = db

        self.title("Smarter Health Connection - Dashboard")
        self.geometry("1280x800")
        self.configure(bg=C["bg"])
        self.minsize(1024, 768)
        
        # Center window
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")

        configure_treeview_style()

        self.views = {}
        self.current_view = None

        self._build_header()
        self._build_sidebar()
        
        # Content frame
        self.content_frame = tk.Frame(self, bg=C["bg"])
        self.content_frame.pack(side="left", fill="both", expand=True)

        self._init_views()
        self._navigate("Dashboard")

    def _build_header(self):
        header = tk.Frame(self, bg=C["white"], height=60)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        # Logo / Title
        tk.Label(header, text="🏥 SMARTER HEALTH CONNECTION", font=F["heading"], bg=C["white"], fg=C["primary"]).pack(side="left", padx=20)

        # Profile
        right_frame = tk.Frame(header, bg=C["white"])
        right_frame.pack(side="right", padx=20)
        
        self.lbl_clock = tk.Label(right_frame, text="", font=F["body"], bg=C["white"], fg=C["text2"])
        self.lbl_clock.pack(side="left", padx=(0, 20))
        self._tick_clock()

        role = self.user_data["role"]
        name = self.user_data["fullname"]
        tk.Label(right_frame, text=f"👤 {name} ({role})", font=F["sub"], bg=C["white"], fg=C["primary"]).pack(side="left")

    def _tick_clock(self):
        now = datetime.now().strftime("%A, %d %B %Y  %I:%M:%S %p")
        self.lbl_clock.config(text=now)
        self.after(1000, self._tick_clock)

    def _build_sidebar(self):
        sidebar = tk.Frame(self, bg=C["sidebar"], width=250)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Navigation items
        nav_items = [
            ("⊞ Dashboard", "Dashboard"),
            ("🧑 Patients", "Patients"),
            ("👨‍⚕️ Doctors", "Doctors"),
            ("📅 Appointments", "Appointments"),
            ("💊 Pharmacy", "Pharmacy"),
            ("🧾 Billing", "Billing"),
            ("📊 Reports", "Reports"),
            ("⚙️ Settings", "Settings"),
        ]

        self.nav_btns = {}
        for text, key in nav_items:
            btn = tk.Button(sidebar, text=f"  {text}", font=F["nav"], bg=C["sidebar"], fg=C["sidebar_text"],
                            relief="flat", bd=0, anchor="w", padx=20, pady=12, cursor="hand2",
                            activebackground=C["sidebar_active"], activeforeground=C["sidebar_atxt"])
            btn.pack(fill="x")
            btn.bind("<Button-1>", lambda e, k=key: self._navigate(k))
            
            # Hover effects
            btn.bind("<Enter>", lambda e, b=btn, k=key: b.config(bg=C["sidebar_hover"] if self.current_view != k else C["sidebar_active"]))
            btn.bind("<Leave>", lambda e, b=btn, k=key: b.config(bg=C["sidebar"] if self.current_view != k else C["sidebar_active"]))
            
            self.nav_btns[key] = btn

        # Logout at bottom
        btn_logout = tk.Button(sidebar, text="  🚪 Logout", font=F["nav"], bg=C["sidebar"], fg=C["danger_lt"],
                               relief="flat", bd=0, anchor="w", padx=20, pady=12, cursor="hand2",
                               activebackground="#2A1B1B", activeforeground=C["danger_lt"])
        btn_logout.pack(side="bottom", fill="x", pady=(0, 20))
        btn_logout.bind("<Button-1>", lambda e: self._logout())

    def _init_views(self):
        self.views["Dashboard"] = DashboardView(self.content_frame, self.db)
        self.views["Patients"] = PatientView(self.content_frame, self.db)
        self.views["Doctors"] = DoctorView(self.content_frame, self.db)
        self.views["Appointments"] = AppointmentView(self.content_frame, self.db)
        self.views["Pharmacy"] = PharmacyView(self.content_frame, self.db)
        self.views["Billing"] = BillingView(self.content_frame, self.db)
        self.views["Reports"] = ReportsView(self.content_frame, self.db)
        self.views["Settings"] = SettingsView(self.content_frame, self.db)

    def _navigate(self, key):
        if self.current_view:
            self.views[self.current_view].pack_forget()
            self.nav_btns[self.current_view].config(bg=C["sidebar"], fg=C["sidebar_text"])

        self.current_view = key
        
        # Highlight active nav
        self.nav_btns[key].config(bg=C["sidebar_active"], fg=C["sidebar_atxt"])
        
        # Show view
        view = self.views[key]
        view.pack(fill="both", expand=True)
        if hasattr(view, 'refresh'):
            view.refresh()

    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.destroy()
            start_app()


def start_app():
    # Make Windows DPI-aware for crisp text
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    def on_login_success(user_data):
        db = Database()
        app = MainWindow(user_data, db)
        app.mainloop()

    login = LoginWindow(on_login_success)
    login.mainloop()


if __name__ == "__main__":
    start_app()
