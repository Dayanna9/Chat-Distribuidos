package chat.servidor;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.SocketChannel;
import java.nio.charset.StandardCharsets;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Queue;

public class ClientConnection {

    private final SocketChannel channel;

    private String username;


    private final ByteArrayOutputStream inputBuffer;


    private final Queue<ByteBuffer> outputQueue;

    public ClientConnection(SocketChannel channel) {

        this.channel = channel;

        this.username = null;

        this.inputBuffer = new ByteArrayOutputStream();

        this.outputQueue = new ArrayDeque<>();
    }

    public SocketChannel getChannel() {
        return channel;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public void appendInput(byte[] datos, int cantidad)
            throws IOException {

        inputBuffer.write(datos, 0, cantidad);
    }

    public String[] getCompleteMessages() {

        byte[] datos = inputBuffer.toByteArray();

        ArrayList<String> mensajes = new ArrayList<>();

        int inicio = 0;

        for (int i = 0; i < datos.length; i++) {

            if (datos[i] == '\n') {

                int longitud = i - inicio;

                String mensaje = new String(
                        datos,
                        inicio,
                        longitud,
                        StandardCharsets.UTF_8
                );

                mensaje = mensaje.replace("\r", "");

                mensajes.add(mensaje);

                inicio = i + 1;
            }
        }


        if (inicio > 0) {

            inputBuffer.reset();

            inputBuffer.write(
                    datos,
                    inicio,
                    datos.length - inicio
            );
        }

        return mensajes.toArray(new String[0]);
    }

    public void queueMessage(String mensaje) {

        String mensajeCompleto = mensaje + "\n";

        ByteBuffer buffer = ByteBuffer.wrap(
                mensajeCompleto.getBytes(StandardCharsets.UTF_8)
        );

        outputQueue.add(buffer);
    }


    public void writePendingMessages() throws IOException {

        while (!outputQueue.isEmpty()) {

            ByteBuffer buffer = outputQueue.peek();

            channel.write(buffer);

            if (buffer.hasRemaining()) {
                return;
            }

            outputQueue.poll();
        }
    }

    public boolean hasPendingMessages() {
        return !outputQueue.isEmpty();
    }

    public void close() {

        try {
            channel.close();
        } catch (IOException ignored) {
        }
    }
}