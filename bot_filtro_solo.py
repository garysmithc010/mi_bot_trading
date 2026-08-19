import json
import yfinance as yf
import pandas as pd
import requests
from datetime import date
from io import StringIO

CAIDA_MINIMA = -5
ARCHIVO_HISTORIAL = "historial.json"
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

        volumen_ratio = df["Volume"].iloc[-1] / df["Volume"].rolling(20).mean().iloc[-1]

        minimo_3m = precios.tail(63).min()
        dist_minimo = ((precio_hoy - minimo_3m) / minimo_3m) * 100

        dias_earnings = "?"
        dias_dividendo = "?"
        market_cap = "?"
        sector = "?"
        pe_ratio = "?"
        dist_52w_high = "?"
        try:
            t = yf.Ticker(ticker)
            cal = t.calendar
            if cal:
                if "Earnings Date" in cal:
                    e = cal["Earnings Date"]
                    e = e[0] if isinstance(e, list) else e
                    dias_earnings = (e - HOY).days
                if "Ex-Dividend Date" in cal:
                    d = cal["Ex-Dividend Date"]
                    d = d[0] if isinstance(d, list) else d
                    dias_dividendo = (d - HOY).days

            info = t.info
            if info.get("marketCap"):
                market_cap = f"${info['marketCap']/1e9:.1f}B"
            if info.get("sector"):
                sector = info["sector"]
            if info.get("trailingPE"):
                pe_ratio = f"{info['trailingPE']:.1f}"
            if info.get("fiftyTwoWeekHigh"):
                dist_52w_high = ((precio_hoy - info["fiftyTwoWeekHigh"]) / info["fiftyTwoWeekHigh"]) * 100
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
            "atr": atr, "rsi": rsi, "dist_minimo": dist_minimo, "volumen_ratio": volumen_ratio,
            "sl": precio_hoy - (1 * atr), "tp": precio_hoy + (1.5 * atr),
            "earnings": dias_earnings, "dividendo": dias_dividendo,
            "dias": dias_como_candidato, "primera_vez": primera_vez,
            "market_cap": market_cap, "sector": sector, "pe": pe_ratio, "dist_52w": dist_52w_high,
        })

    except Exception:
        continue

with open(ARCHIVO_HISTORIAL, "w") as f:
    json.dump({c["ticker"]: c["primera_vez"] for c in candidatos}, f)

print(f"\n{len(candidatos)} CANDIDATOS — copia todo esto y pegalo en el chat con Claude:\n")
print("=" * 60)
for c in candidatos:
    dist_52w_txt = f"{c['dist_52w']:.1f}%" if isinstance(c['dist_52w'], (int, float)) else c['dist_52w']
    print(f"""
TICKER: {c['ticker']}
Precio: ${c['precio']:.2f} | Cambio 7d: {c['cambio']:.2f}% | Media 50d: ${c['media']:.2f}
RSI(14): {c['rsi']:.0f} | Volumen: {c['volumen_ratio']:.2f}x lo normal | {c['dist_minimo']:.1f}% sobre min 3m
ATR: ${c['atr']:.2f} | Stop sugerido: ${c['sl']:.2f} | Target sugerido: ${c['tp']:.2f}
Earnings en: {c['earnings']} | Ex-dividendo en: {c['dividendo']} | Dias como candidato: {c['dias']}
Market cap: {c['market_cap']} | Sector: {c['sector']} | P/E: {c['pe']} | Dist. a max 52sem: {dist_52w_txt}""")
print("=" * 60)