import yfinance as yf

acciones = ["AAPL", "MSFT", "NVDA", "TSLA"]

for ticker in acciones:
    empresa = yf.Ticker(ticker)
    datos = empresa.history(period="60d")
    precios_cierre = datos["Close"]
    
    precio_hoy = precios_cierre.iloc[-1]
    media_movil_50 = precios_cierre.rolling(50).mean().iloc[-1]
    
    print(f"{ticker}: Precio ${precio_hoy:.2f} | Media móvil ${media_movil_50:.2f}")