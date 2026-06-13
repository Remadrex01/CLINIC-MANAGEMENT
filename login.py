"""
Smarter Health Connection — Login Module
==========================================
Modern, centered login card with blue/white theme.
"""

import tkinter as tk
from tkinter import messagebox
from database import Database
from utils import C, F, SHCButton, SHCEntry


class LoginWindow(tk.Tk):
    def __init__(self, on_success_callback):
        super().__init__()
        self.on_success_callback = on_success_callback
        self.db = Database()

        self.title("Smarter Health Connection - Login")
        self.geometry("900x600")
        self.configure(bg=C["primary"])
        self.minsize(800, 500)
        self._center_window()

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.show_pwd_var = tk.BooleanVar(value=False)
        self.remember_var = tk.BooleanVar(value=False)

        self._build_ui()

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        # Center card
        card = tk.Frame(self, bg=C["white"], padx=40, pady=40)
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Logo / Title
        tk.Label(card, text="🏥", font=("Segoe UI", 48), bg=C["white"], fg=C["primary"]).pack()
        tk.Label(card, text="SMARTER HEALTH CONNECTION", font=F["title"], bg=C["white"], fg=C["primary"]).pack(pady=(10, 5))
        tk.Label(card, text="Welcome Back. Please log in to your account.", font=F["body"], bg=C["white"], fg=C["text2"]).pack(pady=(0, 20))

        # Form
        form = tk.Frame(card, bg=C["white"])
        form.pack(fill="x")

        # Username
        tk.Label(form, text="Username", font=F["label"], bg=C["white"], fg=C["text"]).pack(anchor="w")
        self.user_entry = SHCEntry(form, self.username_var, icon="👤", width=35)
        self.user_entry.pack(fill="x", pady=(5, 15))

        # Password
        tk.Label(form, text="Password", font=F["label"], bg=C["white"], fg=C["text"]).pack(anchor="w")
        self.pwd_entry = SHCEntry(form, self.password_var, icon="🔒", show="*", width=35)
        self.pwd_entry.pack(fill="x", pady=(5, 5))

        # Options row (Remember me + Show pwd + Forgot)
        opts = tk.Frame(form, bg=C["white"])
        opts.pack(fill="x", pady=(0, 20))
        
        tk.Checkbutton(opts, text="Remember Me", variable=self.remember_var, font=F["small"], bg=C["white"], fg=C["text"], activebackground=C["white"], selectcolor=C["white"]).pack(side="left")
        tk.Checkbutton(opts, text="Show", variable=self.show_pwd_var, command=self._toggle_pwd, font=F["small"], bg=C["white"], fg=C["text"], activebackground=C["white"], selectcolor=C["white"]).pack(side="left", padx=10)
        
        lbl_forgot = tk.Label(opts, text="Forgot Password?", font=F["small"], bg=C["white"], fg=C["accent"], cursor="hand2")
        lbl_forgot.pack(side="right")
        lbl_forgot.bind("<Button-1>", lambda e: messagebox.showinfo("Forgot Password", "Please contact the system administrator to reset your password."))

        # Login button
        SHCButton(form, "Login", self._login, style="primary", width=30).pack(fill="x", pady=(0, 10))

        # Register button
        SHCButton(form, "Register New Account", self._register, style="secondary", width=30).pack(fill="x", pady=(0, 10))

        # Google button
        btn_google = tk.Button(form, text="G  Continue with Google", command=self._google_login, font=F["btn"], bg=C["white"], fg=C["text"], relief="solid", bd=1, cursor="hand2", pady=8)
        btn_google.pack(fill="x", pady=(0, 15))

        # Exit button
        lbl_exit = tk.Label(card, text="Exit Application", font=F["btn"], bg=C["white"], fg=C["danger"], cursor="hand2")
        lbl_exit.pack()
        lbl_exit.bind("<Button-1>", lambda e: self.destroy())
        
        self.bind("<Return>", lambda e: self._login())

    def _toggle_pwd(self):
        self.pwd_entry._widget.config(show="" if self.show_pwd_var.get() else "*")

    def _login(self):
        user = self.username_var.get().strip()
        pwd = self.password_var.get()

        if not user or not pwd:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        user_data = self.db.authenticate(user, pwd)
        if user_data:
            self.destroy()
            self.on_success_callback(user_data)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def _register(self):
        self.destroy()
        from register import RegisterWindow
        app = RegisterWindow(self.on_success_callback)
        app.mainloop()

    def _google_login(self):
        messagebox.showinfo("Google Login", "Google OAuth integration is simulated in this version.")

