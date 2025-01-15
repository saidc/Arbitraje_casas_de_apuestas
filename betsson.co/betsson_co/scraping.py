
from config import BETSSON_HEADERS
from config.tools import generar_rango_fechas
import requests

def make_get_request(url, headers, payload):
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    

def obtener_apuestas(eventId):
    link = f"https://www.betsson.co/api/sb/v1/widgets/view/v1?configurationKey=sportsbook.event.v2&eventId={eventId}&excludedWidgetKeys=sportsbook.events-table-mini"
    #"https://www.betsson.co/api/sb/v1/widgets/view/v1?configurationKey=sportsbook.event.v2&eventId=f-AVH3IksjfkqNfcQqw4m4-Q&excludedWidgetKeys=sportsbook.events-table-mini"
    
    response = make_get_request(link, BETSSON_HEADERS, {})
    # obtenermos el json de la respuesta y verificamos si es distinto de None
    if response:
        return response
    return None
        
def obtener_partidos(categoryId,competitionId,eventPhase):
    #rango_de_fechas = generar_rango_fechas()
    #link = "https://www.betsson.co/api/sb/v1/widgets/events-table/v2?categoryIds=138&competitionIds=26430&eventPhase=All&eventSortBy=StartDate&maxMarketCount=3&pageNumber=1&regionIds=1"
    #link = "https://www.betsson.co/api/sb/v1/widgets/events-table/v2?categoryIds=11&competitionIds=23122&eventPhase=Prematch&eventSortBy=StartDate&maxMarketCount=3&pageNumber=1&startsBefore=2025-01-11T04:59:59Z&startsOnOrAfter=2025-01-10T05:00:00Z"
    link = f"https://www.betsson.co/api/sb/v1/widgets/events-table/v2?categoryIds={categoryId}&competitionIds={competitionId}&eventPhase={eventPhase}&eventSortBy=StartDate"
    print(link)
    response = make_get_request(link, BETSSON_HEADERS, {})
    # obtenermos el json de la respuesta y verificamos si es distinto de None
    if response:
        return response
    return None


