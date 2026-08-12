import yfinance as yf
import anthropic
import os
import smtplib
from email.mime.text import MIMEText

client_claude = anthropic.Anthropic()

remitente = "garysmithc010@gmail.com"
password_gmail = os.getenv("GMAIL_APP_PASSWORD")
destinatario = "garysmithc010@gmail.com"

acciones = ["AAPL"]  # temporal, solo para probar

for ticker in acciones:
    empresa = yf.Ticker(ticker)
    datos = empresa.history(period="60d")
    precios_cierre = datos["Close"]
    
    precio_hoy = precios_cierre.iloc[-1]
    precio_hace_7_dias = precios_cierre.iloc[-7]
    media_movil_50 = precios_cierre.rolling(50).mean().iloc[-1]
    
    cambio = ((precio_hoy - precio_hace_7_dias) / precio_hace_7_dias) * 100
    
    print(f"\n{ticker}: Precio ${precio_hoy:.2f} | Cambio {cambio:.2f}% | Media ${media_movil_50:.2f}")
    
    if cambio < 100 and precio_hoy > 0:  # temporal, forzado para esta prueba
        print(f"  ⚠️ {ticker} ES CANDIDATO - preguntando a Claude...")
        
        mensaje_claude = client_claude.messages.create(
            model="claude-sonnet-5",
            max_tokens=1000,
            tools=[
                {
                    "type": "web_search_20250305",
                    "name": "web_search"
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    Busca noticias recientes sobre {ticker} (última semana) antes de responder.

                    Analiza este setup de trading considerando tanto los datos técnicos como 
                    cualquier noticia relevante que encuentres. Responde en texto plano sencillo, 
                    sin usar Markdown:

                    Acción: {ticker}
                    Precio actual: ${precio_hoy:.2f}
                    Cambio en 7 días: {cambio:.2f}%
                    Media móvil 50 días: ${media_movil_50:.2f}

                    ¿Es buena oportunidad de compra a corto plazo (2-3 semanas)? Explica si la 
                    caída/tendencia reciente parece ser por una razón temporal o algo más 
                    estructural, según lo que encuentres en noticias recientes.
                    """
                }
            ]
        )
        
        analisis = ""
        for bloque in mensaje_claude.content:
            if bloque.type == "text":
                analisis += bloque.text
        
        print(f"  Claude dice: {analisis}")
        
        correo = MIMEText(f"{ticker}\n\n{analisis}")
        correo["Subject"] = f"Oportunidad de trading: {ticker}"
        correo["From"] = remitente
        correo["To"] = destinatario
        
        with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
            servidor.starttls()
            servidor.login(remitente, password_gmail)
            servidor.send_message(correo)
        
        print(f"  Correo enviado sobre {ticker}")
    else:
        print(f"  {ticker} no cumple criterios")