import os
from twilio.rest import Client

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(account_sid, auth_token)

mensaje = client.messages.create(
    body="Hola Gary, tu bot de trading ya puede mandarte SMS!",
    from_="+14329997021",
    to="+525580347707"
)

print(f"Mensaje enviado, SID: {mensaje.sid}")