import os
import smtplib
from email.mime.text import MIMEText

remitente = "garysmithc010@gmail.com"
password = os.getenv("GMAIL_APP_PASSWORD")
destinatario = "garysmithc010@gmail.com"

mensaje = MIMEText("Hola Gary, tu bot de trading ya puede mandarte correos!")
mensaje["Subject"] = "Prueba de tu bot de trading"
mensaje["From"] = remitente
mensaje["To"] = destinatario

with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
    servidor.starttls()
    servidor.login(remitente, password)
    servidor.send_message(mensaje)

print("Correo enviado!")