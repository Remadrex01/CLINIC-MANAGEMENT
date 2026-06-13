"""Authentication views for login and registration."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox


class AuthenticationPanel(ttk.Frame):
    """Handles login and registration workflows."""

    def __init__(self, parent: tk.Misc, database, on_authenticated) -> None:
        super().__init__(parent, padding=20)
        self.database = database
        self.on_authenticated = on_authenticated
        self.mode = tk.StringVar(value="Login")
        self.remember_me = tk.BooleanVar(value=False)
        self.show_password = tk.BooleanVar(value=False)
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        ttk.Label(self, text=" ClinicCare Pro", font=("Segoe UI", 20, "bold")).grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(self, text="Secure access for clinicians and staff", foreground="#64748b").grid(row=1, column=0, sticky="ew", pady=(0, 16))

        self.mode_toggle = ttk.Frame(self)
        self.mode_toggle.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        ttk.Button(self.mode_toggle, text="Login", command=lambda: self.set_mode("Login")).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(self.mode_toggle, text="Register", command=lambda: self.set_mode("Register")).grid(row=0, column=1)

        self.form_frame = ttk.Frame(self)
        self.form_frame.grid(row=3, column=0, sticky="ew")
        self.set_mode(self.mode.get())

    def set_mode(self, mode: str) -> None:
        self.mode.set(mode)
        for child in self.form_frame.winfo_children():
            child.destroy()
        if mode == "Login":
            self._build_login_form()
        else:
            self._build_register_form()

    def _build_login_form(self) -> None:
        ttk.Label(self.form_frame, text="Username").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.login_username = ttk.Entry(self.form_frame)
        self.login_username.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        ttk.Label(self.form_frame, text="Password").grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.login_password = ttk.Entry(self.form_frame, show="*")
        self.login_password.grid(row=3, column=0, sticky="ew", pady=(0, 8))

        ttk.Checkbutton(self.form_frame, text="Show password", variable=self.show_password, command=self._toggle_login_visibility).grid(row=4, column=0, sticky="w", pady=(0, 8))
        ttk.Checkbutton(self.form_frame, text="Remember me", variable=self.remember_me).grid(row=5, column=0, sticky="w", pady=(0, 8))
        ttk.Button(self.form_frame, text="Login", command=self.login).grid(row=6, column=0, sticky="ew", pady=(8, 6))
        ttk.Button(self.form_frame, text="Forgot password?", command=self.forgot_password).grid(row=7, column=0, sticky="ew")

    def _build_register_form(self) -> None:
        fields = [
            ("Full Name", "fullname"),
            ("Username", "username"),
            ("Email", "email"),
            ("Phone Number", "phone"),
            ("Password", "password"),
            ("Confirm Password", "confirm_password"),
        ]
        self.register_entries = {} 
        for index, (label_text, key) in enumerate(fields):
            ttk.Label(self.form_frame, text=label_text).grid(row=index, column=0, sticky="w", pady=(0, 4))
            entry = ttk.Entry(self.form_frame, show="*" if key in {"password", "confirm_password"} else "")
            entry.grid(row=index + 1, column=0, sticky="ew", pady=(0, 8))
            self.register_entries[key] = entry

        ttk.Label(self.form_frame, text="Role").grid(row=13, column=0, sticky="w", pady=(0, 4))
        self.role_var = tk.StringVar(value="Receptionist")
        role_box = ttk.Combobox(self.form_frame, textvariable=self.role_var, values=["Administrator", "Doctor", "Nurse", "Receptionist", "Pharmacist"], state="readonly")
        role_box.grid(row=14, column=0, sticky="ew", pady=(0, 8))

        ttk.Checkbutton(self.form_frame, text="Show password", variable=self.show_password, command=self._toggle_register_visibility).grid(row=15, column=0, sticky="w", pady=(0, 8))
        ttk.Button(self.form_frame, text="Register", command=self.register).grid(row=16, column=0, sticky="ew", pady=(8, 6))

    def _toggle_login_visibility(self) -> None:
        if self.show_password.get():
            self.login_password.config(show="")
        else:
            self.login_password.config(show="*")

    def _toggle_register_visibility(self) -> None:
        show = "" if self.show_password.get() else "*"
        for key in ("password", "confirm_password"):
            self.register_entries[key].config(show=show)

    def login(self) -> None:
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()
        if not username or not password:
            messagebox.showerror("Validation", "Please enter your username and password")
            return
        user = self.database.authenticate_user(username, password)
        if user:
            if self.remember_me.get():
                messagebox.showinfo("Session", "Credentials will be remembered for this session")
            self.on_authenticated(user)
        else:
            messagebox.showerror("Authentication failed", "Invalid username or password")

    def register(self) -> None:
        fullname = self.register_entries["fullname"].get().strip()
        username = self.register_entries["username"].get().strip()
        email = self.register_entries["email"].get().strip()
        phone = self.register_entries["phone"].get().strip()
        password = self.register_entries["password"].get().strip()
        confirm_password = self.register_entries["confirm_password"].get().strip()
        role = self.role_var.get()
        if not all([fullname, username, email, phone, password, confirm_password, role]):
            messagebox.showerror("Validation", "Please fill all registration fields")
            return
        if password != confirm_password:
            messagebox.showerror("Validation", "Password and confirmation do not match")
            return
        try:
            self.database.register_user(fullname, username, email, phone, password, role)
            messagebox.showinfo("Success", "Account created successfully. You can now log in.")
            self.set_mode("Login")
        except Exception as exc:  # pragma: no cover - widget error path
            messagebox.showerror("Registration failed", str(exc))

    def forgot_password(self) -> None:
        messagebox.showinfo("Password reset", "Please contact the administrator to reset your password")
