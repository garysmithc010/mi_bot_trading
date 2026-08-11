import yfinance as yf
from datetime import date

empresa = yf.Ticker("AAPL")
calendario = empresa.calendar

fecha_earnings = calendario["Earnings Date"][0]
hoy = date.today()
dias_hasta_earnings = (fecha_earnings - hoy).days

print(f"Próximo earnings: {fecha_earnings}")
print(f"Días hasta earnings: {dias_hasta_earnings}")