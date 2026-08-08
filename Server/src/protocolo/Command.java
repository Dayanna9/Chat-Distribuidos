package chat.protocolo;


public class Command {

    private final CommandType tipo;

    private final String argumento;

    private final String destino;


    public Command(CommandType tipo) {
        this.tipo = tipo;
        this.argumento = null;
        this.destino = null;
    }


    public Command(CommandType tipo, String argumento) {
        this.tipo = tipo;
        this.argumento = argumento;
        this.destino = null;
    }


    public Command(CommandType tipo, String destino, String argumento) {
        this.tipo = tipo;
        this.destino = destino;
        this.argumento = argumento;
    }

    public CommandType getTipo() {
        return tipo;
    }

    public String getArgumento() {
        return argumento;
    }

    public String getDestino() {
        return destino;
    }
}