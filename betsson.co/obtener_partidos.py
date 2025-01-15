from betsson_co.scraping import obtener_apuestas, obtener_partidos
import random
import json
import os

categoryId=11
competitionId=6134 # id 6134 es de la liga "Champions League"
eventPhase="Prematch"

response = obtener_partidos(categoryId,competitionId,eventPhase)

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

    # verificar si el archivo obtener_partidos.json ya existe, si existe, se añade un codigo aleatorio de 4 caracteres al final del nombre
    file_name = "obtener_partidos.json"
    #if os.path.exists(file_name):
    #    file_name = file_name.split(".")
    #    file_name = file_name[0] + "_" + str(random.randint(1000,9999)) + "." + file_name[1]
    
    # guardar response en un archivo json
    with open(file_name, 'w') as file:
        json.dump(lista_de_partidos, file)
    #if "referenceId" in response:
        