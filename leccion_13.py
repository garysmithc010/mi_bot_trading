import anthropic

client = anthropic.Anthropic()

candidato = {
    "ticker": "AAPL",
    "precio": 228.50,
    "cambio_7_dias": -5.2,
    "media_movil_50": 225.00
}

mensaje = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=300,
    messages=[
        {
            "role": "user",
            "content": f"""
            Analiza este setup de trading:
            
            Acción: {candidato['ticker']}
            Precio actual: ${candidato['precio']}
            Cambio en 7 días: {candidato['cambio_7_dias']}%
            Media móvil 50 días: ${candidato['media_movil_50']}
            
            ¿Es buena oportunidad de compra a corto plazo (2-3 semanas)?
            Responde en máximo 3 líneas.
            """
        }
    ]
)

print(mensaje.content[0].text)