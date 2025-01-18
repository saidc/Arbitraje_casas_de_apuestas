
from config import BETSSON_HEADERS, betsson_config_file_path, betsson_partidos_Prematch_file_path, EVENT_PHASE_PREMATCH
from config.tools import generar_rango_fechas
import requests
import datetime
import random
import json
import os


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

def obtener_partidos_con_apuestas():
    # leer archivo config_betsson.json 
    with open(betsson_config_file_path, "r") as file:
        betsson_config = json.load(file)
    
    Deportes = betsson_config["DEPORTES"]
    eventPhase = EVENT_PHASE_PREMATCH

    # verificar si el archivo json betsson_partidos_Prematch_file_path existe, si no existe se crea
    if not os.path.exists(betsson_partidos_Prematch_file_path):
        with open(betsson_partidos_Prematch_file_path, "w") as file:
            json.dump({}, file)

    # obtenemos el archivo json betsson_partidos_Prematch_file_path
    with open(betsson_partidos_Prematch_file_path, "r") as file:
        betsson_prematch_file = json.load(file)
    
    # creamos una copia de betsson_prematch_file
    betsson_prematch = betsson_prematch_file.copy()

    # borramos la variable betsson_prematch_file
    del betsson_prematch_file

    lista_de_solicitudes_de_obtener_partidos = []

    # recorrer el listado de Deportes
    for key in Deportes.keys():
        #print("\n\nDeporte: ", key)
        # obtener el valor del deporte
        deporte = Deportes[key]
        # obtener la lista de Eventos & Ligas
        ligas = deporte["Eventos & Ligas"]
        # obtener el valor de categoryId
        categoryId = deporte["categoryId"]
        # recorremos la lista de Ligas
        for liga in ligas.keys():
            # obtenemos el valor de la Liga
            liga_value = ligas[liga]
            # preguntamos si liga_value es tipo list
            if isinstance(liga_value, list):
                # recorremos la lista de ligas
                for partido in liga_value:
                    # obtener partidos de la liga
                    # obtenemos el nombre de la liga
                    name = partido["nombre"] if "nombre" in partido else "X"
                    # obtenemos el id de la liga 
                    competitionId = partido["competitionId"] if "competitionId" in partido else -1
                    #print(name,": ", competitionId)
                    if competitionId != -1:
                        lista_de_solicitudes_de_obtener_partidos.append((categoryId, competitionId, eventPhase))

    print("Iniciando solicitud de partidos...")

    # recorrer la lista de solicitudes de obtener_partidos y tener una barra de progreso de las solicitude de obtener_partidos
    for i, solicitud in enumerate(lista_de_solicitudes_de_obtener_partidos):
        categoryId, competitionId, eventPhase = solicitud
        print(f"\n\nSolicitud {i+1}/{len(lista_de_solicitudes_de_obtener_partidos)}")
        print(f"categoryId: {categoryId}, competitionId: {competitionId}, eventPhase: {eventPhase}")
        # Se solicitan los partidos Prematch de la categoria y competencia, ya estructurados
        lista_de_partidos = obtener_partidos(categoryId, competitionId, eventPhase)
        if lista_de_partidos:
            # se guarda el archivo en la carpeta partidos_Prematch siguiendo la estructura de config_betsson.json
            # 1 se actualiza la variable json betsson_prematch teniendo en cuenta el categoryId y competitionId
            # 1.1 verificamos que categoryId exista en betsson_prematch
            betsson_prematch[categoryId] = betsson_prematch[categoryId] if categoryId in betsson_prematch else {}
            # 1.2 verificamos que competitionId exista en betsson_prematch[categoryId]
            betsson_prematch[categoryId][competitionId] = betsson_prematch[categoryId][competitionId] if competitionId in betsson_prematch[categoryId] else {}
            # 1.3 actualizamos el valor de betsson_prematch[categoryId][competitionId] con la lista de partidos obtenidos usando update
            betsson_prematch[categoryId][competitionId].update(lista_de_partidos)


            # recorrer la lista de partidos obtenidos y obtener las apuestas
            for id in lista_de_partidos.keys():
                # obtener el id del evento
                eventId = lista_de_partidos[id]["eventId"]
                # Obtenemos las apuestas de un partido
                apuestas = obtener_apuestas(eventId)
                if apuestas:
                    # verificamos si contiene data 
                    if "data" in apuestas:
                        data = apuestas["data"]
                        if data:
                            # verificamos si contiene "widgets"
                            if "widgets" in data:
                                widgets = data["widgets"]
                                if widgets:
                                    # verificamos si widgets es de tipo lista 
                                    if isinstance(widgets, list):
                                        MarketList = None
                                        # recorremos la lista de widgets
                                        for widget in widgets:
                                            # buscamos el widget de tipo MarketList
                                            if "type" in widget and widget["type"] == "MarketList":
                                                MarketList = widget
                                                break
                                        # verificamos si MarketList es distinto de None
                                        if MarketList:
                                            # verificamos si contiene "data"
                                            if "data" in MarketList:
                                                market_data = MarketList["data"]
                                                if market_data:
                                                    #verificar que data contenga skeleton
                                                    if "skeleton" in market_data:
                                                        skeleton = market_data["skeleton"]
                                                        if skeleton:
                                                            #verificar que skeleton contenga "marketIdByMarketTemplates"
                                                            if "marketIdByMarketTemplates" in skeleton:
                                                                marketIdByMarketTemplates = skeleton["marketIdByMarketTemplates"]
                                                                if marketIdByMarketTemplates:
                                                                    #verificar que marketIdByMarketTemplates sea de tipo lista
                                                                    if isinstance(marketIdByMarketTemplates, list):
                                                                        marketTemplateId_for_every_marketId = {}
                                                                        #recorrer la lista de marketIdByMarketTemplates
                                                                        for marketIdByMarketTemplate in marketIdByMarketTemplates:
                                                                            #verificar que marketIdByMarketTemplate contenga "marketTemplateId"
                                                                            marketTemplateId = marketIdByMarketTemplate["marketTemplateId"] if "marketTemplateId" in marketIdByMarketTemplate else None
                                                                            #verificar que market contenga "marketIds"
                                                                            marketIds = marketIdByMarketTemplate["marketIds"] if "marketIds" in marketIdByMarketTemplate else None
                                                                            #verificar que marketIds sea de tipo lista
                                                                            if marketIds and isinstance(marketIds, list) and marketTemplateId:
                                                                                # añadimos el marketTemplateId y market Ids a la lista de apuestas en betsson_prematch
                                                                                betsson_prematch[categoryId][competitionId]["apuestas"] = betsson_prematch[categoryId][competitionId]["apuestas"] if "apuestas" in betsson_prematch[categoryId][competitionId] else {}
                                                                                betsson_prematch[categoryId][competitionId]["apuestas"][marketTemplateId] = {
                                                                                    "marketTemplateId": marketTemplateId, 
                                                                                    "marketIds": {}
                                                                                    #"marketIds": [ {f"{marketId}":{"marketId":marketId}} for marketId in marketIds ]
                                                                                }
                                                                                for marketId in marketIds:
                                                                                    betsson_prematch[categoryId][competitionId]["apuestas"][marketTemplateId]["marketIds"][marketId] = {
                                                                                        "marketId": marketId
                                                                                    }
                                                                                    # para cada marketId se le asigna su respectivo maketTemplateId
                                                                                    marketTemplateId_for_every_marketId[marketId] = marketTemplateId
                                                                        #verificamos si market_data contiene "data"
                                                                        if "data" in market_data:
                                                                            market_data_data = market_data["data"]
                                                                            if market_data_data:
                                                                                #verificamos si market_data_data contiene "markets"
                                                                                if "markets" in market_data_data:
                                                                                    markets = market_data_data["markets"]
                                                                                    if markets:
                                                                                        #verificamos si markets es de tipo lista
                                                                                        if isinstance(markets, list):
                                                                                            #recorrer la lista de markets
                                                                                            for market in markets:
                                                                                                #verificar si market contiene "id"
                                                                                                marketId = market["id"] if "id" in market else None
                                                                                                #verificar si market contiene "marketTemplateId"
                                                                                                market_marketTemplateId = market["marketTemplateId"] if "marketTemplateId" in market else None
                                                                                                #verificar si market contiene "columnLayout"
                                                                                                columnLayout = market["columnLayout"] if "columnLayout" in market else None
                                                                                                #verificamos si market contiene "accordionGroup" y dentro de este "groupKey" y "tabKey"
                                                                                                accordionGroup = market["accordionGroup"] if "accordionGroup" in market and "groupKey" in market["accordionGroup"] else None
                                                                                                #verificamos si market contiene "sortOrder"
                                                                                                sortOrder = market["sortOrder"] if "sortOrder" in market else None
                                                                                                #verificamos si market contiene "marketFriendlyName"
                                                                                                marketFriendlyName = market["marketFriendlyName"] if "marketFriendlyName" in market else None
                                                                                                #verificamos si market contiene "label"
                                                                                                label = market["label"] if "label" in market else None
                                                                                                #verificamos si market contiene "status" , el valor mas importante es "Open"
                                                                                                status = market["status"] if "status" in market else None
                                                                                                #verificamos si market contiene "lineValue"
                                                                                                lineValue = market["lineValue"] if "lineValue" in market else None
                                                                                                #verificamos si market contiene "lineValueRaw"
                                                                                                lineValueRaw = market["lineValueRaw"] if "lineValueRaw" in market else None
                                                                                                #verificamos si market_marketTemplateId esta en la lista de apuestas en betsson_prematch
                                                                                                if market_marketTemplateId in betsson_prematch[categoryId][competitionId]["apuestas"]:
                                                                                                    #añadimos la informacion de columnLayout a market_marketTemplateId
                                                                                                    betsson_prematch[categoryId][competitionId]["apuestas"][market_marketTemplateId]["columnLayout"] = columnLayout
                                                                                                    #verificamos si marketId esta en la lista de apuestas en betsson_prematch
                                                                                                    if marketId in betsson_prematch[categoryId][competitionId]["apuestas"][market_marketTemplateId]["marketIds"]:
                                                                                                        if columnLayout:
                                                                                                            betsson_prematch[categoryId][competitionId]["apuestas"][market_marketTemplateId]["marketIds"][marketId]["columnLayout"] = columnLayout
                                                                                                        if accordionGroup:
                                                                                                            betsson_prematch[categoryId][competitionId]["apuestas"][market_marketTemplateId]["marketIds"][marketId]["groupKey"] = accordionGroup["groupKey"]
                                                                                                            betsson_prematch[categoryId][competitionId]["apuestas"][market_marketTemplateId]["marketIds"][marketId]["tabKey"] = accordionGroup["tabKey"]
                                                                                                        if sortOrder:
                                                                                                            betsson_prematch[categoryId][competitionId]["apuestas"][market_marketTemplateId]["marketIds"][marketId]["sortOrder"] = sortOrder
                                                                                                        if marketFriendlyName:
                                                                                                            betsson_prematch[categoryId][competitionId]["apuestas"][market_marketTemplateId]["marketIds"][marketId]["marketFriendlyName"] = marketFriendlyName
                                                                                                        if label:
                                                                                                            betsson_prematch[categoryId][competitionId]["apuestas"][market_marketTemplateId]["marketIds"][marketId]["label"] = label
                                                                                                        if status:
                                                                                                            betsson_prematch[categoryId][competitionId]["apuestas"][market_marketTemplateId]["marketIds"][marketId]["status"] = status
                                                                                                        if lineValue:
                                                                                                            betsson_prematch[categoryId][competitionId]["apuestas"][market_marketTemplateId]["marketIds"][marketId]["lineValue"] = lineValue
                                                                                                        if lineValueRaw:
                                                                                                            betsson_prematch[categoryId][competitionId]["apuestas"][market_marketTemplateId]["marketIds"][marketId]["lineValueRaw"] = lineValueRaw
                                                                                            #verificamos si market_data_data contiene "selections"
                                                                                            if "selections" in market_data_data:
                                                                                                #verificamos si selections es de tipo lista
                                                                                                if isinstance(market_data_data["selections"], list):
                                                                                                    #recorremos la lista de selections
                                                                                                    for selection in market_data_data["selections"]:
                                                                                                        #verificamos si market contiene "marketId"
                                                                                                        marketId = selection["marketId"] if "marketId" in selection else None
                                                                                                        selection_marketTemplateId = marketTemplateId_for_every_marketId[marketId] if marketId in marketTemplateId_for_every_marketId else None
                                                                                                        if selection_marketTemplateId:
                                                                                                            #verificamos si marketId esta en la lista de apuestas en betsson_prematch
                                                                                                            if marketId in betsson_prematch[categoryId][competitionId]["apuestas"][selection_marketTemplateId]["marketIds"]:
                                                                                                                #verificamos si selection contiene "odds"
                                                                                                                odds = selection["odds"] if "odds" in selection else None
                                                                                                                #verificamos si selection contiene "alternateLabel"
                                                                                                                alternateLabel = selection["alternateLabel"] if "alternateLabel" in selection else None
                                                                                                                #verificamos si selection contiene "status"
                                                                                                                status = selection["status"] if "status" in selection else None
                                                                                                                #verificamos si selection contiene "sortOrder"
                                                                                                                sortOrder = selection["sortOrder"] if "sortOrder" in selection else None
                                                                                                                #verificamos si selection contiene "participantId"
                                                                                                                participantId = selection["participantId"] if "participantId" in selection else None
                                                                                                                #verificamos si selection contiene "participantLabel"
                                                                                                                participantLabel = selection["participantLabel"] if "participantLabel" in selection else None
                                                                                                                #verificamos si selection contiene "selectionTemplateId"
                                                                                                                selectionTemplateId = selection["selectionTemplateId"] if "selectionTemplateId" in selection else None
                                                                                                                #verificamos si selection contiene "participant"
                                                                                                                participant = selection["participant"] if "participant" in selection else None
                                                                                                                #verificamos si selection contiene "id"
                                                                                                                selectionId = selection["id"] if "id" in selection else None
                                                                                                                #verificamos si selection contiene "label"
                                                                                                                label = selection["label"] if "label" in selection else None
                                                                                                                # verificamos si apuestas no esta en la lista de apuestas
                                                                                                                if "apuestas" not in betsson_prematch[categoryId][competitionId]["apuestas"][selection_marketTemplateId]["marketIds"][marketId]:
                                                                                                                    betsson_prematch[categoryId][competitionId]["apuestas"][selection_marketTemplateId]["marketIds"][marketId]["apuestas"] = []

                                                                                                                # añadimos la informacion de apuestas a la lista de apuestas en betsson_prematch
                                                                                                                betsson_prematch[categoryId][competitionId]["apuestas"][selection_marketTemplateId]["marketIds"][marketId]["apuestas"].append({
                                                                                                                    "odds": odds,
                                                                                                                    "alternateLabel": alternateLabel,
                                                                                                                    "status": status,
                                                                                                                    "sortOrder": sortOrder,
                                                                                                                    "participantId": participantId,
                                                                                                                    "participantLabel": participantLabel,
                                                                                                                    "selectionTemplateId": selectionTemplateId,
                                                                                                                    "participant": participant,
                                                                                                                    "id": selectionId,
                                                                                                                    "label": label
                                                                                                                })

    # guardamos el archivo json betsson_prematch en betsson_partidos_Prematch_file_path
    with open(betsson_partidos_Prematch_file_path, "w") as file:
        json.dump(betsson_prematch, file)

    print("Solicitud de partidos finalizada...")
    return betsson_prematch



                                                                                                




