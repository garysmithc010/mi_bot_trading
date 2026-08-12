import pandas as pd
import requests
from io import StringIO

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
respuesta = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", headers=headers)

tabla = pd.read_html(StringIO(respuesta.text))
sp500 = tabla[0]
tickers = sp500['Symbol'].tolist()

print("RESULTADO:")
print(f"Total de acciones encontradas: {len(tickers)}")
print(tickers[:10])