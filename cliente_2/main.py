import tkinter as tk

from chat_client import ChatClient
from chat_window import ChatWindow
from name_window import NameWindow


class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.client = None
        self.chat_window = None
        self.name_window = None

    def run(self):
        self.name_window = NameWindow(
            self.root,
            self.start_connection
        )

        self.root.after(
            20,
            self._poll_network
        )

        self.root.mainloop()

    def start_connection(
        self,
        servidor,
        puerto,
        usuario,
        ventana_nombre
    ):
        self.client = ChatClient(
            servidor,
            puerto,
            on_connected=lambda: self._connected(
                usuario
            ),
            on_error=lambda mensaje: self._connection_error(
                mensaje,
                ventana_nombre
            )
        )

        self._usuario = usuario
        self._ventana_nombre = ventana_nombre

        self.client.connect()

    def _connected(self, usuario):
        self.client.send(
            f"LOGIN|{usuario}"
        )

        self.client.on_message = self._wait_for_welcome

    def _wait_for_welcome(self, mensaje):
        partes = mensaje.split("|", 2)

        if partes[0] == "WELCOME":
            usuario = (
                partes[1]
                if len(partes) >= 2
                else self._usuario
            )

            self.chat_window = ChatWindow(
                self.root,
                self.client,
                usuario,
                self.close_application
            )

            self.chat_window._procesar(mensaje)
            return

        if partes[0] == "INFO":
            return

        if partes[0] == "ERROR":
            texto = (
                partes[1]
                if len(partes) >= 2
                else "Error del servidor"
            )

            self._connection_error(
                texto,
                self._ventana_nombre
            )

    def _poll_network(self):
        if self.client:
            self.client.poll()

        if self.root.winfo_exists():
            self.root.after(
                20,
                self._poll_network
            )

    def _connection_error(
        self,
        mensaje,
        ventana_nombre
    ):
        if self.client:
            self.client.close()

        ventana_nombre.error(mensaje)

    def close_application(self):
        try:
            if self.client:
                self.client.close()
        finally:
            self.root.destroy()


if __name__ == "__main__":
    Application().run()