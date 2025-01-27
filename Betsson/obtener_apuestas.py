from betsson_co.scraping import obtener_apuestas, obtener_partidos
from config import betsson_config_file_path, betsson_partidos_Prematch_file_path
import datetime
import random
import json
import os

eventId = "f-QFVna7cEe0CZ2TQ3m_aeEw"

response = obtener_apuestas(eventId) # Obtenemos las apuestas de un partido

apuestas_list = {f"{eventId}":{}}

#verificamos si response es distinto a None 
if response:
    # verificamos si contiene data 
    if "data" in response:
        data = response["data"]
        if data:
            # verificamos si data contiene "widgets"
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
                            # verificamos si MarketList contiene "data"
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
                                                        #recorremos la lista de marketIdByMarketTemplates
                                                        for market in marketIdByMarketTemplates:
                                                            #verificar que market contenga "marketTemplateId"
                                                            marketTemplateId = market["marketTemplateId"] if "marketTemplateId" in market else None
                                                            #verificar que market contenga "marketIds"
                                                            marketIds = market["marketIds"] if "marketIds" in market else None
                                                            #verificar que marketIds sea de tipo lista
                                                            if marketIds and isinstance(marketIds, list) and marketTemplateId:
                                                                # añadimos el marketTemplateId y market Ids a la lista de apuestas
                                                                apuestas_list[f"{eventId}"][marketTemplateId] = {
                                                                    "marketTemplateId": marketTemplateId, 
                                                                    "marketIds": {}
                                                                    #"marketIds": [ {f"{marketId}":{"marketId":marketId}} for marketId in marketIds ]
                                                                    }
                                                                for marketId in marketIds:
                                                                    apuestas_list[f"{eventId}"][marketTemplateId]["marketIds"][marketId] = {"marketId":marketId}
                                                                    # para cada marketId se le asigna su respectivo maketTemplateId
                                                                    marketTemplateId_for_every_marketId[marketId] = marketTemplateId
                                                                #print(marketTemplateId_for_every_marketId)
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
                                                                            #recorremos la lista de markets
                                                                            for market in markets:
                                                                                #verificamos si market contiene "id"
                                                                                marketId = market["id"] if "id" in market else None
                                                                                #verificamos si market contiene "marketTemplateId"
                                                                                market_marketTemplateId = market["marketTemplateId"] if "marketTemplateId" in market else None
                                                                                #verificamos si market contiene "columnLayout"
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
                                                                                #verificamos si market_marketTemplateId esta en la lista de apuestas_list
                                                                                if market_marketTemplateId in apuestas_list[f"{eventId}"]:
                                                                                    #añadimos la informacion de columnLayout a market_marketTemplateId
                                                                                    apuestas_list[f"{eventId}"][market_marketTemplateId]["columnLayout"] = columnLayout
                                                                                    #verificamos si marketId esta en la lista de apuestas_list
                                                                                    if marketId in apuestas_list[f"{eventId}"][market_marketTemplateId]["marketIds"]:
                                                                                        if accordionGroup:
                                                                                            apuestas_list[f"{eventId}"][market_marketTemplateId]["marketIds"][marketId]["groupKey"] = accordionGroup["groupKey"]
                                                                                        #añadimos la informacion de market a la lista de apuestas
                                                                                        apuestas_list[f"{eventId}"][market_marketTemplateId]["marketIds"][marketId]["columnLayout"] = columnLayout
                                                                                        #añadimos la informacion de accordionGroup a la lista de apuestas si es distino de None
                                                                                        if accordionGroup:
                                                                                            apuestas_list[f"{eventId}"][market_marketTemplateId]["marketIds"][marketId]["tabKey"] = accordionGroup["tabKey"]
                                                                                        #añadimos la informacion de sortOrder a la lista de apuestas si es distino de None
                                                                                        if sortOrder:
                                                                                            apuestas_list[f"{eventId}"][market_marketTemplateId]["marketIds"][marketId]["sortOrder"] = sortOrder
                                                                                        #añadimos la informacion de marketFriendlyName a la lista de apuestas si es distino de None
                                                                                        if marketFriendlyName:
                                                                                            apuestas_list[f"{eventId}"][market_marketTemplateId]["marketIds"][marketId]["marketFriendlyName"] = marketFriendlyName
                                                                                        #añadimos la informacion de label a la lista de apuestas si es distino de None
                                                                                        if label:
                                                                                            apuestas_list[f"{eventId}"][market_marketTemplateId]["marketIds"][marketId]["label"] = label
                                                                                        #añadimos la informacion de status a la lista de apuestas si es distino de None
                                                                                        if status:
                                                                                            apuestas_list[f"{eventId}"][market_marketTemplateId]["marketIds"][marketId]["status"] = status
                                                                                        #añadimos la informacion de lineValue a la lista de apuestas si es distino de None
                                                                                        if lineValue:
                                                                                            apuestas_list[f"{eventId}"][market_marketTemplateId]["marketIds"][marketId]["lineValue"] = lineValue
                                                                                        #añadimos la informacion de lineValueRaw a la lista de apuestas si es distino de None
                                                                                        if lineValueRaw:
                                                                                            apuestas_list[f"{eventId}"][market_marketTemplateId]["marketIds"][marketId]["lineValueRaw"] = lineValueRaw
                                                                            
                                                                            #verificamos si market_data_data contiene "selections"
                                                                            if "selections" in market_data_data:
                                                                                #verificamos si selections es de tipo lista
                                                                                if isinstance(market_data_data["selections"], list):
                                                                                    #recorremos la lista de selections
                                                                                    for selection in market_data_data["selections"]:
                                                                                        #verificamos si market contiene "marketId"
                                                                                        marketId = selection["marketId"] if "marketId" in selection else None
                                                                                        selection_marketTemplateId = marketTemplateId_for_every_marketId[marketId] if marketId in marketTemplateId_for_every_marketId else None
                                                                                        #print(f"marketId: {marketId}, selection_marketTemplateId: {selection_marketTemplateId} ")
                                                                                        if selection_marketTemplateId:
                                                                                            #verificamos si marketId esta en la lista de apuestas_list
                                                                                            if marketId in apuestas_list[f"{eventId}"][selection_marketTemplateId]["marketIds"]:
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
                                                                                                # verificamos si apuestas no esta en la lista de apuestas_list
                                                                                                if "apuestas" not in apuestas_list[f"{eventId}"][selection_marketTemplateId]["marketIds"][marketId]:
                                                                                                    apuestas_list[f"{eventId}"][selection_marketTemplateId]["marketIds"][marketId]["apuestas"] = []
                                                                                                # añadimos la informacion de apuestas a la lista de apuestas
                                                                                                apuestas_list[f"{eventId}"][selection_marketTemplateId]["marketIds"][marketId]["apuestas"].append({
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
                                                                                                
                                                              


#escribir en un archivo json con nombre del ID del evento la informacion de apuestas_list
with open(f'{eventId}.json', 'w') as file:
    json.dump(apuestas_list, file)

# escribir en un archivo json marketTemplateId_for_every_marketId
#with open(f'{eventId}_marketTemplateId_for_every_marketId.json', 'w') as file:
#    json.dump(marketTemplateId_for_every_marketId, file)

#print("Lista de apuestas cargada")
## guardar response en un archivo json
#with open('obtener_apuestas.json', 'w') as file:
#    json.dump(response, file)
#
#print("se guardo la lista de apuestas en obtener_apuestas.json")
