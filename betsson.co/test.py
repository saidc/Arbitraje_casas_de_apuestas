import os 
import json 

# leer un archivo json llamado obtener_apuestas.json
with open("obtener_apuestas.json", "r") as file:
    response = json.load(file)

marketIdByMarketTemplates_list = []

# verificar si response contiene data 
if "data" in response:
    data = response["data"]
    # verificar si data contiene widgets
    if "widgets" in data:
        widgets = data["widgets"]
        # verificar si widgets es de tipo lista
        if isinstance(widgets, list):
            MarketList = None
            # recorrer la lista de widgets
            for widget in widgets:
                # buscar el widget de tipo MarketList
                if "type" in widget and widget["type"] == "MarketList":
                    MarketList = widget
                    break
            # verificar si MarketList es distinto de None
            if MarketList:
                # verificar si MarketList contiene data
                if "data" in MarketList:
                    market_data = MarketList["data"]
                    # verificar si market_data contiene skeleton
                    if "skeleton" in market_data:
                        skeleton = market_data["skeleton"]
                        # verificar si skeleton contiene marketIdByMarketTemplates
                        if "marketIdByMarketTemplates" in skeleton:
                            marketIdByMarketTemplates = skeleton["marketIdByMarketTemplates"]
                            # verificar si markets es de tipo lista
                            if isinstance(marketIdByMarketTemplates, list):
                                # recorrer la lista de marketIdByMarketTemplates
                                for market in marketIdByMarketTemplates:
                                    # verificar si market contiene marketTemplateId
                                    marketTemplateId = market["marketTemplateId"] if "marketTemplateId" in market else None
                                    # verificar si market contiene marketId
                                    marketIds = market["marketIds"] if "marketIds" in market else None

                                    marketIdByMarketTemplates_list.append({
                                        "marketTemplateId": marketTemplateId,
                                        "marketId": marketIds
                                    })

# escribir marketIdByMarketTemplates_list en un archivo llamado marketIdByMarketTemplates_list.json
with open("marketIdByMarketTemplates_list.json", "w") as file:
    json.dump(marketIdByMarketTemplates_list, file)


                                    


