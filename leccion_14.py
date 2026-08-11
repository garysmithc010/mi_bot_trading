import yfinance as yf
import anthropic

client = anthropic.Anthropic()

acciones = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", 
            "JPM", "V", "JNJ", "WMT", "PG", "XOM", "DIS", "NFLX", "ADBE"]

for ticker in acciones:
    empresa = yf.Ticker(ticker)
    datos = empresa.history(period="60d")
    precios_cierre = datos["Close"]
    
    precio_hoy = precios_cierre.iloc[-1]
    precio_hace_7_dias = precios_cierre.iloc[-7]
    media_movil_50 = precios_cierre.rolling(50).mean().iloc[-1]
    
    cambio = ((precio_hoy - precio_hace_7_dias) / precio_hace_7_dias) * 100
    
    print(f"\n{ticker}: Precio ${precio_hoy:.2f} | Cambio {cambio:.2f}% | Media ${media_movil_50:.2f}")
    
    if cambio < -5 and precio_hoy > media_movil_50:
        print(f"  ⚠️ {ticker} ES CANDIDATO - preguntando a Claude...")
        
        mensaje = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    Analiza este setup de trading:
                    
                    Acción: {ticker}
                    Precio actual: ${precio_hoy:.2f}
                    Cambio en 7 días: {cambio:.2f}%
                    Media móvil 50 días: ${media_movil_50:.2f}
                    
                    ¿Es buena oportunidad de compra a corto plazo (2-3 semanas)?
                    Responde en máximo 3 líneas.
                    """
                }
            ]
        )
        
        print(f"  Claude dice: {mensaje.content[0].text}")
    else:
        print(f"  {ticker} no cumple criterios")