import tkinter as tk

class LoginPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("500x400")

        tk.Label(
            root,
            text="Smarter Health Connection Login",
            font=("Arial", 16, "bold")
        ).pack(pady=30)

        tk.Label(root, text="Username").pack()
        tk.Entry(root).pack()

        tk.Label(root, text="Password").pack()
        tk.Entry(root, show="*").pack()

        tk.Button(
            root,
            text="Login",
            width=20
        ).pack(pady=20)