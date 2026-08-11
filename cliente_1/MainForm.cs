using System;
using System.Drawing;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace ClienteChatCSharp
{
    public class MainForm : Form
    {
        private readonly ChatClient cliente;

        private readonly string usuarioActual;

        private TextBox txtConversacion;

        private ListBox lstUsuarios;

        private TextBox txtMensaje;

        private Button btnEnviar;

        private Label lblUsuario;

        private Label lblDestino;

        // Se mantiene separado del ListBox para no perder el destinatario
        // cuando el servidor actualiza la lista de usuarios.
        private string? destinatarioSeleccionado;

        public MainForm(
            ChatClient cliente,
            string usuarioActual)
        {
            this.cliente = cliente;
            this.usuarioActual = usuarioActual;

            InicializarInterfaz();

            cliente.MensajeRecibido +=
                Cliente_MensajeRecibido;

            cliente.Desconectado +=
                Cliente_Desconectado;

            Shown += MainForm_Shown;
        }

        private async void MainForm_Shown(
            object sender,
            EventArgs e)
        {
            await cliente.EnviarAsync(
                Protocol.CrearSolicitudUsuarios()
            );
        }

        private void InicializarInterfaz()
        {
            Text =
                $"Chat - {usuarioActual}";

            Size =
                new Size(850, 600);

            MinimumSize =
                new Size(700, 500);

            StartPosition =
                FormStartPosition.CenterScreen;


            lblUsuario =
                new Label();

            lblUsuario.Text =
                usuarioActual;

            lblUsuario.Font =
                new Font(
                    "Segoe UI",
                    12,
                    FontStyle.Bold
                );

            lblUsuario.Dock =
                DockStyle.Top;

            lblUsuario.Height = 45;

            lblUsuario.TextAlign =
                ContentAlignment.MiddleLeft;

            lblUsuario.Padding =
                new Padding(15, 0, 0, 0);

            Controls.Add(lblUsuario);


            Panel panelUsuarios =
                new Panel();

            panelUsuarios.Dock =
                DockStyle.Right;

            panelUsuarios.Width = 180;

            panelUsuarios.Padding =
                new Padding(5);

            Controls.Add(panelUsuarios);

            Label lblUsuarios =
                new Label();

            lblUsuarios.Text =
                "Usuarios conectados";

            lblUsuarios.Dock =
                DockStyle.Top;

            lblUsuarios.Height = 35;

            lblUsuarios.TextAlign =
                ContentAlignment.MiddleCenter;

            lstUsuarios =
                new ListBox();

            lstUsuarios.Dock =
                DockStyle.Fill;

            lstUsuarios.SelectionMode =
                SelectionMode.One;

           
            lstUsuarios.SelectedIndexChanged +=
                LstUsuarios_SelectedIndexChanged;

            panelUsuarios.Controls.Add(
                lstUsuarios
            );

            // El control acoplado al borde superior debe agregarse al final
            // para que el ListBox ocupe solo el espacio restante.
            panelUsuarios.Controls.Add(
                lblUsuarios
            );

            

            Panel panelInferior =
                new Panel();

            panelInferior.Dock =
                DockStyle.Bottom;

            panelInferior.Height = 70;

            panelInferior.Padding =
                new Padding(10);

            Controls.Add(panelInferior);

            btnEnviar =
                new Button();

            btnEnviar.Text =
                "Send";

            btnEnviar.Dock =
                DockStyle.Right;

            btnEnviar.Width = 100;

            btnEnviar.Click +=
                BtnEnviar_Click;

            panelInferior.Controls.Add(
                btnEnviar
            );

            txtMensaje =
                new TextBox();

            txtMensaje.Multiline = false;

            txtMensaje.Dock =
                DockStyle.Fill;

            txtMensaje.Font =
                new Font(
                    "Segoe UI",
                    11
                );

            txtMensaje.KeyDown +=
                TxtMensaje_KeyDown;

            panelInferior.Controls.Add(
                txtMensaje
            );

    

            Panel panelChat =
                new Panel();

            panelChat.Dock =
                DockStyle.Fill;

            panelChat.Padding =
                new Padding(10);

            Controls.Add(panelChat);

            txtConversacion =
                new TextBox();

            txtConversacion.Multiline =
                true;

            txtConversacion.ReadOnly =
                true;

            txtConversacion.ScrollBars =
                ScrollBars.Vertical;

            txtConversacion.Dock =
                DockStyle.Fill;

            txtConversacion.Font =
                new Font(
                    "Segoe UI",
                    10
                );

            panelChat.Controls.Add(
                txtConversacion
            );

            lblDestino =
                new Label();

            lblDestino.Text =
                "Chat grupal";

            lblDestino.Dock =
                DockStyle.Bottom;

            lblDestino.Height = 25;

            lblDestino.TextAlign =
                ContentAlignment.MiddleLeft;

            panelChat.Controls.Add(
                lblDestino
            );

        }

        private void LstUsuarios_SelectedIndexChanged(
            object sender,
            EventArgs e)
        {
            if (lstUsuarios.SelectedItem == null)
            {
                destinatarioSeleccionado =
                    null;

                lblDestino.Text =
                    "Chat grupal";

                return;
            }

            string seleccionado =
                lstUsuarios.SelectedItem.ToString();

            if (seleccionado == usuarioActual)
            {
                destinatarioSeleccionado =
                    null;

                lstUsuarios.ClearSelected();

                lblDestino.Text =
                    "Chat grupal";

                return;
            }

            destinatarioSeleccionado =
                seleccionado;

            lblDestino.Text =
                $"Mensaje privado para: {seleccionado}";
        }

        private async void BtnEnviar_Click(
            object sender,
            EventArgs e)
        {
            await EnviarMensaje();
        }

        private async void TxtMensaje_KeyDown(
            object sender,
            KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter)
            {
                e.SuppressKeyPress = true;

                await EnviarMensaje();
            }
        }

        private async Task EnviarMensaje()
        {
            string mensaje =
                txtMensaje.Text.Trim();

            if (string.IsNullOrWhiteSpace(mensaje))
            {
                return;
            }

          
            string? destino =
                destinatarioSeleccionado;

            if (!string.IsNullOrWhiteSpace(destino))
            {
                await cliente.EnviarAsync(
                    Protocol.CrearMensajePrivado(
                        destino,
                        mensaje
                    )
                );
            }
            else
            {
 
                await cliente.EnviarAsync(
                    Protocol.CrearMensajeGrupo(
                        mensaje
                    )
                );
            }

            txtMensaje.Clear();

            txtMensaje.Focus();
        }

  
        private void Cliente_MensajeRecibido(
            string mensaje)
        {
   
            if (InvokeRequired)
            {
                Invoke(
                    new Action(
                        () => ProcesarMensaje(mensaje)
                    )
                );

                return;
            }

            ProcesarMensaje(mensaje);
        }

        private void ProcesarMensaje(
            string mensaje)
        {
            string[] partes =
                mensaje.Split(
                    '|',
                    3
                );

            if (partes.Length == 0)
            {
                return;
            }

            string tipo =
                partes[0];

            switch (tipo)
            {
                case Protocol.Welcome:

                    AgregarConversacion(
                        $"Conectado como {usuarioActual}"
                    );

                    break;

                case Protocol.Join:

                    if (partes.Length >= 2)
                    {
                        AgregarConversacion(
                            $"[Servidor] {partes[1]} se conectó."
                        );
                    }

                    break;

                case Protocol.Left:

                    if (partes.Length >= 2)
                    {
                        AgregarConversacion(
                            $"[Servidor] {partes[1]} se desconectó."
                        );
                    }

                    break;

                case Protocol.Users:

                    if (partes.Length >= 2)
                    {
                        ActualizarUsuarios(
                            partes[1]
                        );
                    }

                    break;

                case Protocol.Group:

                    if (partes.Length >= 3)
                    {
                        string remitente =
                            partes[1];

                        string texto =
                            partes[2];

                        AgregarConversacion(
                            $"{remitente}: {texto}"
                        );
                    }

                    break;

                case Protocol.Private:

                    if (partes.Length >= 3)
                    {
                        string remitente =
                            partes[1];

                        string texto =
                            partes[2];

                        AgregarConversacion(
                            $"[Privado] {remitente}: {texto}"
                        );
                    }

                    break;

                case Protocol.Error:

                    if (partes.Length >= 2)
                    {
                        AgregarConversacion(
                            $"[ERROR] {partes[1]}"
                        );
                    }

                    break;

                case "INFO":

                    if (partes.Length >= 2)
                    {
                        AgregarConversacion(
                            $"[Servidor] {partes[1]}"
                        );
                    }

                    break;
            }
        }

        private void ActualizarUsuarios(
            string lista)
        {
            string? destinatarioAnterior =
                destinatarioSeleccionado;

            bool conservarSeleccion =
                false;

            lstUsuarios.Items.Clear();

            if (string.IsNullOrWhiteSpace(lista))
            {
                destinatarioSeleccionado =
                    null;

                lblDestino.Text =
                    "Chat grupal";

                return;
            }

            string[] usuarios =
                lista.Split(
                    ',',
                    StringSplitOptions.RemoveEmptyEntries
                );

            foreach (string usuario in usuarios)
            {
                string usuarioLimpio =
                    usuario.Trim();

                if (string.IsNullOrWhiteSpace(usuarioLimpio))
                {
                    continue;
                }

                lstUsuarios.Items.Add(
                    usuarioLimpio
                );

                if (usuarioLimpio == destinatarioAnterior)
                {
                    conservarSeleccion =
                        true;
                }
            }

            if (conservarSeleccion &&
                destinatarioAnterior != null)
            {
                destinatarioSeleccionado =
                    destinatarioAnterior;

                lstUsuarios.SelectedItem =
                    destinatarioAnterior;

                lblDestino.Text =
                    $"Mensaje privado para: {destinatarioAnterior}";
            }
            else
            {
                destinatarioSeleccionado =
                    null;

                lblDestino.Text =
                    "Chat grupal";
            }
        }

        private void AgregarConversacion(
            string texto)
        {
            if (txtConversacion.TextLength > 0)
            {
                txtConversacion.AppendText(
                    Environment.NewLine
                );
            }

            txtConversacion.AppendText(
                texto
            );

            txtConversacion.SelectionStart =
                txtConversacion.TextLength;

            txtConversacion.ScrollToCaret();
        }

        private void Cliente_Desconectado()
        {
            if (InvokeRequired)
            {
                Invoke(
                    new Action(
                        () =>
                        {
                            AgregarConversacion(
                                "[Servidor] Conexión perdida."
                            );

                            btnEnviar.Enabled =
                                false;
                        }
                    )
                );

                return;
            }

            AgregarConversacion(
                "[Servidor] Conexión perdida."
            );

            btnEnviar.Enabled = false;
        }

        protected override async void OnFormClosing(
            FormClosingEventArgs e)
        {
            await cliente.DesconectarAsync();

            base.OnFormClosing(e);
        }
    }
}
