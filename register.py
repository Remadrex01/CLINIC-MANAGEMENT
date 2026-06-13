"""
Smarter Health Connection — Register Module
=============================================
Full registration page with validation.
"""

import re
import tkinter as tk
from tkinter import messagebox, ttk
from database import Database
from utils import C, F, SHCButton, SHCEntry


class RegisterWindow(tk.Tk):
    def __init__(self, on_success_callback):
        super().__init__()
        self.on_success_callback = on_success_callback
        self.db = Database()

        self.title("Smarter Health Connection - Register")
        self.geometry("900x700")
        self.configure(bg=C["primary"])
        self.minsize(800, 600)
        self._center_window()

        self.fullname_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.gender_var = tk.StringVar()
        self.dob_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.role_var = tk.StringVar(value="Receptionist")
        self.pwd_var = tk.StringVar()
        self.confirm_pwd_var = tk.StringVar()

        self._build_ui()

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        card = tk.Frame(self, bg=C["white"], padx=40, pady=20)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="🏥 Register Account", font=F["title"], bg=C["white"], fg=C["primary"]).pack(pady=(0, 20))

        form = tk.Frame(card, bg=C["white"])
        form.pack(fill="both", expand=True)

        # Helper to create fields
        def make_field(parent, label, var, row, col, width=25, show="", values=None):
            f = tk.Frame(parent, bg=C["white"])
            f.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            tk.Label(f, text=label, font=F["label"], bg=C["white"], fg=C["text"]).pack(anchor="w")
            e = SHCEntry(f, var, show=show, values=values, width=width)
            e.pack(fill="x")

        make_field(form, "Full Name *", self.fullname_var, 0, 0)
        make_field(form, "Username *", self.username_var, 0, 1)
        
        make_field(form, "Email *", self.email_var, 1, 0)
        make_field(form, "Phone Number *", self.phone_var, 1, 1)

        make_field(form, "Gender *", self.gender_var, 2, 0, values=["Male", "Female", "Other"])
        make_field(form, "Date of Birth (YYYY-MM-DD)", self.dob_var, 2, 1)

        make_field(form, "Address", self.address_var, 3, 0)
        make_field(form, "Role *", self.role_var, 3, 1, values=["Administrator", "Doctor", "Nurse", "Receptionist", "Pharmacist"])

        make_field(form, "Password *", self.pwd_var, 4, 0, show="*")
        make_field(form, "Confirm Password *", self.confirm_pwd_var, 4, 1, show="*")

        # Buttons
        btns = tk.Frame(card, bg=C["white"])
        btns.pack(fill="x", pady=(20, 0))

        SHCButton(btns, "Register", self._register, style="success").pack(side="right", padx=5)
        SHCButton(btns, "Clear Form", self._clear, style="warning").pack(side="right", padx=5)
        SHCButton(btns, "Back to Login", self._back_to_login, style="secondary").pack(side="left", padx=5)

    def _clear(self):
        for var in (self.fullname_var, self.username_var, self.email_var, self.phone_var, 
                    self.gender_var, self.dob_var, self.address_var, self.pwd_var, self.confirm_pwd_var):
            var.set("")
        self.role_var.set("Receptionist")

    def _back_to_login(self):
        self.destroy()
        from login import LoginWindow
        app = LoginWindow(self.on_success_callback)
        app.mainloop()

    def _validate(self):
        if not all([self.fullname_var.get(), self.username_var.get(), self.email_var.get(), 
                    self.phone_var.get(), self.gender_var.get(), self.role_var.get(), 
                    self.pwd_var.get(), self.confirm_pwd_var.get()]):
            messagebox.showerror("Error", "Please fill all required fields (*).")
            return False
        
        email = self.email_var.get()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Error", "Invalid email format.")
            return False
            
        pwd = self.pwd_var.get()
        if len(pwd) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters.")
            return False
            
        if pwd != self.confirm_pwd_var.get():
            messagebox.showerror("Error", "Passwords do not match.")
            return False
            
        return True

    def _register(self):
        if not self._validate():
            return
            
        success, msg = self.db.create_user(
            self.fullname_var.get().strip(),
            self.username_var.get().strip(),
            self.email_var.get().strip(),
            self.phone_var.get().strip(),
            self.gender_var.get().strip(),
            self.dob_var.get().strip(),
            self.address_var.get().strip(),
            self.role_var.get().strip(),
            self.pwd_var.get()
        )
        
        if success:
            messagebox.showinfo("Success", msg)
            self._back_to_login()
        else:
            messagebox.showerror("Registration Failed", msg)

