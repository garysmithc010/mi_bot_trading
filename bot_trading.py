import sys
import yfinance as yf
import pandas as pd
import requests
import anthropic
import os
import smtplib
from datetime import date
from io import StringIO
from email.mime.text import MIMEText

# ---------- CONFIGURACION ----------
REMITENTE = "garysmithc010@gmail.com"
DESTINATARIO = "garysmithc010@gmail.com"
CAIDA_MINIMA = -5
MODELO = "claude-sonnet-5"

client_claude = anthropic.Anthropic()
password_gmail = os.getenv("GMAIL_APP_PASSWORD")

# ---------- 1. LISTA DEL S&P 500 ----------
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
respuesta = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", headers=headers)
tabla = pd.read_html(StringIO(respuesta.text))
tickers = tabla[0]['Symbol'].tolist()
tickers = [t.replace(".", "-") for t in tickers]

print(f"Descargando datos de {len(tickers)} acciones...")
datos = yf.download(tickers, period="60d", group_by="ticker", auto_adjust=True, progress=False)
print("Descarga lista. Aplicando filtro...\n")

# ---------- 2. FILTRO ----------
candidatos = []

for ticker in tickers:
    try:
        df = datos[ticker].dropna().copy()
        if len(df) < 50:
            continue

        precios = df["Close"]
        precio_hoy = precios.iloc[-1]
        precio_hace_7_dias = precios.iloc[-7]
        media_movil_50 = precios.rolling(50).mean().iloc[-1]
        cambio = ((precio_hoy - precio_hace_7_dias) / precio_hace_7_dias) * 100

        if cambio < CAIDA_MINIMA and precio_hoy > media_movil_50:
            df['High-Low'] = df['High'] - df['Low']
            df['High-PrevClose'] = abs(df['High'] - df['Close'].shift(1))
            df['Low-PrevClose'] = abs(df['Low'] - df['Close'].shift(1))
            df['TR'] = df[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)
            atr = df['TR'].rolling(14).mean().iloc[-1]

            dias_earnings = "desconocido"
            try:
                calendario = yf.Ticker(ticker).calendar
                if calendario and "Earnings Date" in calendario:
                    dias_earnings = (calendario["Earnings Date"][0] - date.today()).days
            except Exception:
                pass

            candidatos.append({
                "ticker": ticker,
                "precio": precio_hoy,
                "cambio": cambio,
                "media": media_movil_50,
                "atr": atr,
                "stop_loss": precio_hoy - (2 * atr),
                "take_profit": precio_hoy + (3 * atr),
                "earnings": dias_earnings,
            })
            print(f"CANDIDATO: {ticker} | ${precio_hoy:.2f} | {cambio:.2f}% | earnings en {dias_earnings} dias")

    except Exception:
        continue

print(f"\nCandidatos encontrados: {len(candidatos)}\n")

if len(candidatos) == 0:
    print("Sin candidatos hoy. No se envia correo.")
    sys.exit()

# ---------- 3. ANALISIS CON CLAUDE ----------
reporte = f"BOT TRADING - {date.today()}\nCandidatos encontrados: {len(candidatos)}\n"
reporte += "=" * 60 + "\n\n"

for c in candidatos:
    print(f"Analizando {c['ticker']} con Claude...")
    try:
        mensaje = client_claude.messages.create(
            model=MODELO,
            max_tokens=20000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{
                "role": "user",
                "content": f"""
Busca noticias recientes sobre {c['ticker']} (ultima semana) antes de responder.

Analiza este setup de trading. Responde en texto plano sencillo, sin Markdown
(no uses #, **, tablas ni emojis):

Accion: {c['ticker']}
Precio actual: ${c['precio']:.2f}
Cambio en 7 dias: {c['cambio']:.2f}%
Media movil 50 dias: ${c['media']:.2f}
Dias hasta el proximo earnings: {c['earnings']}
ATR (volatilidad promedio diaria): ${c['atr']:.2f}
Stop-loss sugerido (2x ATR): ${c['stop_loss']:.2f}
Take-profit sugerido (3x ATR): ${c['take_profit']:.2f}

Responde con esta estructura:
1. VEREDICTO: COMPRAR / ESPERAR / DESCARTAR
2. POR QUE CAYO: la razon segun noticias reales, y si es temporal o estructural
3. RIESGO DE EARNINGS: si cae dentro de 2-3 semanas, si conviene esperar
4. NIVELES: si el stop-loss y take-profit tienen sentido o los ajustarias
5. RESUMEN: 2 lineas maximo
"""
            }]
        )

        analisis = ""
        for bloque in mensaje.content:
            if bloque.type == "text":
                analisis += bloque.text

    except Exception as e:
        analisis = f"(No se pudo analizar: {e})"

    reporte += f"{c['ticker']} | ${c['precio']:.2f} | {c['cambio']:.2f}% en 7 dias\n"
    reporte += f"Media 50d: ${c['media']:.2f} | ATR: ${c['atr']:.2f} | Earnings en {c['earnings']} dias\n"
    reporte += f"Stop-loss: ${c['stop_loss']:.2f} | Take-profit: ${c['take_profit']:.2f}\n\n"
    reporte += analisis + "\n"
    reporte += "-" * 60 + "\n\n"

# ---------- 4. CORREO ----------
correo = MIMEText(reporte)
correo["Subject"] = f"Bot Trading: {len(candidatos)} candidatos - {date.today()}"
correo["From"] = REMITENTE
correo["To"] = DESTINATARIO

with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
    servidor.starttls()
    servidor.login(REMITENTE, password_gmail)
    servidor.send_message(correo)

print(f"\nListo. Correo enviado con {len(candidatos)} candidatos.")