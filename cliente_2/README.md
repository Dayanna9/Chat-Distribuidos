# Cliente 2 - Python / Linux

Este cliente corresponde al segundo cliente del proyecto de Sistemas Distribuidos.

## Características

- Interfaz gráfica con Tkinter.
- El usuario solamente escribe su nombre.
- No existe una pantalla de inicio de sesión separada.
- Al entrar, el cliente envía automáticamente `LOGIN|nombre`.
- Chat grupal.
- Chat privado seleccionando un usuario.
- Lista de usuarios conectados.
- TCP.
- Socket no bloqueante.
- `selectors` para multiplexación de eventos.
- Compatible con el servidor Java existente.

## Estructura

cliente_2/
├── main.py
├── config.py
├── protocol.py
├── chat_client.py
├── name_window.py
├── chat_window.py
└── README.md

## Configuración

En `config.py`:

HOST = "127.0.0.1"
PORT = 5000

Si el servidor está en otra máquina Linux, reemplaza HOST por la IP del servidor.

## Ejecutar en Debian/Linux

Verificar Python:

python3 --version

Verificar Tkinter:

python3 -m tkinter

Si no está instalado:

sudo apt update
sudo apt install python3-tk

Ejecutar:

python3 main.py
