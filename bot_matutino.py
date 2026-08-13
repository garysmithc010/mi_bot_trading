import re
import os
import json
import smtplib
import yfinance as yf
import anthropic
from datetime import date
from email.mime.text import MIMEText

# ---------- EDITA ESTO CADA MAÑANA ----------
WATCHLIST_HOY = ["UAL", "TRMB"]

REMITENTE = "garysmithc010@gmail.com"
DESTINATARIO = "garysmithc010@gmail.com"
MODELO = "claude-sonnet-5"

client_claude = anthropic.Anthropic()
password_gmail = os.getenv("GMAIL_APP_PASSWORD")

try:
    with open("ultimo_analisis.json", "r", encoding="utf-8") as f:
        contexto = json.load(f)
except Exception:
    contexto = {}

def confianza_de(texto):
    m = re.search(r"CONFIANZA:\s*(\d+)", texto)
    return int(m.group(1)) if m else -1

resultados = []

for ticker in WATCHLIST_HOY:
    print(f"Revisando {ticker}...")
    info_ayer = contexto.get(ticker)
    if not info_ayer:
        resultados.append({"ticker": ticker, "confianza": -1, "texto": f"{ticker}: no hay analisis de anoche guardado.\n"})
        continue

    try:
        precio_ahora = yf.Ticker(ticker).fast_info["last_price"]
    except Exception:
        try:
            precio_ahora = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]
        except Exception:
            resultados.append({"ticker": ticker, "confianza": -1, "texto": f"{ticker}: no se pudo obtener precio actual.\n"})
            continue

    try:
        with client_claude.messages.stream(
            model=MODELO,
            max_tokens=1000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{
                "role": "user",
                "content": f"""
Busca si hay noticias nuevas de {ticker} desde ayer (overnight/premarket) antes de responder.

Analisis de anoche:
{info_ayer['analisis_completo']}

Precio de anoche: ${info_ayer['precio']:.2f} | Stop: ${info_ayer['sl']:.2f} | Target: ${info_ayer['tp']:.2f}
Precio AHORA MISMO: ${precio_ahora:.2f}

Responde en texto plano, sin Markdown, muy conciso:

ANOCHE: (resume en una linea el veredicto de anoche y su razon principal)
DECISION: COMPRAR AHORA / ESPERAR / DESCARTAR
CONFIANZA: (numero del 0 al 100, solo el numero)
PRECIO_SUGERIDO: (si dice esperar, a que precio entrarias hoy)
RAZON: (que cambio o no desde anoche, maximo 2 lineas)
"""
            }]
        ) as stream:
            msg = stream.get_final_message()
        analisis_hoy = "".join(b.text for b in msg.content if b.type == "text")
    except Exception as e:
        analisis_hoy = f"CONFIANZA: -1\n(Error: {e})"

    confianza = confianza_de(analisis_hoy)
    texto = f"{ticker} | ahora ${precio_ahora:.2f} (ayer ${info_ayer['precio']:.2f})\n"
    texto += analisis_hoy + "\n"
    resultados.append({"ticker": ticker, "confianza": confianza, "texto": texto})

resultados.sort(key=lambda x: x["confianza"], reverse=True)

reporte = f"CHEQUEO MATUTINO - {date.today()}\n" + "=" * 50 + "\n\n"
for r in resultados:
    reporte += r["texto"] + "-" * 50 + "\n\n"

correo = MIMEText(reporte)
correo["Subject"] = f"Chequeo matutino - {date.today()}"
correo["From"] = REMITENTE
correo["To"] = DESTINATARIO

with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
    servidor.starttls()
    servidor.login(REMITENTE, password_gmail)
    servidor.send_message(correo)

print("Listo.")