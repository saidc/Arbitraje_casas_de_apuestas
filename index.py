from config import casas_de_apuestas_path, catalogo_de_deportes_path, partidos_jugados_path
from datetime import timedelta
import datetime
import json 
import os
import concurrent.futures


TIEMPO_DE_ACTUALIZACION = 30 # minutos
FORMATO_DE_FECHA = "%Y-%m-%dT%H:%M:%SZ"

# 0) obtener listado de casa de apuestas ( Betsson, Rivalo, wplay, Codere, etc ) y catalogo de deportes
with open(casas_de_apuestas_path, "r") as file:
    casas_de_apuestas = json.load(file)

# verificar si el archivo catalogo_de_deportes.json existe
if not os.path.exists(catalogo_de_deportes_path):
    # si no existe el archivo se crea con un diccionario vacio
    with open(catalogo_de_deportes_path, "w") as file:
        json.dump({}, file, indent=4)

with open(catalogo_de_deportes_path, "r") as file:
    catalogo_de_deportes = json.load(file)

# 0.1) Recorre listado de casas de apuestas
#      obtener los keys de las casas de apuestas
for casa_de_apuesta_key in casas_de_apuestas.keys():
    # crear una variable de tiempo de inicio para saber cuanto tiempo se demora en actualizar la casa de apuesta actual
    casa_de_apuesta_start_time = datetime.datetime.now()

    # obtener el valor de la casa de apuesta
    casa_de_apuesta_actual = casas_de_apuestas[casa_de_apuesta_key]
    # obtener el nombre de la casa de apuesta
    name = casa_de_apuesta_actual["name"]
    # verificar si catalogo_de_deportes tiene el key name
    if name not in catalogo_de_deportes:
        # si no esta en el catalogo de deportes se añade el key name con un diccionario vacio
        catalogo_de_deportes[name] = {"name": name,"Catalogo_de_deportes": {}}

    # obtener seleccion_de_deportes de la casa de apuesta actual y verificar si es de tipo lista de lo contrario lista vacia  
    seleccion_de_deportes = casa_de_apuesta_actual["seleccion_de_deportes"] if isinstance(casa_de_apuesta_actual["seleccion_de_deportes"], list) else []
    # crea una lista vacia de ids de deportes seleccionados para almacenar los ids de deportes seleccionados
    lista_de_ids_de_deportes_seleccionados = [v["categoryId"] for v in seleccion_de_deportes] if len(seleccion_de_deportes)>0 else []
    
    # verificar si el nombre de la casa de apuesta es de betsson 
    if name == "Betsson": 
# 1) Solicitud Scraping de deportes para actualizar catalogo de deportes
        scraping_deportes_url = casa_de_apuesta_actual["deportes_url"]
        # creamos variable "resultado" que obtiene el resultado del scraping de la casa de apuesta actual
        actualizacion_de_catalogo_deportes = None
        # colocar un try catch para manejar errores en caso de que no exista el from {name} import {name}_scraping
        try:
            # dado la variable name obtener un import con el valor de la variable name.config ejemplo from Betsson.config import scraping
            exec(f"from {name} import {name}_EVENT_PHASE_PREMATCH, {name}_scraping, actualizar_catalogo_deportes_de_{name}, obtener_partidos_{name}, obtener_apuestas_{name}, request_obtener_partidos_{name}, procesar_respuesta_obtener_partidos_{name}, request_obtener_apuestas_{name}, procesar_request_obtener_apuestas_{name}")
            # ahora ejecuta la funcion importada con una de entrada, y guarda el resultado de la ejecucion de la funcion 
            exec(f"actualizacion_de_catalogo_deportes = {name}_scraping(scraping_deportes_url)")
        except Exception as e:
            print(f"error en el scraping de {name} con el error {e}")

# 2) Actualizar Catalogo de deporte con deportes seleccionados
        # verifica si resultado es diferente de None
        if actualizacion_de_catalogo_deportes:
            # crea una variable new_catalogo_de_deportes que obtiene el resultado de la actualizacion del catalogo de deportes de la casa de apuesta actual
            new_catalogo_de_deportes = None
            try:
                # ahora ejecuta la funcion importada con una de entrada, y guarda el resultado de la ejecucion de la funcion
                exec(f"new_catalogo_de_deportes = actualizar_catalogo_deportes_de_{name}(lista_de_ids_de_deportes_seleccionados, catalogo_de_deportes, actualizacion_de_catalogo_deportes)")
            except Exception as e:
                print(f"error en la actualizacion del catalogo de deportes de {name} con el error {e}")
            
            # verifica si new_catalogo_de_deportes es diferente de None y si es diferente actualiza el catalogo de deportes con el nuevo catalogo de deportes
            catalogo_de_deportes = new_catalogo_de_deportes if new_catalogo_de_deportes != None else catalogo_de_deportes
            
            # actualiza el catalogo de deportes con key name y se le asigna el valor de resultado del scraping con los ids de deportes seleccionados, sin borrar los elementos que ya estan en el catalogo de deportes
            # nuevo_catalogo_de_deportes = {k: v for k, v in actualizacion_de_catalogo_deportes.items() if k in lista_de_ids_de_deportes_seleccionados}
            # catalogo_de_deportes[name]["Catalogo_de_deportes"] = {**catalogo_de_deportes[name]["Catalogo_de_deportes"], **nuevo_catalogo_de_deportes}
                
# 3) Recorrer listado de deportes seleccionados
            # recorrer el catalogo de deportes actualizado para filtrar solo los Deportes seleccionados
            deportes_seleccionados = {k:v for k, v in catalogo_de_deportes[name]["Catalogo_de_deportes"].items() if len(lista_de_ids_de_deportes_seleccionados)==0 or (k in lista_de_ids_de_deportes_seleccionados and "regionIds" in v)}            
            
# 4) Generar lista de solicitudes para obtener los partidos que estan dentro de los Deportes y apuestas seleccionados
            # crear una lista vacia para guardar las solicitudes de los partidos de la casa de apuesta actual
            lista_de_solicitudes = []
            # crear una lista vacia para guardar los partidos que se van a revisar si ya se han vencido o requieren actualizacion
            partidos_por_revisar = []
            # se recorre los deportes seleccionados
            for k,v in deportes_seleccionados.items():
                # se recorre las regiones de los deportes seleccionados
                for k2,v2 in v["regionIds"].items():
                    # se recorre las competencias de las regiones de los deportes seleccionados
                    for k3,v3 in v2["competitionIds"].items():
                        lista_de_solicitudes.append({
                            "categoryId":v["categoryId"],
                            "regionId":v2["regionId"],
                            "competitionId":v3["competitionId"]
                        })
                        for k4,v4 in v3["eventIds"].items():
                            if "startDate" in v4 and "eventId" in v4:
                                # guardar en una lista los partidos que se van a revisar si ya se han vencido
                                partidos_por_revisar.append({
                                    "categoryId":v["categoryId"],
                                    "regionId":v2["regionId"],
                                    "competitionId":v3["competitionId"],
                                    "eventId":v4["eventId"],
                                    "startDate":v4["startDate"]
                                })

            
# 5) Hacer solicitudes para obtener los partidos que estan dentro de los Deportes y apuestas seleccionados
            # crear una lista vacia para guardar los partidos que se van a consultar las apuestas
            lista_de_partidos_por_consultar_apuestas = []

            # crearemos un listado que obtiene las respuestas de las solicitudes de los partidos de la casa de apuesta actual
            lista_de_request_de_partidos = []
            MAX_THREADS = 4
            # Usar ThreadPoolExecutor para paralelizar las solicitudes
            with concurrent.futures.ThreadPoolExecutor(MAX_THREADS) as executor:
                # crear un diccionario vacio para guardar los futures de las solicitudes de los partidos
                futures = {}
                # recorrer la lista de solicitudes para realizar las solicitudes de los partidos usando hilos para agilizar el proceso 
                for i, solicitud in enumerate(lista_de_solicitudes):
                    categoryId = solicitud["categoryId"]
                    regionId = solicitud["regionId"]
                    competitionId = solicitud["competitionId"]
                    # inicializar future en None para verificar si se ejecuto correctamente la solicitud
                    future = None
                    try:
                        # ahora ejecuta la funcion request_obtener_partidos_{name} usando hilos para agilizar el proceso
                        exec(f"future = executor.submit(request_obtener_partidos_{name}, categoryId, regionId, competitionId, {name}_EVENT_PHASE_PREMATCH, i, len(lista_de_solicitudes))")                    
                    except Exception as e:
                        print(f"error al hacer la solicitud {i} de la competencia {competitionId} de la region {regionId} del deporte {categoryId} de la casa de apuesta {name} con el error {e}")
                    # verificar si future es diferente de None, indicando que se ejecuto correctamente la solicitud y se puede guardar en un diccionario de solicitudes futuras
                    if future:
                        # guardar el future en un diccionario con el indice de la solicitud
                        futures[future] = i
                
                # recorrer los futures para obtener los resultados de las solicitudes de los partidos de la casa de apuesta actual
                for future in concurrent.futures.as_completed(futures):
                    # obtener el resultado de la solicitud
                    result = future.result()
                    # verificar si result es diferente de None
                    if result:
                        # agregar el resultado a la lista de request de partidos, para luego procesar la respuesta
                        lista_de_request_de_partidos.append(result)
            
# 6) Actualizar Catalogo de Deportes con los partidos que estan dentro de los Deportes y apuestas seleccionados
                contador = 0
                # recoremos la lista de request de partidos para obtener las respuestas y realizar el procesado de la respuesta
                for i, respuesta_json in enumerate(lista_de_request_de_partidos):
                    print(i)
                    categoryId = respuesta_json["categoryId"]
                    regionId = respuesta_json["regionId"]
                    competitionId = respuesta_json["competitionId"]
                    eventPhase = respuesta_json["eventPhase"]
                    response = respuesta_json["response"]
                    
                    # crea una variable lista_de_partidos que obtiene el resultado de la solicitud de los partidos de la casa de apuesta actual
                    lista_de_partidos = None 
                    try:
                        # ahora ejecuta la funcion importada procesar_respuesta_obtener_partidos_{name} con la respuesta de los partidos
                        exec(f"lista_de_partidos = procesar_respuesta_obtener_partidos_{name}(response)")
                    except Exception as e:
                        print(f"error en la actualizacion del catalogo de deportes de {name} con el error {e}")

                    if lista_de_partidos:
                        # verificar que eventIds exista en el catalogo de deportes
                        catalogo_de_deportes[name]["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"] = catalogo_de_deportes[name]["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"] if "eventIds" in catalogo_de_deportes[name]["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId] else {}
                        # obtener los keys de los partidos obtenidos en eventIds del catalogo de deportes
                        keys_eventIds = catalogo_de_deportes[name]["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"].keys()
                        # obtener los keys del listado de partidos obtenidos
                        keys_lista_de_partidos = lista_de_partidos.keys()
                        # actualizar el listado de partidos obtenidos solo con los que no aparezcan en el catalogo de deportes
                        lista_de_partidos = {k:v for k,v in lista_de_partidos.items() if k not in keys_eventIds}
                        # actualiza el catalogo de deportes con los partidos obtenidos
                        catalogo_de_deportes[name]["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"].update(lista_de_partidos)
                    
# 7) Recorrer Catalogo de Deportes 
# 7.1) Generar lista de solicitudes para obtener apuestas de los partidos que estan dentro de los Deportes y apuestas seleccionados
                        # guardar en una lista los partidos que se van a consultar las apuestas
                        for key_partido in lista_de_partidos.keys():
                            lista_de_partidos_por_consultar_apuestas.append({
                                "categoryId":categoryId,
                                "regionId":regionId,
                                "competitionId":competitionId,
                                "eventId":key_partido,
                                "startDate":lista_de_partidos[key_partido]["startDate"] if "startDate" in lista_de_partidos[key_partido] else None
                            })

                        # recorrer el catalogo de deportes para verificar si hay partidos que no han sido actualizados en mas del TIEMPO_DE_ACTUALIZACION en minutos
                        for eventId in keys_eventIds:
                            # obtener el valor de eventId en el catalogo de deportes de la casa de apuesta actual
                            eventId_value = catalogo_de_deportes[name]["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]
                            # obtener el valor de startDate en eventId_value si existe, para verificar si ya se vencio el partido
                            startDate = eventId_value["startDate"] if "startDate" in eventId_value else None
                            # verificar que no este vencido 
                            if startDate:
                                # convertir startDate a datetime con formato "%Y-%m-%dT%H:%M:%SZ"
                                startDate = datetime.datetime.strptime(startDate, FORMATO_DE_FECHA)
                                # verificar si startDate es mayor a la fecha actual porque si es menor ya se vencio y no se debe consultar apuestas, sino que se debe eliminar del catalogo de deportes y guardar en el archivo partidos_jugados.json
                                if startDate > datetime.datetime.now():
                                    # mirar cuando fue la ultima actualizacion del eventId
                                    if "lastUpdate" in eventId_value:
                                        # obtener el valor de lastUpdate
                                        lastUpdate = eventId_value["lastUpdate"]
                                        # convertir lastUpdate a datetime con formato "%Y-%m-%dT%H:%M:%SZ"
                                        lastUpdate = datetime.datetime.strptime(lastUpdate, FORMATO_DE_FECHA)
                                        # verificar si lastUpdate es mayor al TIEMPO_DE_ACTUALIZACION en minutos de la fecha actual para añadir a la lista de partidos por consultar o actualizar apuestas
                                        if lastUpdate < datetime.datetime.now() - timedelta(minutes=TIEMPO_DE_ACTUALIZACION):
                                            # verificar si eventId no esta en la lista de partidos por consultar apuestas para evitar consultas duplicadas
                                            existe_eventId = True in [True for partido in lista_de_partidos_por_consultar_apuestas if partido["eventId"]==eventId]
                                            # si no esta en la lista de partidos por consultar apuestas se añade
                                            if not existe_eventId:
                                                # si no esta en la lista de partidos por consultar apuestas se añade
                                                lista_de_partidos_por_consultar_apuestas.append({
                                                    "categoryId":categoryId,
                                                    "regionId":regionId,
                                                    "competitionId":competitionId,
                                                    "eventId":eventId,
                                                    "startDate":eventId_value["startDate"] if "startDate" in eventId_value else None
                                                })
                            
                    else:
                        # si no se obtiene la lista de partidos se aumenta el contador para saber cuantos partidos no se obtuvieron
                        contador += 1
                    # imprimir el numero de solicitud actual y el total de solicitudes para saber en que solicitud se encuentra
                    print(f"Solicitud {i+1-contador}/{len(lista_de_request_de_partidos)-contador} ")
                     
                # verificar si el archivo partidos_jugados.json existe
                if not os.path.exists(partidos_jugados_path):
                    # si no existe el archivo se crea con un diccionario vacio
                    with open(partidos_jugados_path, "w") as file:
                        json.dump({}, file, indent=4)
                        
                # leer el archivo partidos_jugados.json
                with open(partidos_jugados_path, "r") as file:
                    partidos_jugados_file = json.load(file)
            
# 7.2) Buscar partidos que ya se han vencido y eliminarlos ( se eliminan y se guardan en un archivo json de partidos ya jugados )
                for i, partido in enumerate(partidos_por_revisar):
                    categoryId = partido["categoryId"]
                    regionId = partido["regionId"]
                    competitionId = partido["competitionId"]
                    eventId = partido["eventId"]
                    startDate = partido["startDate"]
                    # convertir startDate a datetime con formato "2025-01-31T17:30:00Z"
                    startDate = datetime.datetime.strptime(startDate, FORMATO_DE_FECHA)
                    # verificar si startDate es menor a la fecha actual para eliminar el partido del catalogo de deportes y guardarlo en el archivo partidos_jugados.json
                    if startDate < datetime.datetime.now():
                        # verificar si el key name existe en el archivo partidos_jugados.json
                        if name not in partidos_jugados_file:
                            # si no existe el key name se crea con un diccionario vacio
                            partidos_jugados_file[name] = {}
                        # verificar si el key categoryId existe en el key name del archivo partidos_jugados.json
                        if categoryId not in partidos_jugados_file[name]:
                            # si no existe el key categoryId se crea con un diccionario vacio
                            partidos_jugados_file[name][categoryId] = {}
                        # verificar si el key regionId existe en el key categoryId del archivo
                        if regionId not in partidos_jugados_file[name][categoryId]:
                            # si no existe el key regionId se crea con un diccionario vacio
                            partidos_jugados_file[name][categoryId][regionId] = {}
                        # verificar si el key competitionId existe en el key regionId del archivo
                        if competitionId not in partidos_jugados_file[name][categoryId][regionId]:
                            # si no existe el key competitionId se crea con un diccionario vacio
                            partidos_jugados_file[name][categoryId][regionId][competitionId] = {}
                        # verificar si el key eventId existe en el key competitionId del archivo
                        if eventId not in partidos_jugados_file[name][categoryId][regionId][competitionId]:
                            # si no existe el key eventId se crea con un diccionario vacio
                            partidos_jugados_file[name][categoryId][regionId][competitionId][eventId] = {}
                        
                        # guardar el partido en el archivo partidos_jugados.json
                        partidos_jugados_file[name][categoryId][regionId][competitionId][eventId] = catalogo_de_deportes[name]["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]

                        # eliminar el partido del catalogo de deportes
                        del catalogo_de_deportes[name]["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]
                        # imprimir el partido eliminado para saber que se ha eliminado correctamente
                        print(f"Partido {i+1}/{len(partidos_por_revisar)} eliminado")

                # guardar el archivo partidos_jugados.json
                with open(partidos_jugados_path, "w") as file:
                    json.dump(partidos_jugados_file, file, indent=4)
                print("se han eliminado los partidos que ya se han vencido")

# 8) Hacer solicitudes para obtener las apuestas de los partidos que estan dentro de los Deportes y apuestas seleccionados
                lista_de_request_de_apuestas = []
                # Usar ThreadPoolExecutor para paralelizar las solicitudes
                with concurrent.futures.ThreadPoolExecutor(MAX_THREADS) as executor2:
                    # crear un diccionario vacio para guardar los futures de las solicitudes de las apuestas
                    futures = {}
                    # recorrer la lista de partidos por consultar apuestas
                    for i, partido in enumerate(lista_de_partidos_por_consultar_apuestas):
                        
                        categoryId = partido["categoryId"]
                        regionId = partido["regionId"]
                        competitionId = partido["competitionId"]
                        eventId = partido["eventId"]
                        startDate = partido["startDate"]
                        # inicializar future en None para verificar si se ejecuto correctamente la solicitud
                        future = None
                        try:
                            # ahora ejecuta la funcion obtener_apuestas_{name} usando hilos para agilizar el proceso
                            exec(f"future = executor2.submit(request_obtener_apuestas_{name}, catalogo_de_deportes[name], categoryId, regionId, competitionId, eventId, i, len(lista_de_partidos_por_consultar_apuestas))")
                        except Exception as e:
                            print(f"error al hacer la solicitud {i} de las apuestas del partido {eventId} de la competencia {competitionId} de la region {regionId} del deporte {categoryId} de la casa de apuesta {name} con el error {e}")
                        # verificar si future es diferente de None, indicando que se ejecuto correctamente la solicitud y se puede guardar en un diccionario de solicitudes futuras
                        if future:
                            # guardar el future en un diccionario con el indice de la solicitud
                            futures[future] = i
                    # recorrer los futures para obtener los resultados de las solicitudes de las apuestas de los partidos de la casa de apuesta actual
                    for future in concurrent.futures.as_completed(futures):
                        # obtener el resultado de la solicitud
                        result = future.result()
                        # verificar si result es diferente de None
                        if result:
                            # agregar el resultado a la lista de request de apuestas, para luego procesar la respuesta
                            lista_de_request_de_apuestas.append(result)
                
# 9) Actualizar Catalogo de Deportes con apuestas de Deportes y apuestas seleccionados
                contador2 = 0
                # recorrer la lista de request de apuestas para obtener las respuestas y realizar el procesado de la respuesta
                for i, respuesta_json in enumerate(lista_de_request_de_apuestas):
                    print(i)
                    # obtener el catalogo de deportes de la casa de apuesta actual
                    Betsson_catalog = catalogo_de_deportes[name]
                    categoryId = respuesta_json["categoryId"]
                    regionId = respuesta_json["regionId"]
                    competitionId = respuesta_json["competitionId"]
                    eventId = respuesta_json["eventId"]
                    response = respuesta_json["response"]
                    # crea una variable lista_de_apuestas que obtiene el resultado de la solicitud de las apuestas de la casa de apuesta actual
                    lista_de_apuestas = None
                    try:
                        # ahora ejecuta la funcion importada procesar_request_obtener_apuestas_{name} con la respuesta de las apuestas
                        exec(f"lista_de_apuestas = procesar_request_obtener_apuestas_{name}(Betsson_catalog, categoryId, regionId, competitionId, eventId, response)")
                    except Exception as e:
                        print(f"error en la actualizacion del catalogo de deportes de {name} con el error {e}")
                    
                    # verificar si lista_de_apuestas es diferente de None
                    if lista_de_apuestas:
                        # se actualiza el catalogo de deportes con las apuestas obtenidas
                        catalogo_de_deportes[name].update(lista_de_apuestas)
                    else:
                        # si no se obtiene la lista de apuestas se aumenta el contador para saber cuantas apuestas no se obtuvieron
                        contador2 += 1
                    print(f"Solicitud {i+1-contador2}/{len(lista_de_partidos_por_consultar_apuestas)-contador2} ")

                print("se han actualizado las apuestas de los partidos ✅")
    # crear una variable de tiempo final para saber cuanto tiempo se demoro en actualizar la casa de apuesta actual
    casa_de_apuesta_end_time = datetime.datetime.now()
    # imprimir el tiempo que se demoro en actualizar la casa de apuesta actual
    print(f"se ha demorado {casa_de_apuesta_end_time - casa_de_apuesta_start_time} en actualizar la casa de apuesta {name}")

# guarda el catalogo de deportes actualizado en el archivo catalogo_de_deportes.json
with open(catalogo_de_deportes_path, "w") as file:
    json.dump(catalogo_de_deportes, file, indent=4)

print("se ha actualizado el catalogo de deportes")


# Despues de finalizado ciclo de recorrer el listado de casa de apuestas

# 10) Generar listado de partidos, de cada casa de apuestas, que tienen apuestas en los proximos 3 dias, y mayor a 1 hora del tiempo actual

# 11) Buscar segun los nombres de los partidos, los partidos que coinciden en las diferentes casas de apuestas, para identificar los partidos en comun entre las casas de apuestas
# Nota: tener una lista final con las coincidencias de los partidos en comun entre las casas de apuestas

# 12) Generar listado de apuestas que coinciden en los partidos en comun entre las casas de apuestas
# Nota: tener una lista final con las coincidencias de las apuestas en comun entre las casas de apuestas

# 13) Generar el calculo de oportunidades de arbitraje entre las apuestas que coinciden en los partidos en comun entre las casas de apuestas
# Nota: tener una lista final con las oportunidades de arbitraje entre las apuestas que coinciden en los partidos en comun entre las casas de apuestas
# Nota: tener en cada item de la lista el nombre de de cada casa de apuesta, el nombre del partido, el tipo de apuesta, el valor de ganancia de apuesta, el valor de la apuesta para cada casa de apuesta, el valor de la oportunidad de arbitraje para cada casa de apuesta y en total
# 13.1) Generar un grupo de apuestas que coinciden en los partidos en comun entre las casas de apuestas
# Nota: guardar en cada item de la lista un numero de grupo para identificar las apuestas que coinciden en los partidos en comun entre las casas de apuestas

# 14) Guardar en un archivo json las oportunidades de arbitraje entre las apuestas que coinciden en los partidos en comun entre las casas de apuestas

# 15) Enviar notificacion al bot de telegram con las oportunidades de arbitraje entre las apuestas que coinciden en los partidos en comun entre las casas de apuestas
# Nota: tener en cada item de la lista el nombre de de cada casa de apuesta, el nombre del partido, el tipo de apuesta, el valor de ganancia de apuesta, el valor de la apuesta para cada casa de apuesta, el valor de la oportunidad de arbitraje para cada casa de apuesta

# 16) reiniciar el proceso de actualizacion de los valores de apuesta cada 5 minutos, para revisar si hay cambios en los valores de las apuestas y generar nuevas oportunidades de arbitraje o eliminen las oportunidades de arbitraje existentes
