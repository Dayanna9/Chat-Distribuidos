package chat.servidor;

import chat.protocolo.Command;
import chat.protocolo.CommandParser;
import chat.protocolo.CommandType;

import java.util.concurrent.locks.ReentrantLock;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;


public class ChatServer {


    private final int port;

    private ServerSocketChannel serverChannel;


    private Selector selector;


    private final Map<SocketChannel, ClientConnection> clients;


    private final Map<String, ClientConnection> users;

    private final ReentrantLock lock;

    public ChatServer(int port) 
    {

        this.port = port;

        clients = new HashMap<>();

        users = new HashMap<>();

    
        lock = new ReentrantLock();
        }


    public void start() {

        try {

            selector = Selector.open();

            serverChannel = ServerSocketChannel.open();

            serverChannel.configureBlocking(false);

            serverChannel.bind(
                    new InetSocketAddress(port)
            );


            serverChannel.register(
                    selector,
                    SelectionKey.OP_ACCEPT
            );

            mostrarInicio();

            while (true) {


                selector.select();

                Iterator<SelectionKey> iterator =
                        selector.selectedKeys().iterator();

                while (iterator.hasNext()) {

                    SelectionKey key = iterator.next();

                    iterator.remove();

                    if (!key.isValid()) {
                        continue;
                    }

                    try {

                        if (key.isAcceptable()) {
                            acceptClient();
                        }

                        if (key.isReadable()) {
                            readClient(key);
                        }

                        if (key.isWritable()) {
                            writeClient(key);
                        }

                    } catch (IOException e) {

                        disconnectClient(key);
                    }
                }
            }

        } catch (IOException e) {

            System.err.println(
                    "Error iniciando el servidor: "
                            + e.getMessage()
            );

        } finally {

            stop();
        }
    }


    private void acceptClient() throws IOException {

        SocketChannel channel =
                serverChannel.accept();

        if (channel == null) {
            return;
        }


        channel.configureBlocking(false);

        SelectionKey key = channel.register(
                selector,
                SelectionKey.OP_READ
        );


        ClientConnection client =
                new ClientConnection(channel);

        key.attach(client);

        lock.lock();

        try {

                clients.put(channel, client);

        } finally {

                lock.unlock();
        }

        System.out.println();
        System.out.println(
                "[CONEXIÓN] Cliente conectado: "
                        + channel.getRemoteAddress()
        );

        System.out.println(
                "[INFO] Clientes conectados: "
                        + clients.size()
        );

        send(client,
                "INFO|Conectado al servidor");

        send(client,
                "INFO|Debes iniciar sesión usando LOGIN|nombre");

        activarEscritura(client);
    }


    private void readClient(SelectionKey key)
            throws IOException {

        ClientConnection client =
                (ClientConnection) key.attachment();

        SocketChannel channel =
                client.getChannel();

        ByteBuffer buffer =
                ByteBuffer.allocate(4096);

        int bytesLeidos;

        while ((bytesLeidos = channel.read(buffer)) > 0) {

            buffer.flip();

            byte[] datos = new byte[buffer.remaining()];

            buffer.get(datos);

            client.appendInput(
                    datos,
                    datos.length
            );

            buffer.clear();
        }

        if (bytesLeidos == -1) {

            disconnectClient(key);

            return;
        }

        String[] mensajes =
                client.getCompleteMessages();

        for (String mensaje : mensajes) {

            if (!mensaje.isBlank()) {

                System.out.println(
                        "[RECIBIDO] "
                                + obtenerNombre(client)
                                + ": "
                                + mensaje
                );

                processMessage(client, mensaje);
            }
        }
    }

    private void processMessage(
            ClientConnection client,
            String texto) {

        Command command =
                CommandParser.parse(texto);

        switch (command.getTipo()) {

            case LOGIN:
                processLogin(
                        client,
                        command.getArgumento()
                );
                break;

            case GROUP:
                processGroup(
                        client,
                        command.getArgumento()
                );
                break;

            case PRIVATE:
                processPrivate(
                        client,
                        command.getDestino(),
                        command.getArgumento()
                );
                break;

            case LIST:
                processList(client);
                break;

            case EXIT:
                disconnectClient(
                        findKey(client)
                );
                break;

            case UNKNOWN:
                send(
                        client,
                        "ERROR|Comando desconocido"
                );

                activarEscritura(client);
                break;
        }
    }

    private void processLogin(
        ClientConnection client,
        String username) {

    if (client.getUsername() != null) {

        send(
                client,
                "ERROR|Ya has iniciado sesión"
        );

        activarEscritura(client);

        return;
    }

    if (!validarUsername(username)) {

        send(
                client,
                "ERROR|Nombre de usuario inválido"
        );

        activarEscritura(client);

        return;
    }

    lock.lock();

    try {

        if (users.containsKey(username)) {

            send(
                    client,
                    "ERROR|El usuario ya está conectado"
            );

            activarEscritura(client);

            return;
        }

        client.setUsername(username);

        users.put(username, client);

        System.out.println(
                "[LOGIN] Usuario conectado: "
                        + username
        );

    } finally {

        lock.unlock();
    }

    send(
            client,
            "WELCOME|" + username
    );

    broadcast(
            "JOIN|" + username,
            client
    );

    broadcastUserList();

    activarEscritura(client);
}


    private void processGroup(
            ClientConnection sender,
            String mensaje) {

        if (!isLogged(sender)) {

            send(
                    sender,
                    "ERROR|Debes iniciar sesión primero"
            );

            activarEscritura(sender);

            return;
        }

        if (mensaje == null || mensaje.isBlank()) {

            send(
                    sender,
                    "ERROR|El mensaje está vacío"
            );

            activarEscritura(sender);

            return;
        }

        String mensajeServidor =
                "GROUP|"
                        + sender.getUsername()
                        + "|"
                        + mensaje;

        broadcast(
                mensajeServidor,
                null
        );

        System.out.println(
                "[GRUPO] "
                        + sender.getUsername()
                        + ": "
                        + mensaje
        );
    }

    private void processPrivate(
        ClientConnection sender,
        String destino,
        String mensaje) {

    if (!isLogged(sender)) {

        send(
                sender,
                "ERROR|Debes iniciar sesión primero"
        );

        activarEscritura(sender);

        return;
    }

    ClientConnection receptor;

    
    lock.lock();

    try {

        receptor = users.get(destino);

    } finally {

        lock.unlock();
    }

    if (receptor == null) {

        send(
                sender,
                "ERROR|El usuario no está conectado"
        );

        activarEscritura(sender);

        return;
    }

    if (receptor == sender) {

        send(
                sender,
                "ERROR|No puedes enviarte un mensaje a ti mismo"
        );

        activarEscritura(sender);

        return;
    }

    String mensajeServidor =
            "PRIVATE|"
                    + sender.getUsername()
                    + "|"
                    + mensaje;

    send(
            receptor,
            mensajeServidor
    );

    send(
            sender,
            mensajeServidor
    );

    activarEscritura(receptor);
    activarEscritura(sender);

    System.out.println(
            "[PRIVADO] "
                    + sender.getUsername()
                    + " -> "
                    + destino
                    + ": "
                    + mensaje
    );
}

    private void processList(
            ClientConnection client) {

        if (!isLogged(client)) {

            send(
                    client,
                    "ERROR|Debes iniciar sesión primero"
            );

            activarEscritura(client);

            return;
        }

        StringBuilder lista =
                new StringBuilder("USERS|");

        boolean primero = true;

        for (String username : users.keySet()) {

            if (!primero) {
                lista.append(",");
            }

            lista.append(username);

            primero = false;
        }

        send(
                client,
                lista.toString()
        );

        activarEscritura(client);
    }


        private List<ClientConnection> getClientsSnapshot() {

                lock.lock();

                try 
                {

                        return new ArrayList<>(
                                clients.values()
                        );

                } finally 
                {

                        lock.unlock();
                }
        }

    private void broadcast(
        String mensaje,
        ClientConnection excluir) {

    List<ClientConnection> clientes =
            getClientsSnapshot();

    for (ClientConnection client : clientes) {

        if (client == excluir) {
            continue;
        }

        if (!isLogged(client)) {
            continue;
        }

        send(
                client,
                mensaje
        );

        activarEscritura(client);
    }
}

    private void broadcastUserList() {

    List<String> nombres;

    lock.lock();

    try {

        nombres =
                new ArrayList<>(
                        users.keySet()
                );

    } finally {

        lock.unlock();
    }

    String lista =
            String.join(
                    ",",
                    nombres
            );

    broadcast(
            "USERS|" + lista,
            null
    );
}

    private void send(
            ClientConnection client,
            String mensaje) {

        client.queueMessage(mensaje);
    }

    private void activarEscritura(
            ClientConnection client) {

        SelectionKey key =
                client.getChannel().keyFor(selector);

        if (key == null || !key.isValid()) {
            return;
        }

        key.interestOps(
                key.interestOps()
                        | SelectionKey.OP_WRITE
        );
    }

    private void writeClient(
            SelectionKey key)
            throws IOException {

        ClientConnection client =
                (ClientConnection) key.attachment();

        client.writePendingMessages();

        if (!client.hasPendingMessages()) {

            key.interestOps(
                    key.interestOps()
                            & ~SelectionKey.OP_WRITE
            );
        }
    }

    private void disconnectClient(
        SelectionKey key) {

        if (key == null) {
                return;
        }

        ClientConnection client =
                (ClientConnection) key.attachment();

        if (client == null) {
                return;
        }

        String username =
                client.getUsername();


        lock.lock();

        try {

                if (username != null) {

                users.remove(username);

                System.out.println(
                        "[DESCONECTADO] "
                                + username
                );
                }

                clients.remove(
                        client.getChannel()
                );

        } finally {

                lock.unlock();
        }


        if (username != null) {

                broadcast(
                        "LEFT|" + username,
                        client
                );
        }

        key.cancel();

        client.close();

        System.out.println(
                "[INFO] Clientes conectados: "
                        + getClientCount()
        );

        broadcastUserList();
        }

        private int getClientCount() {

                lock.lock();

                try 
                {

                        return clients.size();

                }
                finally 
                {

                        lock.unlock();
                }
        }

        private SelectionKey findKey(
            ClientConnection client) {

        return client
                .getChannel()
                .keyFor(selector);
    }

    private boolean isLogged(
            ClientConnection client) {

        return client.getUsername() != null;
    }

    private String obtenerNombre(
            ClientConnection client) {

        if (client.getUsername() == null) {
            return "SIN_LOGIN";
        }

        return client.getUsername();
    }

    private boolean validarUsername(
            String username) {

        if (username == null) {
            return false;
        }

        username = username.trim();

        return username.matches(
                "[a-zA-Z0-9_]{3,20}"
        );
    }

    private void mostrarInicio() {

        System.out.println();
        System.out.println(
                "========================================"
        );

        System.out.println(
                "       SERVIDOR DE CHAT - JAVA"
        );

        System.out.println(
                "========================================"
        );

        System.out.println(
                "Puerto: " + port
        );

        System.out.println(
                "Modo: Java NIO / No bloqueante"
        );

        System.out.println(
                "Esperando clientes..."
        );

        System.out.println(
                "========================================"
        );

        System.out.println();
    }

    private void stop() {

        try {

            if (serverChannel != null) {
                serverChannel.close();
            }

            if (selector != null) {
                selector.close();
            }

        } catch (IOException ignored) {
        }
    }
}