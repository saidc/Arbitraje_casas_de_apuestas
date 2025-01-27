
from Betsson.Betsson_config import BETSSON_HEADERS, BETSSON_HEADERS_SCRAPING_DEPORTES, Betsson
from bs4 import BeautifulSoup
import datetime
import requests
import json

def Betsson_scraping(url):
    payload = {}
    response = requests.request("GET", url, headers=BETSSON_HEADERS_SCRAPING_DEPORTES, data=payload)
    sportCatalog_tree = {}
    # verificamos que la respuesta sea 200
    if response.status_code == 200:
        # pasamos el texto de reaponse a un objeto BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # se busca un script con id="halo-app-state" 
        script = soup.find("script", id="halo-app-state")

        # se obtiene el contenido del script
        script = script.string

        # se obtiene el contenido del script en formato json
        script = json.loads(script)

        # se verifica si el script contiene la key "NGRX_STATE"
        if "NGRX_STATE" in script:
            # se obtiene el valor de la key "NGRX_STATE"
            ngrx_state = script["NGRX_STATE"]

            # se verifica si ngrx_state contiene la key "sportsbook"
            if "sportsbook" in ngrx_state:
                # se obtiene el valor de la key "leagues"
                sportsbook = ngrx_state["sportsbook"]

                # se verifica si sportsbook contiene la key "sportCatalog"
                if "sportCatalog" in sportsbook:
                    # se obtiene el valor de la key "sportCatalog"
                    sportCatalog = sportsbook["sportCatalog"]

                    # se verifica si sportCatalog contiene la key "offering"
                    if "offering" in sportCatalog:
                        # se obtiene el valor de la key "offering"
                        offering = sportCatalog["offering"]

                        # se verifica si offering contiene la key "indexByIdSlug"
                        if "indexByIdSlug" in offering:
                            # se obtiene el valor de la key "indexByIdSlug"
                            indexByIdSlug = offering["indexByIdSlug"]
                            
                            # se verifica si indexByIdSlug es de tipo diccionario
                            if isinstance(indexByIdSlug, dict):
                                # se obtiene las keys del diccionario 
                                keys = indexByIdSlug.keys()
                                # se recorre las keys
                                for key in keys:
                                    # se obtiene el valor de la key
                                    value = indexByIdSlug[key]
                                    # hace un split de la key con el caracter "/"
                                    key_split = key.split("/")
                                    # se hace un split del value con el caracter "/"
                                    value_split = value.split("/")
                                    # se hace un conteo de los elementos de key_split y value_split y asignamos a sportCatalog_tree , teniendo en cuenta el orden de gerarquia [categoryIds, regionIds, competitionIds, eventId]
                                    # Ejemplo: "1/14/16/f-rkgznc0f6ewqfpnw_now2g":"futbol/alemania/alemania-2-bundesliga/greuther-furth-1-fc-kaiserslautern?eventId=f-RKGznC0f6EWQFpNW_nOW2g"  => {"1": { categoryIds:"1", "categoryName": "futbol", "regionIds": { "14": { regionIds: "14", "regionName": "alemania", "competitionIds": { "16": { competitionIds: "16", "competitionName": "alemania-2-bundesliga", "eventId": { "f-rkgznc0f6ewqfpnw_now2g": { eventId: "f-rkgznc0f6ewqfpnw_now2g", "eventName": "greuther-furth-1-fc-kaiserslautern" } } } } } } }
                                    # ten presente que un key y un value puede tener 1 o mas elementos separados por el caracter "/" es decir que el split puede tener uno o mas elementos
                                    if len(value_split) >= len(key_split):
                                        for i in range(len(key_split)):
                                            # verifico el nivel de jerarquia [categoryIds, regionIds, competitionIds, eventId]
                                            if i == 0:
                                                # obtengo el key 0
                                                k = key_split[0]
                                                # obtengo el value 0
                                                v = value_split[0]
                                                # verifico si el key no esta en sportCatalog_tree
                                                if k not in sportCatalog_tree:
                                                    # añado el key al diccionario
                                                    sportCatalog_tree[key_split[i]] = {"categoryId": k, "categoryName": v, "regionIds": {}}
                                            elif i == 1:
                                                # obtengo el key 0
                                                k_0 = key_split[0]
                                                # obtengo el value 0
                                                v_0 = value_split[0]
                                                # obtengo el key 1
                                                k_1 = key_split[1]
                                                # obtengo el value 1
                                                v_1 = value_split[1]
                                                # verifico si el key no esta en sportCatalog_tree
                                                if k_1 not in sportCatalog_tree[k_0]["regionIds"]:
                                                    # añado el key al diccionario
                                                    sportCatalog_tree[k_0]["regionIds"][k_1] = {"regionId": k_1, "regionName": v_1, "competitionIds": {}}
                                            elif i == 2:
                                                # obtengo el key 0
                                                k_0 = key_split[0]
                                                # obtengo el value 0
                                                v_0 = value_split[0]
                                                # obtengo el key 1
                                                k_1 = key_split[1]
                                                # obtengo el value 1
                                                v_1 = value_split[1]
                                                # obtengo el key 2
                                                k_2 = key_split[2]
                                                # obtengo el value 2
                                                v_2 = value_split[2]
                                                # verifico si el key no esta en sportCatalog_tree
                                                if k_2 not in sportCatalog_tree[k_0]["regionIds"][k_1]["competitionIds"]:
                                                    # añado el key al diccionario
                                                    sportCatalog_tree[k_0]["regionIds"][k_1]["competitionIds"][k_2] = {"competitionId": k_2, "competitionName": v_2, "eventIds": {}}
                                            elif i == 3:
                                                # obtengo el key 0
                                                k_0 = key_split[0]
                                                # obtengo el value 0
                                                v_0 = value_split[0]
                                                # obtengo el key 1
                                                k_1 = key_split[1]
                                                # obtengo el value 1
                                                v_1 = value_split[1]
                                                # obtengo el key 2
                                                k_2 = key_split[2]
                                                # obtengo el value 2
                                                v_2 = value_split[2]
                                                # obtengo el key 3
                                                k_3 = key_split[3]
                                                # obtengo el value 3
                                                v_3 = value_split[3]
                                                # verifico si el key no esta en sportCatalog_tree
                                                if k_3 not in sportCatalog_tree[k_0]["regionIds"][k_1]["competitionIds"][k_2]["eventIds"]:
                                                    # añado el key al diccionario
                                                    sportCatalog_tree[k_0]["regionIds"][k_1]["competitionIds"][k_2]["eventIds"][k_3] = {"eventId": k_3, "eventName": v_3}
                                # verifica si sportCatalog_tree no esta vacio
                                if sportCatalog_tree:
                                    return sportCatalog_tree
    return None                            

def make_get_request(url, headers, payload):
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def obtener_partidos_Betsson(categoryId,competitionId,eventPhase):
    #rango_de_fechas = generar_rango_fechas()
    #link = "https://www.betsson.co/api/sb/v1/widgets/events-table/v2?categoryIds=138&competitionIds=26430&eventPhase=All&eventSortBy=StartDate&maxMarketCount=3&pageNumber=1&regionIds=1"
    #link = "https://www.betsson.co/api/sb/v1/widgets/events-table/v2?categoryIds=11&competitionIds=23122&eventPhase=Prematch&eventSortBy=StartDate&maxMarketCount=3&pageNumber=1&startsBefore=2025-01-11T04:59:59Z&startsOnOrAfter=2025-01-10T05:00:00Z"
    link = f"https://www.betsson.co/api/sb/v1/widgets/events-table/v2?categoryIds={categoryId}&competitionIds={competitionId}&eventPhase={eventPhase}&eventSortBy=StartDate"
    print(link)
    response = make_get_request(link, BETSSON_HEADERS, {})
    # obtenermos el json de la respuesta y verificamos si es distinto de None
    # verificar si response contiene skeleton, topics, topicsMap, data, referenceId
    if response:
        lista_de_partidos = {}

        if "skeleton" in response:
            # verificasr si response["skeleton"] contiene "eventIds", "marketTemplates", "marketTimeFrames", "marketTimeFrameLabels"
            if "eventIds" in response["skeleton"]:
                eventIds = response["skeleton"]["eventIds"]
                
                lista_de_partidos = { id: { "eventId": id } for id in eventIds }
                
            """
            if "marketTemplates" in response["skeleton"]:
                marketTemplates = response["skeleton"]["marketTemplates"]
                if marketTemplates:
                    lista_de_partidos.append(marketTemplates)
            if "marketTimeFrames" in response["skeleton"]:
                marketTimeFrames = response["skeleton"]["marketTimeFrames"]
                if marketTimeFrames:
                    lista_de_partidos.append(marketTimeFrames)
            if "marketTimeFrameLabels" in response["skeleton"]:
                marketTimeFrameLabels = response["skeleton"]["marketTimeFrameLabels"]
                if marketTimeFrameLabels:
                    lista_de_partidos.append(marketTimeFrameLabels)
            """
        #if "topics" in response:   
        #if "topicsMap" in response :
        if "data" in response :
            data = response["data"]
            if data:
                # verificar si data contiene "events"
                if "events" in data:
                    events = data["events"]
                    if events:
                        for event in events:
                            if "id" in event:
                                id = event["id"]
                                if id in lista_de_partidos:
                                    
                                    new_event_data = {                                    
                                        "categoryId": event["categoryId"],
                                        "categoryName": event["categoryName"],
                                        "regionId": event["regionId"],
                                        "regionName": event["regionName"],
                                        "competitionId": event["competitionId"],
                                        "slug": event["slug"],
                                        "phase": event["phase"],
                                        "startDate": event["startDate"],
                                        "categoryTrackingLabel": event["categoryTrackingLabel"],
                                        "competitionTrackingLabel": event["competitionTrackingLabel"],
                                        "regionTrackingLabel": event["regionTrackingLabel"],
                                        "neutralPath": event["neutralPath"],
                                        "label": event["label"]
                                        
                                    }
                                    lista_de_partidos[id].update(new_event_data)
                                    #"participants": event[{"label":p["label"],"id":p["id"],"sortOrder":p["sortOrder"]} for p in participants],
                                    participants = []
                                    for p in event["participants"]:
                                        participant = {
                                            "label": p["label"],
                                            "id": p["id"],
                                            "sortOrder": p["sortOrder"]
                                        }
                                        participants.append(participant)
                                    lista_de_partidos[id]["participants"] = participants
        return lista_de_partidos
    return None


def actualizar_catalogo_deportes_de_Betsson(deportes_seleccionados, catalogo_deportes, actualizacion_de_catalogo_deportes):
    # verificar si catalogo_deportes es un diccionario y actualizacion_de_catalogo_deportes es un diccionario y deportes_seleccionados es una lista
    if isinstance(catalogo_deportes, dict) and isinstance(actualizacion_de_catalogo_deportes, dict) and isinstance(deportes_seleccionados, list):
        # verificar si catalogo_deportes contiene el key Betsson 
        if Betsson not in catalogo_deportes:
            catalogo_deportes[Betsson] = {"name": Betsson, "Catalogo_de_deportes": {}}
        # obtener las keys de catalogo_deportes y las keys de actualizacion_de_catalogo_deportes
        keys_catalogo_deportes = catalogo_deportes[Betsson]["Catalogo_de_deportes"].keys()
        keys_actualizacion_de_catalogo_deportes = [k for k in actualizacion_de_catalogo_deportes.keys() if (len(deportes_seleccionados)== 0 or k in deportes_seleccionados) ]
        # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
        for key in keys_actualizacion_de_catalogo_deportes:
            if key not in keys_catalogo_deportes:
                catalogo_deportes[Betsson]["Catalogo_de_deportes"][key] = actualizacion_de_catalogo_deportes[key]
            else:
                # verificar si catalogo_deportes contiene la key regionIds
                if "regionIds" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]:
                    catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"] = actualizacion_de_catalogo_deportes[key]["regionIds"]
                else:
                    # obtener las keys de regionIds de catalogo_deportes y las keys de regionIds de actualizacion_de_catalogo_deportes
                    keys_regionIds = catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"].keys()
                    keys_actualizacion_regionIds =   actualizacion_de_catalogo_deportes[key]["regionIds"].keys()
                    # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
                    for key_regionIds in keys_actualizacion_regionIds:
                        if key_regionIds not in keys_regionIds:
                            catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]
                        else:
                            # verificar si catalogo_deportes contiene la key competitionIds
                            if "competitionIds" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]:
                                catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"]
                            else:
                                # obtener las keys de competitionIds de catalogo_deportes y las keys de competitionIds de actualizacion_de_catalogo_deportes
                                keys_competitionIds = catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"].keys()
                                keys_actualizacion_competitionIds =   actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"].keys()
                                # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
                                for key_competitionIds in keys_actualizacion_competitionIds:
                                    if key_competitionIds not in keys_competitionIds:
                                        catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]
                                    else:
                                        # verificar si catalogo_deportes contiene la key eventIds
                                        if "eventIds" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]:
                                            catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"]
                                        else:
                                            # obtener las keys de eventId de catalogo_deportes y las keys de eventId de actualizacion_de_catalogo_deportes
                                            keys_eventId = catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"].keys()
                                            keys_actualizacion_eventId =   actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"].keys()
                                            # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
                                            for key_eventId in keys_actualizacion_eventId:
                                                if key_eventId not in keys_eventId:
                                                    catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"][key_eventId] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"][key_eventId]
                                                # --------------------------------------------------------------------------------
    return catalogo_deportes                                                         

"""

def actualizar_catalogo_deportes_de_Betsson(deportes_seleccionados, catalogo_deportes, actualizacion_de_catalogo_deportes):
    # verificar si catalogo_deportes es un diccionario y actualizacion_de_catalogo_deportes es un diccionario y deportes_seleccionados es una lista
    if isinstance(catalogo_deportes, dict) and isinstance(actualizacion_de_catalogo_deportes, dict) and isinstance(deportes_seleccionados, list):
        # verificar si catalogo_deportes contiene el key Betsson 
        if Betsson not in catalogo_deportes:
            catalogo_deportes[Betsson] = {"name": Betsson, "Catalogo_de_deportes": {}}
        # obtener las keys de catalogo_deportes y las keys de actualizacion_de_catalogo_deportes
        keys_catalogo_deportes = catalogo_deportes[Betsson]["Catalogo_de_deportes"].keys()
        keys_actualizacion_de_catalogo_deportes = [k for k in actualizacion_de_catalogo_deportes.keys() if (len(deportes_seleccionados)== 0 or k in deportes_seleccionados) ]
        # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
        for key in keys_actualizacion_de_catalogo_deportes:
            if key not in keys_catalogo_deportes:
                catalogo_deportes[Betsson]["Catalogo_de_deportes"][key] = actualizacion_de_catalogo_deportes[key]
            else:
                # verificar si catalogo_deportes contiene la key regionIds
                if "regionIds" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]:
                    catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"] = actualizacion_de_catalogo_deportes[key]["regionIds"]
                else:
                    # obtener las keys de regionIds de catalogo_deportes y las keys de regionIds de actualizacion_de_catalogo_deportes
                    keys_regionIds = catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"].keys()
                    keys_actualizacion_regionIds =   actualizacion_de_catalogo_deportes[key]["regionIds"].keys()
                    # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
                    for key_regionIds in keys_actualizacion_regionIds:
                        if key_regionIds not in keys_regionIds:
                            catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]
                        else:
                            # verificar si catalogo_deportes contiene la key competitionIds
                            if "competitionIds" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]:
                                catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"]
                            else:
                                # obtener las keys de competitionIds de catalogo_deportes y las keys de competitionIds de actualizacion_de_catalogo_deportes
                                keys_competitionIds = catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"].keys()
                                keys_actualizacion_competitionIds =   actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"].keys()
                                # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
                                for key_competitionIds in keys_actualizacion_competitionIds:
                                    if key_competitionIds not in keys_competitionIds:
                                        catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]
                                    else:
                                        # verificar si catalogo_deportes contiene la key eventIds
                                        if "eventIds" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]:
                                            catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"]
                                        else:
                                            # obtener las keys de eventId de catalogo_deportes y las keys de eventId de actualizacion_de_catalogo_deportes
                                            keys_eventId = catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"].keys()
                                            keys_actualizacion_eventId =   actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"].keys()
                                            # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
                                            for key_eventId in keys_actualizacion_eventId:
                                                if key_eventId not in keys_eventId:
                                                    catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"][key_eventId] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"][key_eventId]
                                                # --------------------------------------------------------------------------------
                                                else:
                                                    # verificar si catalogo_deportes contiene la key apuestas
                                                    if "apuestas" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]:
                                                        catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"]
                                                    else:
                                                        partido_vencido = False
                                                        # verificar si catalogo_deportes contiene la key startDate 
                                                        if "startDate" in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]:
                                                            # verificar si la fecha de startDate ya ha vencido, es decir que es menor a la fecha actual
                                                            startDate = catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["startDate"]
                                                            # convertir en datetime la fecha de startDate
                                                            startDate = datetime.strptime(startDate, "%Y-%m-%dT%H:%M:%S.%fZ")
                                                            # obtener la fecha actual
                                                            fecha_actual = datetime.now()
                                                            # verificar si la fecha de startDate es menor a la fecha actual
                                                            partido_vencido = startDate < fecha_actual

                                                        if not partido_vencido:
                                                            # obtener las keys de apuestas de catalogo_deportes y las keys de apuestas de actualizacion_de_catalogo_deportes
                                                            keys_apuestas = catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"].keys()
                                                            keys_actualizacion_apuestas = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"].keys()
                                                            # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
                                                            for key_apuestas in keys_actualizacion_apuestas:
                                                                if key_apuestas not in keys_apuestas:
                                                                    catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]
                                                                else:
                                                                    # verificar si catalogo_deportes contiene la key marketIds
                                                                    if "marketIds" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]:
                                                                        catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"]
                                                                    else:
                                                                        # obtener las keys de marketIds de catalogo_deportes y las keys de marketIds de actualizacion_de_catalogo_deportes
                                                                        keys_marketIds = catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"].keys()
                                                                        keys_actualizacion_marketIds = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"].keys()
                                                                        # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
                                                                        for key_marketIds in keys_actualizacion_marketIds:
                                                                            if key_marketIds not in keys_marketIds:
                                                                                catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]
                                                                            else: 
                                                                                # verificar si catalogo_deportes contiene la key apuestas
                                                                                if "apuestas" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]:
                                                                                    catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"]
                                                                                else: 
                                                                                    # obtener las keys de apuestas de catalogo_deportes y las keys de apuestas de actualizacion_de_catalogo_deportes
                                                                                    keys_apuestas_2 = catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"].keys()
                                                                                    keys_actualizacion_apuestas_2 = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"].keys()
                                                                                    # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
                                                                                    for key_apuestas_2 in keys_actualizacion_apuestas_2:
                                                                                        if key_apuestas_2 not in keys_apuestas_2:
                                                                                            catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]
                                                                                        else:
                                                                                            # verificar si catalogo_deportes contiene la key odds
                                                                                            if "odds" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]:
                                                                                                catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["odds"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["odds"]
                                                                                            else:
                                                                                                # verificar si el valor de odds en actualizacion_de_catalogo_deportes es distinto al valor de odds en catalogo_deportes
                                                                                                if actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["odds"] != catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["odds"]:
                                                                                                    catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["odds"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["odds"]
                                                                                            
                                                                                            # verificar si catalogo_deportes contiene la key status
                                                                                            if "status" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]:
                                                                                                catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["status"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["status"]
                                                                                            else:
                                                                                                # verificar si el valor de status en actualizacion_de_catalogo_deportes es distinto al valor de status en catalogo_deportes
                                                                                                if actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["status"] != catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["status"]:
                                                                                                    catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["status"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["status"]
    return catalogo_deportes                                                         

"""
