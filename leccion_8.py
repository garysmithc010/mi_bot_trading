import yfinance as yf

ticker = "AAPL"
empresa = yf.Ticker(ticker)
datos = empresa.history(period="2y")
precios = datos["Close"]

media_movil = precios.rolling(50).mean()

resultados = []

for i in range(50, len(precios) - 15):
    precio_actual = precios.iloc[i]
    precio_hace_7_dias = precios.iloc[i - 7]
    media_ese_dia = media_movil.iloc[i]
    
    cambio = ((precio_actual - precio_hace_7_dias) / precio_hace_7_dias) * 100
    
    if cambio < -5 and precio_actual > media_ese_dia:
        precio_futuro = precios.iloc[i + 15]
        cambio_futuro = ((precio_futuro - precio_actual) / precio_actual) * 100
        resultados.append(cambio_futuro)

print(f"Total de veces que se cumplió el criterio: {len(resultados)}")

exitos = [r for r in resultados if r > 0]
print(f"Veces que SUBIÓ después: {len(exitos)}")

if len(resultados) > 0:
    porcentaje_exito = (len(exitos) / len(resultados)) * 100
    print(f"Porcentaje de éxito: {porcentaje_exito:.1f}%")