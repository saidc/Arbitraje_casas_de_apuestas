from config import betsson_partidos_Prematch_file_path

import json 

# obtenemos el archivo json betsson_partidos_Prematch_file_path
with open(betsson_partidos_Prematch_file_path, "r") as file:
    betsson_prematch = json.load(file)


# obtener el archivo json exploracion_manual\marketTemplateIds.json 
with open("exploracion_manual\marketTemplateIds.json", "r") as file:
    marketTemplateIds = json.load(file)

# obtener de betsson_prematch los keys 
deportes_keys = betsson_prematch.keys()

# recorrer los keys de betsson_prematch
for deporte_key in deportes_keys:
    # obtener el valor de la key
    deporte = betsson_prematch[deporte_key]
    # obtener las ligas de la key
    ligas = deporte.keys()
    # recorrer las ligas
    for liga in ligas:
        # obtener el valor de la liga
        liga_value = deporte[liga]
        # obtener los partidos de la liga como keys
        partidos = liga_value.keys()
        # recorrer los partidos
        for partido in partidos:
            # obtener el valor del partido
            partido_value = liga_value[partido]
            # verificar el partido contiene apuestas
            if "apuestas" in partido_value:
                apuestas = partido_value["apuestas"]
                # obtener los tipos de apuestas como keys
                tipos_de_apuestas = apuestas.keys()
                # recorrer las apuestas
                for tipo_de_apuesta in tipos_de_apuestas:
                    # verificar si el tipo de apuesta contiene marketIds
                    if "marketIds" in apuestas[tipo_de_apuesta]:
                        marketIds = apuestas[tipo_de_apuesta]["marketIds"]
                        # obtener los marketIds como keys
                        marketIds_keys = marketIds.keys()
                        # vericicar si el tipo de apuesta contiene marketTemplateId
                        tipo_de_apuesta_marketTemplateId = apuestas[tipo_de_apuesta]["marketTemplateId"] if "marketTemplateId" in apuestas[tipo_de_apuesta] else None
                        if tipo_de_apuesta_marketTemplateId:
                            # recorrer los marketIds
                            for marketId in marketIds_keys:
                                # obtener el valor del marketId
                                marketId_value = marketIds[marketId]
                                # verificar si el marketId contiene marketFriendlyName
                                if "marketFriendlyName" in marketId_value:
                                    marketFriendlyName = marketId_value["marketFriendlyName"]
                                    # convertir el texto de marketFriendlyName a texto normal ejemplo "Primer tiempo 1X2 + Ambos equipos anotar\u00e1n" a "Primer tiempo 1X2 + Ambos equipos anotarán"
                                    #marketFriendlyName = marketFriendlyName.encode().decode("unicode_escape")
                                    if tipo_de_apuesta_marketTemplateId not in marketTemplateIds:
                                        # si no existe el tipo_de_apuesta_marketTemplateId en marketTemplateIds, se crea
                                        marketTemplateIds[tipo_de_apuesta_marketTemplateId] = []
                                    # añadir marketFriendlyName a marketTemplateIds con el valor de tipo_de_apuesta_marketTemplateId
                                    marketTemplateIds[tipo_de_apuesta_marketTemplateId].append(marketFriendlyName)

# recorrer marketTemplateIds verificando que no existan duplicados
for marketTemplateId in marketTemplateIds:
    marketTemplateIds[marketTemplateId] = list(set(marketTemplateIds[marketTemplateId]))

# guardar marketTemplateIds en exploracion_manual\marketTemplateIds.json
with open("exploracion_manual\marketTemplateIds.json", "w") as file:
    json.dump(marketTemplateIds, file, indent=4)

