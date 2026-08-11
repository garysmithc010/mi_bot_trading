import yfinance as yf

acciones = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", 
            "JPM", "V", "JNJ", "WMT", "PG", "XOM", "DIS", "NFLX", "ADBE"]

resultados_totales = []

for ticker in acciones:
    empresa = yf.Ticker(ticker)
    datos = empresa.history(period="5y")
    precios = datos["Close"]
    volumen = datos["Volume"]
    
    media_movil = precios.rolling(50).mean()
    volumen_promedio = volumen.rolling(20).mean()
    
    for i in range(50, len(precios) - 15):
        precio_actual = precios.iloc[i]
        precio_hace_7_dias = precios.iloc[i - 7]
        media_ese_dia = media_movil.iloc[i]
        volumen_ese_dia = volumen.iloc[i]
        volumen_promedio_ese_dia = volumen_promedio.iloc[i]
        
        cambio = ((precio_actual - precio_hace_7_dias) / precio_hace_7_dias) * 100
        volumen_ratio = volumen_ese_dia / volumen_promedio_ese_dia
        
        if cambio < -5 and precio_actual > media_ese_dia and volumen_ratio > 1.5:
            precio_futuro = precios.iloc[i + 15]
            cambio_futuro = ((precio_futuro - precio_actual) / precio_actual) * 100
            resultados_totales.append(cambio_futuro)
    
    print(f"{ticker} procesado...")

exitos = [r for r in resultados_totales if r > 0]
fracasos = [r for r in resultados_totales if r <= 0]

print(f"\nTotal: {len(resultados_totales)} | Ganadoras: {len(exitos)} | Perdedoras: {len(fracasos)}")

if len(exitos) > 0 and len(fracasos) > 0:
    ganancia_promedio = sum(exitos) / len(exitos)
    perdida_promedio = sum(fracasos) / len(fracasos)
    ratio = abs(ganancia_promedio / perdida_promedio)
    win_rate = len(exitos) / len(resultados_totales) * 100
    
    print(f"Ganancia promedio CUANDO GANA: {ganancia_promedio:.2f}%")
    print(f"Pérdida promedio CUANDO PIERDE: {perdida_promedio:.2f}%")
    print(f"Ratio Riesgo/Recompensa: {ratio:.2f}")
    print(f"Win rate: {win_rate:.1f}%")