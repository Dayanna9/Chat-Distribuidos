import tkinter as tk
from tkinter import messagebox

from config import HOST, PORT


class NameWindow:

    def __init__(self, root, on_enter):
        self.root = root
        self.on_enter = on_enter

        self.root.title("Chat - Conexión")
        self.root.geometry("400x330")
        self.root.resizable(False, False)
        self.root.configure(bg="white")

        self._build()

    def _build(self):

        title = tk.Label(
            self.root,
            text="CHAT",
            font=("Segoe UI", 18, "bold"),
            bg="white"
        )
        title.place(x=155, y=25)

        tk.Label(
            self.root,
            text="Servidor:",
            bg="white"
        ).place(x=40, y=85)

        self.txt_servidor = tk.Entry(self.root)
        self.txt_servidor.insert(0, HOST)
        self.txt_servidor.place(
            x=120, y=82,
            width=210,
            height=25
        )

        tk.Label(
            self.root,
            text="Puerto:",
            bg="white"
        ).place(x=40, y=125)

        self.txt_puerto = tk.Entry(self.root)
        self.txt_puerto.insert(0, str(PORT))
        self.txt_puerto.place(
            x=120, y=122,
            width=210,
            height=25
        )

        tk.Label(
            self.root,
            text="Usuario:",
            bg="white"
        ).place(x=40, y=165)

        self.txt_usuario = tk.Entry(self.root)
        self.txt_usuario.place(
            x=120, y=162,
            width=210,
            height=25
        )

        self.btn_conectar = tk.Button(
            self.root,
            text="Conectar",
            command=self._conectar
        )
        self.btn_conectar.place(
            x=130, y=210,
            width=120,
            height=35
        )

        self.lbl_estado = tk.Label(
            self.root,
            text="",
            bg="white"
        )
        self.lbl_estado.place(
            x=40,
            y=260
        )

        self.txt_usuario.focus_set()

        self.root.bind(
            "<Return>",
            lambda event: self._conectar()
        )

    def _conectar(self):

        servidor = self.txt_servidor.get().strip()
        puerto_texto = self.txt_puerto.get().strip()
        usuario = self.txt_usuario.get().strip()

        if not usuario:
            messagebox.showwarning(
                "Usuario",
                "Debes escribir un usuario."
            )
            return

        try:
            puerto = int(puerto_texto)
        except ValueError:
            messagebox.showwarning(
                "Puerto",
                "El puerto no es válido."
            )
            return

        self.btn_conectar.config(
            state="disabled"
        )

        self.lbl_estado.config(
            text="Conectando..."
        )

        self.on_enter(
            servidor,
            puerto,
            usuario,
            self
        )

    def error(self, mensaje):

        self.btn_conectar.config(
            state="normal"
        )

        self.lbl_estado.config(
            text="Error de conexión."
        )

        messagebox.showerror(
            "Error",
            mensaje
        )