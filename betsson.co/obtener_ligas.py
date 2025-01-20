from config import BETSSON_HEADERS_LIGAS
import requests
import json

url = "https://www.betsson.co/api/sb/v1/widgets/view/v1?categoryIds=1&configurationKey=sportsbook.category&excludedWidgetKeys=sportsbook.tournament.carousel&slug=futbol&timezoneOffsetMinutes=-300"

payload = {}

response = requests.request("GET", url, headers=BETSSON_HEADERS_LIGAS, data=payload)
if response.status_code == 200:
    response = response.json()
else:
    response = None

if response:
    # guardar respuesta en un archivo json 
    with open("exploracion_manual\ligas.json", "w") as file:
        json.dump(response, file)
        
    print("Archivo guardado")
else:
    print("No se pudo guardar el archivo")
