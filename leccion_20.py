import yfinance as yf

empresa = yf.Ticker("AAPL")
calendario = empresa.calendar
print(calendario)