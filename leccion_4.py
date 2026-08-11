import yfinance as yf

apple = yf.Ticker("AAPL")
datos = apple.history(period="10d")

precios_cierre = datos["Close"]

precio_hoy = precios_cierre.iloc[-1]
precio_hace_7_dias = precios_cierre.iloc[-7]

print(f"Precio hoy: ${precio_hoy:.2f}")
print(f"Precio hace 7 días: ${precio_hace_7_dias:.2f}")

cambio = ((precio_hoy - precio_hace_7_dias) / precio_hace_7_dias) * 100

print(f"Cambio: {cambio:.2f}%")