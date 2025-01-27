from config import BETSSON_HEADERS_LIGAS
import requests
import json
#      https://www.betsson.co/api/sb/v1/widgets/view/v1?categoryIds=1&configurationKey=sportsbook.category&excludedWidgetKeys=sportsbook.tournament.carousel&slug=futbol&timezoneOffsetMinutes=-300 
url = "https://www.betsson.co/api/sb/v1/widgets/view/v1?categoryIds=1&configurationKey=sportsbook.category&excludedWidgetKeys=sportsbook.tournament.carousel&slug=futbol&timezoneOffsetMinutes=-300"

payload = {}

response = requests.request("GET", url, headers=BETSSON_HEADERS_LIGAS, data=payload)
if response.status_code == 200:
    response = response.json()
else:
    response = None

if response:
    # guardar respuesta en un archivo json 
    #with open("exploracion_manual\ligas.json", "w") as file:
    #    json.dump(response, file)
    # response["data"]["widgets"][2]["key"] # se obtiene el key del id del widget de competencias
    # competencias = response["data"]["widgets"][2]["data"]["data"]["items"] # se obtiene todas las competencias
    # sportsbook.category.competition 
    # a continuacion vamos a tratar de obtener informacion de CompetitionName como el label
    
    lista_competencias = []

    # verificar si response contiene la key "data"
    if "data" in response:
        # verificar si data contiene la key "widgets"
        if "widgets" in response["data"]:
            # verificar si widgets es de tipo lista 
            if isinstance(response["data"]["widgets"], list):
                # recorrer la lista de widgets
                for widget in response["data"]["widgets"]:
                    # verificar si el widget contiene la key "key"
                    if "key" in widget:
                        # verificar si el key del widget es igual a "sportsbook.category.competition"
                        if widget["key"] == "sportsbook.category.competition":
                            # verificar si el widget contiene la key "data"
                            if "data" in widget:
                                # verificar si data contiene la key "data"
                                if "data" in widget["data"]:
                                    # verificar si data contiene la key "items"
                                    if "items" in widget["data"]["data"]:
                                        # verificar si items es de tipo lista
                                        if isinstance(widget["data"]["data"]["items"], list):
                                            # recorrer la lista de items
                                            for item in widget["data"]["data"]["items"]:
                                                # verificar si el item contiene la key "labelType" y es igual a "CompetitionName"
                                                if "labelType" in item and item["labelType"] == "CompetitionName":
                                                    # verificar si el item contiene la key "label"
                                                    label = item["label"] if "label" in item else None
                                                    # verificar si el item contiene la key "slug"
                                                    slug = item["slug"] if "slug" in item else None
                                                    # verificar si el item contiene la key "visibleCount"
                                                    visibleCount = item["visibleCount"] if "visibleCount" in item else None
                                                    # verificar si el item contiene la key "widgetRequest"
                                                    widgetRequest = item["widgetRequest"] if "widgetRequest" in item else None
                                                    if widgetRequest:
                                                        # verificar si widgetRequest contiene la key "categoryIds" y es de tipo lista
                                                        categoryIds = widgetRequest["categoryIds"] if "categoryIds" in widgetRequest and isinstance(widgetRequest["categoryIds"], list) else None
                                                        # verificar si widgetRequest contiene la key "competitionIds" y es de tipo lista 
                                                        competitionIds = widgetRequest["competitionIds"] if "competitionIds" in widgetRequest and isinstance(widgetRequest["competitionIds"], list) else None
                                                        # verificar si widgetRequest contiene la key "regionIds" y es de tipo lista 
                                                        regionIds = widgetRequest["regionIds"] if "regionIds" in widgetRequest and isinstance(widgetRequest["regionIds"], list) else None
                                                        # añadimos la informacion a la lista de competencias
                                                        lista_competencias.append({
                                                            "label": label,
                                                            "slug": slug,
                                                            "visibleCount": visibleCount,
                                                            "categoryIds": categoryIds,
                                                            "competitionIds": competitionIds,
                                                            "regionIds": regionIds
                                                        })
                                                    """
                                                    # verificar si el item contiene la key "metaData" y si es de tipo lista
                                                    if "metaData" in item and isinstance(item["metaData"], list):
                                                        # recorrer la lista de metaData
                                                        for metaData in item["metaData"]:
                                                            # verificar si el metaData contiene la key "competitionId"
                                                            competitionId = metaData["competitionId"] if "competitionId" in metaData else None
                                                            # verificar si el metaData contiene la key "startDate"
                                                            startDate = metaData["startDate"] if "startDate" in metaData else None
                                                    """
                                            #guardar la lista de competencias en un archivo json
                                            with open("exploracion_manual\competencias.json", "w") as file:
                                                json.dump(lista_competencias, file)
                                                print("Archivo guardado como competencias.json")
                                        else:
                                            print("El key 'items' no es una lista")
                                    else:
                                        print("No se encontro la key 'items' en data")
                                else:
                                    print("No se encontro la key 'data' en data")
                            else:
                                print("No se encontro la key 'data' en widget")
                            break                    
                        else:
                            print("El key del widget no es igual a 'sportsbook.category.competition'")
                    else:
                        print("No se encontro la key 'key' en widget")
    print("Archivo guardado")
else:
    print("No se pudo guardar el archivo")
