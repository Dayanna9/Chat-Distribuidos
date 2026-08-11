import errno
import selectors
import socket


class ChatClient:
    """
    Cliente TCP NO BLOQUEANTE.
    Usa socket.setblocking(False) y selectors.
    No utiliza un socket bloqueante para esperar mensajes.
    """

    def __init__(
        self,
        host,
        port,
        on_message=None,
        on_connected=None,
        on_disconnected=None,
        on_error=None
    ):
        self.host = host
        self.port = port

        self.socket = None
        self.selector = selectors.DefaultSelector()

        self.connected = False
        self.connecting = False

        self.on_message = on_message
        self.on_connected = on_connected
        self.on_disconnected = on_disconnected
        self.on_error = on_error

        self.input_buffer = ""
        self.output_buffer = ""

    def connect(self):
        try:
            self.socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            self.socket.setblocking(False)

            resultado = self.socket.connect_ex(
                (self.host, self.port)
            )

            if resultado == 0:
                self._connection_completed()
                return

            if resultado in (
                errno.EINPROGRESS,
                errno.EWOULDBLOCK,
                errno.EALREADY,
                10035
            ):
                self.connecting = True

                self.selector.register(
                    self.socket,
                    selectors.EVENT_WRITE,
                    self._socket_event
                )
                return

            raise OSError(
                resultado,
                "No se pudo iniciar la conexión"
            )

        except Exception as exc:
            self._error(str(exc))
            self.close()

    def poll(self):
        """
        Revisa eventos de red sin bloquear.
        La interfaz Tkinter llama este método periódicamente.
        """
        if self.socket is None:
            return

        try:
            eventos = self.selector.select(timeout=0)

            for key, mask in eventos:
                callback = key.data
                callback(mask)

        except (OSError, ValueError) as exc:
            if self.connected or self.connecting:
                self._error(str(exc))
                self.close()

    def _socket_event(self, mask):
        if self.socket is None:
            return

        if self.connecting:
            error = self.socket.getsockopt(
                socket.SOL_SOCKET,
                socket.SO_ERROR
            )

            if error != 0:
                self._error(
                    f"No fue posible conectar. Código: {error}"
                )
                self.close()
                return

            self._connection_completed()

        if self.connected and (mask & selectors.EVENT_READ):
            self._receive()

        if self.connected and (mask & selectors.EVENT_WRITE):
            self._flush_output()

    def _connection_completed(self):
        self.connecting = False
        self.connected = True

        try:
            self.selector.unregister(self.socket)
        except Exception:
            pass

        self.selector.register(
            self.socket,
            selectors.EVENT_READ,
            self._socket_event
        )

        if self.on_connected:
            self.on_connected()

    def send(self, message):
        if not self.connected or self.socket is None:
            return False

        self.output_buffer += message + "\n"

        try:
            self._flush_output()
            return True
        except Exception as exc:
            self._error(str(exc))
            self.close()
            return False

    def _flush_output(self):
        if not self.connected or self.socket is None:
            return

        if not self.output_buffer:
            self._set_events(
                read=True,
                write=False
            )
            return

        data = self.output_buffer.encode("utf-8")

        try:
            cantidad = self.socket.send(data)

            if cantidad > 0:
                self.output_buffer = (
                    self.output_buffer[cantidad:]
                )

            self._set_events(
                read=True,
                write=bool(self.output_buffer)
            )

        except BlockingIOError:
            self._set_events(
                read=True,
                write=True
            )

    def _receive(self):
        if self.socket is None:
            return

        try:
            data = self.socket.recv(4096)

            if not data:
                self.close()
                return

            self.input_buffer += data.decode(
                "utf-8",
                errors="replace"
            )

            while "\n" in self.input_buffer:
                mensaje, self.input_buffer = (
                    self.input_buffer.split("\n", 1)
                )

                mensaje = mensaje.rstrip("\r")

                if mensaje.strip() and self.on_message:
                    self.on_message(mensaje)

        except BlockingIOError:
            pass

        except OSError as exc:
            self._error(str(exc))
            self.close()

    def _set_events(self, read=True, write=False):
        if self.socket is None:
            return

        events = 0

        if read:
            events |= selectors.EVENT_READ

        if write:
            events |= selectors.EVENT_WRITE

        try:
            self.selector.modify(
                self.socket,
                events,
                self._socket_event
            )
        except (KeyError, ValueError):
            pass

    def close(self, send_exit=False):
        estaba_activo = (
            self.connected or self.connecting
        )

        if send_exit and self.connected:
            try:
                self.send("EXIT")
            except Exception:
                pass

        self.connected = False
        self.connecting = False

        if self.socket is not None:
            try:
                self.selector.unregister(self.socket)
            except Exception:
                pass

            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass

            try:
                self.socket.close()
            except Exception:
                pass

            self.socket = None

        if estaba_activo and self.on_disconnected:
            self.on_disconnected()

    def _error(self, message):
        if self.on_error:
            self.on_error(message)
