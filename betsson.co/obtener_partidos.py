from betsson_co.scraping import obtener_apuestas, obtener_partidos
from config import betsson_config_file_path, betsson_partidos_Prematch_file_path
import datetime
import random
import json
import os

# crear una variable que tome el tiempo actual 
# para poder comparar con el tiempo de creacion del archivo partidos_Prematch.json
# y asi saber si se debe actualizar el archivo
time_now = datetime.datetime.now()

# leer archivo config_betsson.json 
with open(betsson_config_file_path, "r") as file:
    config = json.load(file)

Deportes = config["DEPORTES"]
eventPhase = "Prematch"

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

# guardamos la actualizacion del archivo betsson_partidos_Prematch_file_path
with open(betsson_partidos_Prematch_file_path, "w") as file:
    json.dump(betsson_prematch, file)
print("Archivo actualizado: ", betsson_partidos_Prematch_file_path)

# crear una variable de tiempo final para comparar con el tiempo de creacion del archivo partidos_Prematch.json
time_final = datetime.datetime.now()

# calcular el tiempo de ejecucion
time_execution = time_final - time_now
print("Tiempo de ejecucion: ", time_execution)

#categoryId=11
#competitionId=6134 # id 6134 es de la liga "Champions League"
#eventPhase="Prematch"
