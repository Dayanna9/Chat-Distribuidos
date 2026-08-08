using System;
using System.Drawing;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace ClienteChatCSharp
{
    public class LoginForm : Form
    {
        private TextBox txtServidor;
        private TextBox txtPuerto;
        private TextBox txtUsuario;
        private Button btnConectar;
        private Label lblEstado;

        public LoginForm()
        {
            InicializarInterfaz();
        }

        private void InicializarInterfaz()
        {
            Text = "Chat - Conexión";

            Size = new Size(400, 330);

            StartPosition =
                FormStartPosition.CenterScreen;

            FormBorderStyle =
                FormBorderStyle.FixedSingle;

            MaximizeBox = false;

            Label titulo =
                new Label();

            titulo.Text = "CHAT";

            titulo.Font =
                new Font(
                    "Segoe UI",
                    18,
                    FontStyle.Bold
                );

            titulo.AutoSize = true;

            titulo.Location =
                new Point(155, 25);

            Controls.Add(titulo);

            Label lblServidor =
                new Label();

            lblServidor.Text = "Servidor:";

            lblServidor.Location =
                new Point(40, 85);

            lblServidor.AutoSize = true;

            Controls.Add(lblServidor);

            txtServidor =
                new TextBox();

            txtServidor.Location =
                new Point(120, 82);

            txtServidor.Size =
                new Size(210, 25);

            txtServidor.Text =
                "127.0.0.1";

            Controls.Add(txtServidor);

            Label lblPuerto =
                new Label();

            lblPuerto.Text = "Puerto:";

            lblPuerto.Location =
                new Point(40, 125);

            lblPuerto.AutoSize = true;

            Controls.Add(lblPuerto);

            txtPuerto =
                new TextBox();

            txtPuerto.Location =
                new Point(120, 122);

            txtPuerto.Size =
                new Size(210, 25);

            txtPuerto.Text =
                "5000";

            Controls.Add(txtPuerto);

            Label lblUsuario =
                new Label();

            lblUsuario.Text = "Usuario:";

            lblUsuario.Location =
                new Point(40, 165);

            lblUsuario.AutoSize = true;

            Controls.Add(lblUsuario);

            txtUsuario =
                new TextBox();

            txtUsuario.Location =
                new Point(120, 162);

            txtUsuario.Size =
                new Size(210, 25);

            Controls.Add(txtUsuario);

            btnConectar =
                new Button();

            btnConectar.Text =
                "Conectar";

            btnConectar.Location =
                new Point(130, 210);

            btnConectar.Size =
                new Size(120, 35);

            btnConectar.Click +=
                BtnConectar_Click;

            Controls.Add(btnConectar);

            lblEstado =
                new Label();

            lblEstado.AutoSize = true;

            lblEstado.Location =
                new Point(40, 260);

            Controls.Add(lblEstado);
        }

        private async void BtnConectar_Click(
            object sender,
            EventArgs e)
        {
            string servidor =
                txtServidor.Text.Trim();

            string puertoTexto =
                txtPuerto.Text.Trim();

            string usuario =
                txtUsuario.Text.Trim();

            if (string.IsNullOrWhiteSpace(usuario))
            {
                MessageBox.Show(
                    "Debes escribir un usuario."
                );

                return;
            }

            if (!int.TryParse(
                    puertoTexto,
                    out int puerto))
            {
                MessageBox.Show(
                    "El puerto no es válido."
                );

                return;
            }

            btnConectar.Enabled = false;

            lblEstado.Text =
                "Conectando...";

            try
            {
                ChatClient cliente =
                    new ChatClient(
                        servidor,
                        puerto
                    );

                await cliente.ConectarAsync();

             
                await cliente.EnviarAsync(
                    Protocol.CrearLogin(usuario)
                );

            
                MainForm ventanaPrincipal =
                    new MainForm(
                        cliente,
                        usuario
                    );

                ventanaPrincipal.FormClosed +=
                    (s, args) =>
                    {
                        Close();
                    };

                Hide();

                ventanaPrincipal.Show();
            }
            catch (Exception ex)
            {
                lblEstado.Text =
                    "Error de conexión.";

                btnConectar.Enabled = true;

                MessageBox.Show(
                    "No fue posible conectarse.\n\n"
                    + ex.Message,
                    "Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
            }
        }
    }
}