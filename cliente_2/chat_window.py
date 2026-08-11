import tkinter as tk

from protocol import Protocol


class ChatWindow:

    def __init__(
        self,
        root,
        client,
        usuario,
        on_close
    ):
        self.root = root
        self.client = client
        self.usuario = usuario
        self.on_close = on_close

        self.private_windows = {}

        self._build()

        self.client.on_message = self._on_message
        self.client.on_disconnected = self._on_disconnected
        self.client.on_error = self._on_error

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self._close
        )

        self.root.after(
            100,
            self._request_users
        )

    def _build(self):

        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.title(
            f"Chat - {self.usuario}"
        )

        self.root.geometry(
            "850x600"
        )

        self.root.minsize(
            700,
            500
        )

        self.root.configure(
            bg="white"
        )

        self.lbl_usuario = tk.Label(
            self.root,
            text=self.usuario,
            font=("Segoe UI", 12, "bold"),
            anchor="w",
            bg="white"
        )

        self.lbl_usuario.pack(
            side="top",
            fill="x",
            padx=(15, 0),
            pady=(8, 0),
            ipady=7
        )

        panel_usuarios = tk.Frame(
            self.root,
            width=180,
            bg="white",
            padx=5,
            pady=5
        )

        panel_usuarios.pack(
            side="right",
            fill="y"
        )

        panel_usuarios.pack_propagate(False)

        tk.Label(
            panel_usuarios,
            text="Usuarios conectados",
            bg="white"
        ).pack(
            fill="x",
            pady=(0, 5)
        )

        self.lista_usuarios = tk.Listbox(
            panel_usuarios,
            exportselection=False
        )

        self.lista_usuarios.pack(
            fill="both",
            expand=True
        )

        self.lista_usuarios.bind(
            "<Double-Button-1>",
            self._usuario_seleccionado
        )

        self.lista_usuarios.bind(
            "<ButtonRelease-1>",
            self._usuario_seleccionado
        )

        panel_inferior = tk.Frame(
            self.root,
            height=70,
            bg="white",
            padx=10,
            pady=10
        )

        panel_inferior.pack(
            side="bottom",
            fill="x"
        )

        panel_inferior.pack_propagate(False)

        self.btn_enviar = tk.Button(
            panel_inferior,
            text="Send",
            command=self._enviar
        )

        self.btn_enviar.pack(
            side="right",
            fill="y"
        )

        self.txt_mensaje = tk.Entry(
            panel_inferior,
            font=("Segoe UI", 11)
        )

        self.txt_mensaje.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 5)
        )

        self.txt_mensaje.bind(
            "<Return>",
            lambda event: self._enviar()
        )

        panel_chat = tk.Frame(
            self.root,
            bg="white",
            padx=10,
            pady=10
        )

        panel_chat.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.txt_conversacion = tk.Text(
            panel_chat,
            font=("Segoe UI", 10),
            wrap="word",
            state="disabled"
        )

        self.txt_conversacion.pack(
            side="top",
            fill="both",
            expand=True
        )

        self.lbl_destino = tk.Label(
            panel_chat,
            text="Chat grupal",
            anchor="w",
            bg="white"
        )

        self.lbl_destino.pack(
            side="bottom",
            fill="x"
        )

        self.txt_mensaje.focus_set()

    def _request_users(self):

        if self.client.connected:
            self.client.send(
                Protocol.users()
            )

    def _usuario_seleccionado(
        self,
        event=None
    ):

        seleccion = (
            self.lista_usuarios.curselection()
        )

        if not seleccion:
            return

        seleccionado = (
            self.lista_usuarios.get(
                seleccion[0]
            )
        )

        if seleccionado == self.usuario:
            return

        self._abrir_chat_privado(
            seleccionado
        )

    def _abrir_chat_privado(
        self,
        usuario_destino
    ):

        if usuario_destino in self.private_windows:

            ventana = self.private_windows[
                usuario_destino
            ]

            try:
                ventana.lift()
                ventana.focus_force()
                return
            except tk.TclError:
                del self.private_windows[
                    usuario_destino
                ]

        ventana = PrivateChatWindow(
            self.root,
            self.client,
            self.usuario,
            usuario_destino,
            self._cerrar_ventana_privada
        )

        self.private_windows[
            usuario_destino
        ] = ventana

    def _cerrar_ventana_privada(
        self,
        usuario_destino
    ):

        if usuario_destino in self.private_windows:

            del self.private_windows[
                usuario_destino
            ]

    def _enviar(self):

        mensaje = (
            self.txt_mensaje.get().strip()
        )

        if not mensaje:
            return

        if not self.client.connected:
            return

        self.client.send(
            Protocol.group(
                mensaje
            )
        )

        self._agregar(
            f"{self.usuario}: {mensaje}"
        )

        self.txt_mensaje.delete(
            0,
            tk.END
        )

        self.txt_mensaje.focus_set()

    def _on_message(
        self,
        mensaje
    ):

        self.root.after(
            0,
            lambda: self._procesar(mensaje)
        )

    def _procesar(
        self,
        mensaje
    ):

        partes = mensaje.split(
            "|",
            2
        )

        tipo = partes[0]

        if tipo == Protocol.INFO:

            if len(partes) >= 2:

                self._agregar(
                    f"[Servidor] {partes[1]}"
                )

        elif tipo == Protocol.WELCOME:

            if len(partes) >= 2:

                self._agregar(
                    f"Conectado como {partes[1]}"
                )

        elif tipo == Protocol.USERS:

            if len(partes) >= 2:

                self._actualizar_usuarios(
                    partes[1]
                )

        elif tipo == Protocol.JOIN:

            if len(partes) >= 2:

                self._agregar(
                    f"[Servidor] {partes[1]} se conectó"
                )

                self._request_users()

        elif tipo == Protocol.LEFT:

            if len(partes) >= 2:

                self._agregar(
                    f"[Servidor] {partes[1]} se desconectó"
                )

                self._request_users()

        elif tipo == Protocol.GROUP:

            if len(partes) >= 3:

                remitente = partes[1]
                mensaje_texto = partes[2]

                if remitente != self.usuario:

                    self._agregar(
                        f"{remitente}: {mensaje_texto}"
                    )

        elif tipo == Protocol.PRIVATE:

            if len(partes) >= 3:

                remitente = partes[1]
                mensaje_texto = partes[2]

                # El servidor confirma el privado devolviéndolo también al
                # emisor. Esa copia ya se muestra al enviar, por lo que no se
                # debe abrir un chat privado consigo mismo.
                if remitente == self.usuario:
                    return

                ventana = (
                    self._obtener_chat_privado(
                        remitente
                    )
                )

                ventana.recibir_mensaje(
                    remitente,
                    mensaje_texto
                )

        elif tipo == Protocol.ERROR:

            if len(partes) >= 2:

                self._agregar(
                    f"[Servidor] {partes[1]}"
                )

    def _actualizar_usuarios(
        self,
        texto
    ):

        self.lista_usuarios.delete(
            0,
            tk.END
        )

        usuarios = [
            usuario.strip()
            for usuario in texto.split(",")
            if usuario.strip()
        ]

        for usuario in usuarios:

            self.lista_usuarios.insert(
                tk.END,
                usuario
            )

    def _obtener_chat_privado(
        self,
        usuario_destino
    ):

        if usuario_destino in self.private_windows:

            return self.private_windows[
                usuario_destino
            ]

        ventana = PrivateChatWindow(
            self.root,
            self.client,
            self.usuario,
            usuario_destino,
            self._cerrar_ventana_privada
        )

        self.private_windows[
            usuario_destino
        ] = ventana

        return ventana

    def _agregar(
        self,
        texto
    ):

        self.txt_conversacion.config(
            state="normal"
        )

        self.txt_conversacion.insert(
            tk.END,
            texto + "\n"
        )

        self.txt_conversacion.see(
            tk.END
        )

        self.txt_conversacion.config(
            state="disabled"
        )

    def _on_disconnected(
        self
    ):

        self.root.after(
            0,
            self._desconectado
        )

    def _desconectado(
        self
    ):

        self._agregar(
            "[Servidor] Conexión perdida"
        )

        self.btn_enviar.config(
            state="disabled"
        )

    def _on_error(
        self,
        mensaje
    ):

        self.root.after(
            0,
            lambda: self._agregar(
                f"[Error] {mensaje}"
            )
        )

    def _close(self):

        try:

            self.client.close(
                send_exit=True
            )

        finally:

            self.on_close()


class PrivateChatWindow:

    def __init__(
        self,
        root,
        client,
        usuario_local,
        usuario_destino,
        on_close
    ):

        self.root = root
        self.client = client

        self.usuario_local = usuario_local
        self.usuario_destino = usuario_destino

        self.on_close = on_close

        self.window = tk.Toplevel(
            root
        )

        self.window.title(
            f"Chat - {usuario_destino}"
        )

        self.window.geometry(
            "850x600"
        )

        self.window.minsize(
            700,
            500
        )

        self.window.configure(
            bg="white"
        )

        self._build()

        self.window.protocol(
            "WM_DELETE_WINDOW",
            self._close
        )

    def _build(self):

        tk.Label(
            self.window,
            text=self.usuario_destino,
            font=("Segoe UI", 12, "bold"),
            anchor="w",
            bg="white"
        ).pack(
            side="top",
            fill="x",
            padx=(15, 0),
            pady=(8, 0),
            ipady=7
        )

        panel_derecho = tk.Frame(
            self.window,
            width=180,
            bg="white",
            padx=5,
            pady=5
        )

        panel_derecho.pack(
            side="right",
            fill="y"
        )

        panel_derecho.pack_propagate(
            False
        )

        tk.Label(
            panel_derecho,
            text="Usuario",
            bg="white"
        ).pack(
            fill="x",
            pady=(0, 5)
        )

        lista = tk.Listbox(
            panel_derecho
        )

        lista.pack(
            fill="both",
            expand=True
        )

        lista.insert(
            tk.END,
            self.usuario_destino
        )

        panel_inferior = tk.Frame(
            self.window,
            height=70,
            bg="white",
            padx=10,
            pady=10
        )

        panel_inferior.pack(
            side="bottom",
            fill="x"
        )

        panel_inferior.pack_propagate(
            False
        )

        self.btn_enviar = tk.Button(
            panel_inferior,
            text="Send",
            command=self._enviar
        )

        self.btn_enviar.pack(
            side="right",
            fill="y"
        )

        self.txt_mensaje = tk.Entry(
            panel_inferior,
            font=("Segoe UI", 11)
        )

        self.txt_mensaje.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 5)
        )

        self.txt_mensaje.bind(
            "<Return>",
            lambda event: self._enviar()
        )

        panel_chat = tk.Frame(
            self.window,
            bg="white",
            padx=10,
            pady=10
        )

        panel_chat.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.txt_conversacion = tk.Text(
            panel_chat,
            font=("Segoe UI", 10),
            wrap="word",
            state="disabled"
        )

        self.txt_conversacion.pack(
            side="top",
            fill="both",
            expand=True
        )

        tk.Label(
            panel_chat,
            text=f"Chat privado con {self.usuario_destino}",
            anchor="w",
            bg="white"
        ).pack(
            side="bottom",
            fill="x"
        )

        self.txt_mensaje.focus_set()

    def _enviar(self):

        mensaje = (
            self.txt_mensaje.get().strip()
        )

        if not mensaje:
            return

        if not self.client.connected:
            return

        self.client.send(
            Protocol.private(
                self.usuario_destino,
                mensaje
            )
        )

        self._agregar(
            f"{self.usuario_local}: {mensaje}"
        )

        self.txt_mensaje.delete(
            0,
            tk.END
        )

        self.txt_mensaje.focus_set()

    def recibir_mensaje(
        self,
        remitente,
        mensaje
    ):

        self._agregar(
            f"{remitente}: {mensaje}"
        )

        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()

    def _agregar(
        self,
        texto
    ):

        self.txt_conversacion.config(
            state="normal"
        )

        self.txt_conversacion.insert(
            tk.END,
            texto + "\n"
        )

        self.txt_conversacion.see(
            tk.END
        )

        self.txt_conversacion.config(
            state="disabled"
        )

    def _close(self):

        self.on_close(
            self.usuario_destino
        )

        self.window.destroy()
