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

exitos = [r for r in resultados_totales if r > 0]
fracasos = [r for r in resultados_totales if r <= 0]

print(f"\nTotal: {len(resultados_totales)} | Ganadoras: {len(exitos)} | Perdedoras: {len(fracasos)}")

ganancia_promedio = sum(exitos) / len(exitos)
perdida_promedio = sum(fracasos) / len(fracasos)

print(f"Ganancia promedio CUANDO GANA: {ganancia_promedio:.2f}%")
print(f"Pérdida promedio CUANDO PIERDE: {perdida_promedio:.2f}%")

ratio = abs(ganancia_promedio / perdida_promedio)
print(f"Ratio Riesgo/Recompensa: {ratio:.2f}")