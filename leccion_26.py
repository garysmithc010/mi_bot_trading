import yfinance as yf
import pandas as pd
import requests
from io import StringIO

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
respuesta = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", headers=headers)
tabla = pd.read_html(StringIO(respuesta.text))
tickers = tabla[0]['Symbol'].tolist()
tickers = [t.replace(".", "-") for t in tickers]

print(f"Descargando datos de {len(tickers)} acciones...")
print("Esto tarda 1-2 minutos. La pantalla se va a ver quieta, es normal.")

datos = yf.download(tickers, period="60d", group_by="ticker", auto_adjust=True, progress=False)

print("Descarga lista. Aplicando filtro...\n")

candidatos = []
errores = 0

for ticker in tickers:
    try:
        df = datos[ticker].dropna()
        
        if len(df) < 50:
            continue
        
        precios = df["Close"]
        precio_hoy = precios.iloc[-1]
        precio_hace_7_dias = precios.iloc[-7]
        media_movil_50 = precios.rolling(50).mean().iloc[-1]
        
        cambio = ((precio_hoy - precio_hace_7_dias) / precio_hace_7_dias) * 100
        
        if cambio < -5 and precio_hoy > media_movil_50:
            candidatos.append(ticker)
            print(f"CANDIDATO: {ticker} | ${precio_hoy:.2f} | Cambio {cambio:.2f}% | Media ${media_movil_50:.2f}")
    
    except Exception:
        errores += 1
        continue

print(f"\n--- RESUMEN ---")
print(f"Acciones revisadas: {len(tickers)}")
print(f"Acciones sin datos suficientes: {errores}")
print(f"CANDIDATOS ENCONTRADOS: {len(candidatos)}")
print(candidatos)