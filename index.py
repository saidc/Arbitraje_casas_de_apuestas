from Betsson.Betsson_config import  EVENT_PHASE_PREMATCH
import json 
from config import casas_de_apuestas_path, catalogo_de_deportes_path

# 0) obtener listado de casa de apuestas ( Betsson, Rivalo, wplay, Codere, etc ) y catalogo de deportes
with open(casas_de_apuestas_path, "r") as file:
    casas_de_apuestas = json.load(file)

with open(catalogo_de_deportes_path, "r") as file:
    catalogo_de_deportes = json.load(file)

# 0.1) Recorre listado de casas de apuestas
#      obtener los keys de las casas de apuestas
for casa_de_apuesta_key in casas_de_apuestas.keys():
    # obtener el valor de la casa de apuesta
    casa_de_apuesta_actual = casas_de_apuestas[casa_de_apuesta_key]
    name = casa_de_apuesta_actual["name"]
    # verificar si catalogo_de_deportes tiene el key name
    if name not in catalogo_de_deportes:
        # si no esta en el catalogo de deportes se añade el key name con un diccionario vacio
        catalogo_de_deportes[name] = {"name": name,"Catalogo_de_deportes": {}}

    # obtener catalogo de deportes de la casa de apuesta actual usando name 
    catalogo_deporte_actual = catalogo_de_deportes[name]

    # obtener seleccion_de_deportes de la casa de apuesta actual y verificar si es de tipo lista de lo contrario lista vacia  
    seleccion_de_deportes = casa_de_apuesta_actual["seleccion_de_deportes"] if isinstance(casa_de_apuesta_actual["seleccion_de_deportes"], list) else []
    # crea una lista vacia de ids de deportes seleccionados para almacenar los ids de deportes seleccionados
    lista_de_ids_de_deportes_seleccionados = [v["categoryId"] for v in seleccion_de_deportes] if len(seleccion_de_deportes)>0 else []
    
    # verificar si el nombre de la casa de apuesta es de betsson 
    if casa_de_apuesta_actual["name"] == "Betsson": 
# 1) Solicitud Scraping de deportes para actualizar catalogo de deportes
        scraping_deportes_url = casa_de_apuesta_actual["deportes_url"]
        # creamos variable "resultado" que obtiene el resultado del scraping de la casa de apuesta actual
        actualizacion_de_catalogo_deportes = None
        # colocar un try catch para manejar errores en caso de que no exista el from {name} import {name}_scraping
        try:
            # dado la variable name obtener un import con el valor de la variable name.config ejemplo from Betsson.config import scraping
            exec(f"from {name} import {name}_scraping, actualizar_catalogo_deportes_de_{name}")
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
            #nuevo_catalogo_de_deportes = {k: v for k, v in actualizacion_de_catalogo_deportes.items() if k in lista_de_ids_de_deportes_seleccionados}
            #catalogo_de_deportes[name]["Catalogo_de_deportes"] = {**catalogo_de_deportes[name]["Catalogo_de_deportes"], **nuevo_catalogo_de_deportes}
                
# 3) Recorrer listado de deportes seleccionados
            # recorrer el catalogo de deportes actualizado para filtrar solo los Deportes seleccionados
            deportes_seleccionados = {k:v for k, v in catalogo_de_deportes[name]["Catalogo_de_deportes"].items() if len(lista_de_ids_de_deportes_seleccionados)==0 or (k in lista_de_ids_de_deportes_seleccionados and "regionIds" in v)}            
            
# 4) Generar lista de solicitudes para obtener los partidos que estan dentro de los Deportes y apuestas seleccionados
            lista_de_solicitudes = []
            for k,v in deportes_seleccionados.items():
                for k2,v2 in v["regionIds"].items():
                    for k3,v3 in v2["competitionIds"].items():
                        lista_de_solicitudes.append({
                            "categoryId":v["categoryId"],
                            "regionId":v2["regionId"],
                            "competitionId":v3["competitionId"],
                            "eventPhase": EVENT_PHASE_PREMATCH
                            })
            
# 5) Hacer solicitudes para obtener los partidos que estan dentro de los Deportes y apuestas seleccionados
            # recorrer la lista de solicitudes
            for i, solicitud in enumerate(lista_de_solicitudes):
                categoryId = solicitud["categoryId"]
                regionId = solicitud["regionId"]
                competitionId = solicitud["competitionId"]
                eventPhase = solicitud["eventPhase"]

                lista_de_partidos = None
                try:
                    #lista_de_partidos = obtener_partidos(categoryId, competitionId, eventPhase)
                    exec(f"lista_de_partidos = obtener_partidos_{name}(categoryId,competitionId,eventPhase)")
                except Exception as e:
                    print(f"error en la actualizacion del catalogo de deportes de {name} con el error {e}")
                
                if lista_de_partidos:
                    
                

# guarda el catalogo de deportes actualizado en el archivo catalogo_de_deportes.json
with open(catalogo_de_deportes_path, "w") as file:
    json.dump(catalogo_de_deportes, file, indent=4)
print("se ha actualizado el catalogo de deportes")





# 6) Actualizar Catalogo de Deportes con los partidos que estan dentro de los Deportes y apuestas seleccionados

# 7) Recorrer Catalogo de Deportes 

# 7.1) Buscar partidos que ya se han vencido y eliminarlos ( se eliminan y se guardan en un archivo json de partidos ya jugados )

# 7.2) Generar lista de solicitudes para obtener apuestas de los partidos que estan dentro de los Deportes y apuestas seleccionados

# 8) Hacer solicitudes para obtener las apuestas de los partidos que estan dentro de los Deportes y apuestas seleccionados

# 9) Actualizar Catalogo de Deportes con apuestas de Deportes y apuestas seleccionados

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
