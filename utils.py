import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

load_dotenv()


def enviar_email(resumo, caminho_anexo=None):

    email_user = os.getenv("EMAIL")
    email_password = os.getenv("SENHA_E")

    msg = MIMEMultipart()
    msg['Subject'] = 'Robô RH - Execução Finalizada'
    msg['From'] = email_user
    msg['To'] = 'caio.ssilva0@hapvida.com.br'

    # corpo do email
    msg.attach(MIMEText(resumo, 'plain'))

    # 📎 anexo (se existir)
    if caminho_anexo and os.path.exists(caminho_anexo):
        with open(caminho_anexo, "rb") as f:
            anexo = MIMEApplication(f.read(), Name=os.path.basename(caminho_anexo))
        
        anexo['Content-Disposition'] = f'attachment; filename="{os.path.basename(caminho_anexo)}"'
        msg.attach(anexo)

    # envio
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(email_user, email_password)
        server.send_message(msg)
