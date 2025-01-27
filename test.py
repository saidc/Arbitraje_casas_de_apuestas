import json 
from config import casas_de_apuestas_path, catalogo_de_deportes_path

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

    # crear una copia de catalogo_de_deportes
    catalogo_de_deportes_cp = catalogo_de_deportes.copy()
    # recorrer el catalogo de deportes actualizado
    deportes_seleccionados = {k:v for k, v in catalogo_de_deportes_cp[name]["Catalogo_de_deportes"].items() if len(lista_de_ids_de_deportes_seleccionados)==0 or (k in lista_de_ids_de_deportes_seleccionados and "regionIds" in v)}
    #print(deportes_seleccionados)

    ds = []

    for k,v in deportes_seleccionados.items():
        for k2,v2 in v["regionIds"].items():
            for k3,v3 in v2["competitionIds"].items():
                ds.append({
                    "categoryId":v["categoryId"],
                    "regionId":v2["regionId"],
                    "competitionId":v3["competitionId"],
                    })
    
    print(ds)
    #deportes_seleccionados = [list(v["regionIds"].values()) for k,v in deportes_seleccionados.items() if "regionIds" in v ]
    #deportes_seleccionados = [list(item["competitionIds"].values()) for sublist in deportes_seleccionados for item in sublist]
    #deportes_seleccionados = [list(item["eventIds"].values()) for sublist in deportes_seleccionados for item in sublist]

a = { 
        "a": {
            "regionIds":{
                "1":{"competitionIds": {
                    "1":"a11",
                    "2":"a12"
                    }
                },
                "2":{"competitionIds": {
                    "1":"a21",
                    "2":"a22"
                    }
                }
            }
        } ,
        "b": {
            "regionIds":{
                "1":{"competitionIds": {
                    "1":"b11",
                    "2":"b12"}
                },
                "2":{"competitionIds": {
                    "1":"b21",
                    "2":"b22"}
                },
            }
        } ,
    }

"""
b = [list(v["regionIds"].values()) for k, v in a.items() if "regionIds" in v]
print(b)
b = [ list(item["competitionIds"].values()) for sublist in b for item in sublist]
print(b)
# unir todas las lista de listas
b = [item for sublist in b for item in sublist]
print(b)
"""
