# Procesos, Hilos y Sincronización - Caso Práctico

## Solicitud del laboratorio

1. Desarrollar un programa para comunicación por chat, con sockets, no bloqueantes, para conversación de grupo y privada.
2. Explicar detalladamente la relevancia de la sincronización en sistemas distribuidos.
3. Identificar y describir diversas tipologías de sincronización.
4. Elaborar un cuadro comparativo de técnicas de sincronización e implementar una de ellas con su mecanismo de bloqueo.
5. Describir una implementación donde la sincronización sea el core.
6. Leer la lectura complementaria 3.
7. Diseñar una presentación ejecutiva de máximo 7 minutos que demuestre la aplicación práctica de los conceptos.

## Implementación del proyecto

### Servidor

- Lenguaje: Java.
- Sistema: Linux.
- Puerto: 5000.
- Comunicación: TCP.
- Modelo: Java NIO.
- `ServerSocketChannel`.
- `SocketChannel`.
- `Selector`.
- Canales configurados como no bloqueantes.
- `ReentrantLock` para proteger las estructuras compartidas `clients` y `users`.

### Cliente 1

- Lenguaje: C#.
- Interfaz gráfica: Windows Forms.
- Sistema: Windows.

### Cliente 2

- Lenguaje: Python.
- Sistema: Linux.
- Interfaz gráfica: Tkinter.
- Comunicación TCP no bloqueante.
- `selectors`.
- Chat grupal y privado.

## Protocolo

LOGIN|usuario
GROUP|mensaje
PRIVATE|destinatario|mensaje
LIST
EXIT

## Respuestas del servidor

WELCOME|usuario
JOIN|usuario
LEFT|usuario
USERS|usuario1,usuario2
GROUP|remitente|mensaje
PRIVATE|remitente|mensaje
ERROR|mensaje
INFO|mensaje

## Sincronización

La técnica implementada en el servidor es exclusión mutua mediante `ReentrantLock`.

El recurso compartido está compuesto principalmente por:

- `Map<SocketChannel, ClientConnection> clients`
- `Map<String, ClientConnection> users`

El lock evita que operaciones concurrentes modifiquen estas estructuras de forma insegura.

## Relación con procesos e hilos

El servidor gestiona múltiples conexiones mediante Java NIO y un `Selector`, evitando un bloqueo individual por cliente.

El cliente Python utiliza la interfaz gráfica como hilo principal y consulta periódicamente el `Selector` mediante `after()`, evitando bloquear la interfaz mientras espera datos de red.

## Resultado

La arquitectura permite:

Cliente C# ──┐
            ├──> Servidor Java ──> recursos compartidos protegidos
Cliente Python ┘

Los dos clientes pueden:

- conectarse al servidor,
- registrarse con un nombre,
- consultar usuarios,
- enviar mensajes grupales,
- enviar mensajes privados,
- desconectarse correctamente.
