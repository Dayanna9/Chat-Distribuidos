class Protocol:
    """Comandos compatibles con el servidor Java del proyecto."""

    LOGIN = "LOGIN"
    GROUP = "GROUP"
    PRIVATE = "PRIVATE"
    LIST = "LIST"
    EXIT = "EXIT"

    WELCOME = "WELCOME"
    JOIN = "JOIN"
    LEFT = "LEFT"
    USERS = "USERS"
    ERROR = "ERROR"
    INFO = "INFO"

    @staticmethod
    def login(usuario):
        return f"LOGIN|{usuario}"

    @staticmethod
    def group(mensaje):
        return f"GROUP|{mensaje}"

    @staticmethod
    def private(destinatario, mensaje):
        return f"PRIVATE|{destinatario}|{mensaje}"

    @staticmethod
    def users():
        return "LIST"

    @staticmethod
    def exit():
        return "EXIT"
