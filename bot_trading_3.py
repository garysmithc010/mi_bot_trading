import re
import sys
import json
import os
import smtplib
import yfinance as yf
import pandas as pd
import requests
import anthropic
from datetime import date
from io import StringIO
from email.mime.text import MIMEText

# ---------- CONFIGURACION ----------
REMITENTE = "garysmithc010@gmail.com"
DESTINATARIO = "garysmithc010@gmail.com"
CAIDA_MINIMA = -5
MODELO = "claude-sonnet-5"
ARCHIVO_HISTORIAL = "historial.json"

client_claude = anthropic.Anthropic()
password_gmail = os.getenv("GMAIL_APP_PASSWORD")
HOY = date.today()

try:
    with open(ARCHIVO_HISTORIAL, "r") as f:
        historial = json.load(f)
except Exception:
    historial = {}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
respuesta = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", headers=headers)
tickers = pd.read_html(StringIO(respuesta.text))[0]['Symbol'].tolist()
tickers = [t.replace(".", "-") for t in tickers]

print(f"Descargando {len(tickers)} acciones (1 año de historia)...")
datos = yf.download(tickers, period="1y", group_by="ticker", auto_adjust=True, progress=False)
print("Aplicando filtro...\n")

candidatos = []

for ticker in tickers:
    try:
        df = datos[ticker].dropna().copy()
        if len(df) < 130:
            continue

        precios = df["Close"]
        precio_hoy = precios.iloc[-1]
        media_50 = precios.rolling(50).mean().iloc[-1]
        cambio = ((precio_hoy - precios.iloc[-7]) / precios.iloc[-7]) * 100

        if cambio >= CAIDA_MINIMA or precio_hoy <= media_50:
            continue

        df['HL'] = df['High'] - df['Low']
        df['HC'] = abs(df['High'] - df['Close'].shift(1))
        df['LC'] = abs(df['Low'] - df['Close'].shift(1))
        atr = df[['HL', 'HC', 'LC']].max(axis=1).rolling(14).mean().iloc[-1]

        delta = precios.diff()
        ganancia = delta.where(delta > 0, 0)
        perdida = -delta.where(delta < 0, 0)
        avg_ganancia = ganancia.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        avg_perdida = perdida.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        rsi = (100 - (100 / (1 + avg_ganancia / avg_perdida))).iloc[-1]

        minimo_3m = precios.tail(63).min()
        dist_minimo = ((precio_hoy - minimo_3m) / minimo_3m) * 100

        dias_earnings = "?"
        dias_dividendo = "?"
        try:
            cal = yf.Ticker(ticker).calendar
            if cal:
                if "Earnings Date" in cal:
                    e = cal["Earnings Date"]
                    e = e[0] if isinstance(e, list) else e
                    dias_earnings = (e - HOY).days
                if "Ex-Dividend Date" in cal:
                    d = cal["Ex-Dividend Date"]
                    d = d[0] if isinstance(d, list) else d
                    dias_dividendo = (d - HOY).days
        except Exception:
            pass

        if isinstance(dias_earnings, int) and dias_earnings < 0:
            dias_earnings = "ya paso"
        if isinstance(dias_dividendo, int) and dias_dividendo < 0:
            dias_dividendo = "ya paso"

        primera_vez = historial.get(ticker, HOY.isoformat())
        dias_como_candidato = (HOY - date.fromisoformat(primera_vez)).days + 1

        candidatos.append({
            "ticker": ticker, "precio": precio_hoy, "cambio": cambio, "media": media_50,
            "atr": atr, "rsi": rsi, "dist_minimo": dist_minimo,
            "sl": precio_hoy - (2 * atr), "tp": precio_hoy + (3 * atr),
            "earnings": dias_earnings, "dividendo": dias_dividendo,
            "dias": dias_como_candidato, "primera_vez": primera_vez,
        })
        print(f"CANDIDATO: {ticker} | ${precio_hoy:.2f} | RSI {rsi:.0f} | dia {dias_como_candidato}")

    except Exception:
        continue

print(f"\nCandidatos: {len(candidatos)}\n")

with open(ARCHIVO_HISTORIAL, "w") as f:
    json.dump({c["ticker"]: c["primera_vez"] for c in candidatos}, f)

if not candidatos:
    print("Sin candidatos hoy. No se envia correo.")
    sys.exit()

def confianza_de(texto):
    m = re.search(r"CONFIANZA:\s*(\d+)", texto)
    return int(m.group(1)) if m else -1

for c in candidatos:
    print(f"Analizando {c['ticker']}...")
    try:
        with client_claude.messages.stream(
            model=MODELO,
            max_tokens=1500,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{
                "role": "user",
                "content": f"""
Busca noticias recientes de {c['ticker']} (ultima semana) antes de responder.

Datos:
Precio ${c['precio']:.2f} | Cambio 7d {c['cambio']:.2f}% | Media 50d ${c['media']:.2f}
RSI (14): {c['rsi']:.0f} | Distancia a minimo de 3 meses: {c['dist_minimo']:.1f}%
ATR ${c['atr']:.2f} | Stop ${c['sl']:.2f} | Target ${c['tp']:.2f}
Earnings en {c['earnings']} dias | Ex-dividendo en {c['dividendo']} dias
Lleva {c['dias']} dias como candidato

Responde en texto plano, sin Markdown, MUY conciso. Formato exacto:

EMPRESA: (que hace, una linea de 10 palabras maximo)
VEREDICTO: COMPRAR / ESPERAR / DESCARTAR
CONFIANZA: (numero del 0 al 100, solo el numero)
URGENCIA: HOY / ESTA SEMANA / SIN PRISA
CAUSA: (por que cayo segun noticias, y si es temporal o estructural, 2 lineas max)
CONFIRMACION_TECNICA: (el RSI indica sobreventa real o todavia no? esta cerca de un soporte solido -poco espacio a la baja- o todavia hay espacio para seguir cayendo? 2 lineas max)
TESIS: (en una frase: especificamente por que esperarias que rebote pronto, o por que no, conectando la razon de la caida con la situacion tecnica)
RIESGO: (earnings o dividendo cercano si aplica, 1 linea)
NIVELES: (si el stop y target tienen sentido o los ajustarias, 1 linea)
"""
            }]
        ) as stream:
            msg = stream.get_final_message()
        c["analisis"] = "".join(b.text for b in msg.content if b.type == "text")
    except Exception as e:
        c["analisis"] = f"CONFIANZA: -1\n(Error: {e})"

    c["confianza"] = confianza_de(c["analisis"])

contexto_completo = {
    c["ticker"]: {
        "fecha": HOY.isoformat(),
        "precio": c["precio"],
        "sl": c["sl"],
        "tp": c["tp"],
        "atr": c["atr"],
        "confianza": c["confianza"],
        "analisis_completo": c["analisis"],
    }
    for c in candidatos
}
with open("ultimo_analisis.json", "w", encoding="utf-8") as f:
    json.dump(contexto_completo, f, ensure_ascii=False)

candidatos.sort(key=lambda x: x["confianza"], reverse=True)

reporte = f"BOT TRADING - {HOY}\n{len(candidatos)} candidatos, ordenados por confianza\n"
reporte += "=" * 55 + "\n\n"

for i, c in enumerate(candidatos, 1):
    reporte += f"#{i}  {c['ticker']}  |  confianza {c['confianza']}\n"
    reporte += f"${c['precio']:.2f} | {c['cambio']:.2f}% en 7d | RSI {c['rsi']:.0f} | dia {c['dias']} como candidato\n"
    reporte += f"Stop ${c['sl']:.2f} | Target ${c['tp']:.2f} | ATR ${c['atr']:.2f} | {c['dist_minimo']:.1f}% sobre min 3m\n"
    reporte += f"Earnings en {c['earnings']} | Ex-dividendo en {c['dividendo']}\n\n"
    reporte += c["analisis"] + "\n"
    reporte += "-" * 55 + "\n\n"

correo = MIMEText(reporte)
correo["Subject"] = f"Bot Trading: {len(candidatos)} candidatos - {HOY}"
correo["From"] = REMITENTE
correo["To"] = DESTINATARIO

with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
    servidor.starttls()
    servidor.login(REMITENTE, password_gmail)
    servidor.send_message(correo)

print(f"\nListo. Correo enviado con {len(candidatos)} candidatos.")