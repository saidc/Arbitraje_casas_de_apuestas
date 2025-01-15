from betsson_co.scraping import obtener_apuestas, obtener_partidos
import random
import json
import os

# leer archivo config_betsson.json 
with open("exploracion_manual\config_betsson.json", "r") as file:
    config = json.load(file)

Deportes = config["DEPORTES"]

# recorrer el listado de Deportes
for key in Deportes.keys():
    print("\n\nDeporte: ", key)
    # obtener el valor del deporte
    deporte = Deportes[key]
    # obtener la lista de Eventos & Ligas
    ligas = deporte["Eventos & Ligas"]
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
                print(name,": ", competitionId)
                if competitionId != -1:
                    prueba_de_obtener_partidos(11, competitionId, "Prematch")

def prueba_de_obtener_partidos():
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

#prueba_de_obtener_partidos()            