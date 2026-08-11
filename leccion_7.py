import yfinance as yf

acciones = ["AAPL", "MSFT", "NVDA", "TSLA"]

for ticker in acciones:
    empresa = yf.Ticker(ticker)
    datos = empresa.history(period="60d")
    precios_cierre = datos["Close"]
    
    precio_hoy = precios_cierre.iloc[-1]
    precio_hace_7_dias = precios_cierre.iloc[-7]
    media_movil_50 = precios_cierre.rolling(50).mean().iloc[-1]
    
    cambio = ((precio_hoy - precio_hace_7_dias) / precio_hace_7_dias) * 100
    
    print(f"\n{ticker}: Precio ${precio_hoy:.2f} | Cambio {cambio:.2f}% | Media ${media_movil_50:.2f}")
    
    if cambio < -5 and precio_hoy > media_movil_50:
        print(f"  ⚠️ {ticker} ES CANDIDATO")
    else:
        print(f"  {ticker} no cumple criterios")