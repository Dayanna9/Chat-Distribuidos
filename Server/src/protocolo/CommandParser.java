package chat.protocolo;


public class CommandParser {

    public static Command parse(String linea) {


        linea = linea.trim();

        if (linea.isEmpty()) {
            return new Command(CommandType.UNKNOWN);
        }

        if (linea.startsWith("LOGIN|")) {

            String nombre = linea.substring(6).trim();

            if (nombre.isEmpty()) {
                return new Command(CommandType.UNKNOWN);
            }

            return new Command(
                    CommandType.LOGIN,
                    nombre
            );
        }

        if (linea.startsWith("GROUP|")) {

            String mensaje = linea.substring(6);

            return new Command(
                    CommandType.GROUP,
                    mensaje
            );
        }


        if (linea.startsWith("PRIVATE|")) {

            String[] partes = linea.split("\\|", 3);

            if (partes.length < 3) {
                return new Command(CommandType.UNKNOWN);
            }

            String destino = partes[1].trim();
            String mensaje = partes[2];

            if (destino.isEmpty() || mensaje.isEmpty()) {
                return new Command(CommandType.UNKNOWN);
            }

            return new Command(
                    CommandType.PRIVATE,
                    destino,
                    mensaje
            );
        }

        if (linea.equals("LIST")) {
            return new Command(CommandType.LIST);
        }

        if (linea.equals("EXIT")) {
            return new Command(CommandType.EXIT);
        }

        return new Command(CommandType.UNKNOWN);
    }
}