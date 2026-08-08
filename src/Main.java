package chat;

import chat.servidor.ChatServer;

public class Main {

    public static void main(String[] args) {


        int puerto = 5000;


        ChatServer servidor = new ChatServer(puerto);


        servidor.start();
    }
}