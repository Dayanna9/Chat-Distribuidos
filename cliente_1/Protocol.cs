using System;

namespace ClienteChatCSharp
{
 
    public static class Protocol
    {


        public const string Login = "LOGIN";

        public const string Group = "GROUP";

        public const string Private = "PRIVATE";

        public const string List = "LIST";

        public const string Exit = "EXIT";


        public const string Welcome = "WELCOME";

        public const string Join = "JOIN";

        public const string Left = "LEFT";

        public const string Users = "USERS";

        public const string Error = "ERROR";

 
        public static string CrearLogin(string usuario)
        {
            return $"LOGIN|{usuario}";
        }

  
        public static string CrearMensajeGrupo(string mensaje)
        {
            return $"GROUP|{mensaje}";
        }


        public static string CrearMensajePrivado(
            string destinatario,
            string mensaje)
        {
            return $"PRIVATE|{destinatario}|{mensaje}";
        }

     
        public static string CrearSolicitudUsuarios()
        {
            return "LIST";
        }

        public static string CrearSalida()
        {
            return "EXIT";
        }
    }
}