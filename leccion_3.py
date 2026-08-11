import yfinance as yf

apple = yf.Ticker("AAPL")
datos = apple.history(period="5d")

print(datos)