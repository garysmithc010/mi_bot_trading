import yfinance as yf

ticker = "AAPL"
empresa = yf.Ticker(ticker)
datos = empresa.history(period="60d")

datos['High-Low'] = datos['High'] - datos['Low']
datos['High-PrevClose'] = abs(datos['High'] - datos['Close'].shift(1))
datos['Low-PrevClose'] = abs(datos['Low'] - datos['Close'].shift(1))
datos['TR'] = datos[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)

atr = datos['TR'].rolling(14).mean().iloc[-1]
precio_actual = datos['Close'].iloc[-1]

stop_loss = precio_actual - (2 * atr)
take_profit = precio_actual + (3 * atr)

print(f"Precio actual: ${precio_actual:.2f}")
print(f"ATR (volatilidad promedio diaria): ${atr:.2f}")
print(f"Stop-loss sugerido (2x ATR): ${stop_loss:.2f}")
print(f"Take-profit sugerido (3x ATR): ${take_profit:.2f}")