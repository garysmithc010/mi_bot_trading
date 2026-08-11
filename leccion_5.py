import yfinance as yf

acciones = ["AAPL", "MSFT", "NVDA", "TSLA"]

for ticker in acciones:
    empresa = yf.Ticker(ticker)
    datos = empresa.history(period="10d")
    precios_cierre = datos["Close"]
    
    precio_hoy = precios_cierre.iloc[-1]
    precio_hace_7_dias = precios_cierre.iloc[-7]
    
    cambio = ((precio_hoy - precio_hace_7_dias) / precio_hace_7_dias) * 100
    
    print(f"{ticker}: ${precio_hoy:.2f} | Cambio: {cambio:.2f}%")