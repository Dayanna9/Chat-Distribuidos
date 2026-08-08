using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace ClienteChatCSharp
{

    public class ChatClient
    {
        private readonly string servidor;

        private readonly int puerto;

        private Socket socket;

        private CancellationTokenSource cancellationTokenSource;

        private readonly SemaphoreSlim sendLock =
            new SemaphoreSlim(1, 1);

     
        public event Action<string> MensajeRecibido;

    
        public event Action Desconectado;

        public bool EstaConectado
        {
            get
            {
                return socket != null &&
                       socket.Connected;
            }
        }

        public ChatClient(
            string servidor,
            int puerto)
        {
            this.servidor = servidor;
            this.puerto = puerto;
        }

    
        public async Task ConectarAsync()
        {
            socket = new Socket(
                AddressFamily.InterNetwork,
                SocketType.Stream,
                ProtocolType.Tcp
            );

        
            socket.Blocking = false;

            cancellationTokenSource =
                new CancellationTokenSource();

            IPAddress ip;

          
            if (!IPAddress.TryParse(
                    servidor,
                    out ip))
            {
                IPHostEntry host =
                    await Dns.GetHostEntryAsync(servidor);

                ip = host.AddressList[0];
            }

            IPEndPoint endpoint =
                new IPEndPoint(ip, puerto);

       
            await socket.ConnectAsync(endpoint);

          
            _ = RecibirMensajesAsync(
                cancellationTokenSource.Token
            );
        }

        public async Task EnviarAsync(
            string mensaje)
        {
            if (!EstaConectado)
            {
                return;
            }

    
            string mensajeCompleto =
                mensaje + "\n";

            byte[] datos =
                Encoding.UTF8.GetBytes(
                    mensajeCompleto
                );

            await sendLock.WaitAsync();

            try
            {
                int enviados = 0;

                while (enviados < datos.Length)
                {
                    int cantidad =
                        await socket.SendAsync(
                            datos.AsMemory(enviados),
                            SocketFlags.None
                        );

                    if (cantidad == 0)
                    {
                        throw new SocketException();
                    }

                    enviados += cantidad;
                }
            }
            finally
            {
                sendLock.Release();
            }
        }

    
        private async Task RecibirMensajesAsync(
            CancellationToken cancellationToken)
        {
            byte[] buffer =
                new byte[4096];

            StringBuilder acumulador =
                new StringBuilder();

            try
            {
                while (!cancellationToken.IsCancellationRequested)
                {
                    int cantidad =
                        await socket.ReceiveAsync(
                            buffer,
                            SocketFlags.None,
                            cancellationToken
                        );

    
                    if (cantidad == 0)
                    {
                        break;
                    }

                    string texto =
                        Encoding.UTF8.GetString(
                            buffer,
                            0,
                            cantidad
                        );

                    acumulador.Append(texto);

               
                    ProcesarMensajesCompletos(
                        acumulador
                    );
                }
            }
            catch (OperationCanceledException)
            {
                // Desconexión normal.
            }
            catch (SocketException)
            {
                // socjet cerrado.
            }
            catch (ObjectDisposedException)
            {
                //socket liberado.
            }
            finally
            {
                Desconectado?.Invoke();
            }
        }

        private void ProcesarMensajesCompletos(
            StringBuilder acumulador)
        {
            while (true)
            {
                int posicion =
                    acumulador.ToString().IndexOf('\n');

                if (posicion < 0)
                {
                    break;
                }

                string mensaje =
                    acumulador
                        .ToString(
                            0,
                            posicion
                        )
                        .TrimEnd('\r');

                
                acumulador.Remove(
                    0,
                    posicion + 1
                );

                if (!string.IsNullOrWhiteSpace(mensaje))
                {
                    MensajeRecibido?.Invoke(
                        mensaje
                    );
                }
            }
        }

      
        public async Task DesconectarAsync()
        {
            try
            {
                if (EstaConectado)
                {
                    await EnviarAsync(
                        Protocol.CrearSalida()
                    );
                }
            }
            catch
            {
                // conexión perdida.
            }

            try
            {
                cancellationTokenSource?.Cancel();

                socket?.Shutdown(
                    SocketShutdown.Both
                );

                socket?.Close();
            }
            catch
            {
                
            }
        }
    }
}