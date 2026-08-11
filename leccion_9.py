import yfinance as yf

acciones = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META"]

resultados_totales = []

for ticker in acciones:
    empresa = yf.Ticker(ticker)
    datos = empresa.history(period="2y")
    precios = datos["Close"]
    
    media_movil = precios.rolling(50).mean()
    
    for i in range(50, len(precios) - 15):
        precio_actual = precios.iloc[i]
        precio_hace_7_dias = precios.iloc[i - 7]
        media_ese_dia = media_movil.iloc[i]
        
        cambio = ((precio_actual - precio_hace_7_dias) / precio_hace_7_dias) * 100
        
        if cambio < -5 and precio_actual > media_ese_dia:
            precio_futuro = precios.iloc[i + 15]
            cambio_futuro = ((precio_futuro - precio_actual) / precio_actual) * 100
            resultados_totales.append(cambio_futuro)
    
    print(f"{ticker} procesado...")

print(f"\nTotal de veces que se cumplió el criterio: {len(resultados_totales)}")

exitos = [r for r in resultados_totales if r > 0]
print(f"Veces que SUBIÓ después: {len(exitos)}")

if len(resultados_totales) > 0:
    porcentaje_exito = (len(exitos) / len(resultados_totales)) * 100
    print(f"Porcentaje de éxito: {porcentaje_exito:.1f}%")
    
    ganancia_promedio = sum(resultados_totales) / len(resultados_totales)
    print(f"Ganancia/pérdida promedio por trade: {ganancia_promedio:.2f}%")