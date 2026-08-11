# Lección 2: LOOPS (repetir código)
# Queremos monitorear varias acciones: AAPL, MSFT, NVDA, TSLA

# Sin loops (aburrido):
print("Analizando AAPL...")
print("Analizando MSFT...")
print("Analizando NVDA...")
print("Analizando TSLA...")

# Con loops (inteligente):
print("\n--- USANDO LOOPS ---\n")

acciones = ["AAPL", "MSFT", "NVDA", "TSLA"]

for accion in acciones:
    print(f"Analizando {accion}...")

# Ahora con más lógica
print("\n--- CON DATOS SIMULADOS ---\n")

precios = {
    "AAPL": 228.50,
    "MSFT": 425.30,
    "NVDA": 142.80,
    "TSLA": 243.15
}

for ticker, precio in precios.items():
    cambio_porcentaje = -2.5  # Simulamos que bajó 2.5%
    nuevo_precio = precio * (1 + cambio_porcentaje / 100)
    
    print(f"{ticker}: ${precio} → ${nuevo_precio:.2f} ({cambio_porcentaje}%)")