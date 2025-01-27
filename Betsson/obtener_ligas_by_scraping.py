from bs4 import BeautifulSoup
import requests
import pandas as pd
import json

#url = "https://www.betsson.co/apuestas-deportivas/futbol?tab=allLeagues"
url = "https://www.betsson.co/apuestas-deportivas/"

payload = {}
headers = {
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.37'
}

response = requests.request("GET", url, headers=headers, data=payload)

# obtener el estado de la respuesta
print(response.status_code)

sportCatalog_tree = {}

# verificamos que la respuesta sea 200
if response.status_code == 200:
    # pasamos el texto de reaponse a un objeto BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # se busca un script con id="halo-app-state" 
    script = soup.find("script", id="halo-app-state")

    # se obtiene el contenido del script
    script = script.string

    # se obtiene el contenido del script en formato json
    script = json.loads(script)

    # se verifica si el script contiene la key "NGRX_STATE"
    if "NGRX_STATE" in script:
        # se obtiene el valor de la key "NGRX_STATE"
        ngrx_state = script["NGRX_STATE"]

        # se verifica si ngrx_state contiene la key "sportsbook"
        if "sportsbook" in ngrx_state:
            # se obtiene el valor de la key "leagues"
            sportsbook = ngrx_state["sportsbook"]

            # se verifica si sportsbook contiene la key "sportCatalog"
            if "sportCatalog" in sportsbook:
                # se obtiene el valor de la key "sportCatalog"
                sportCatalog = sportsbook["sportCatalog"]

                # se verifica si sportCatalog contiene la key "offering"
                if "offering" in sportCatalog:
                    # se obtiene el valor de la key "offering"
                    offering = sportCatalog["offering"]

                    # se verifica si offering contiene la key "indexByIdSlug"
                    if "indexByIdSlug" in offering:
                        # se obtiene el valor de la key "indexByIdSlug"
                        indexByIdSlug = offering["indexByIdSlug"]
                        
                        # se verifica si indexByIdSlug es de tipo diccionario
                        if isinstance(indexByIdSlug, dict):
                            # se obtiene las keys del diccionario 
                            keys = indexByIdSlug.keys()
                            # se recorre las keys
                            for key in keys:
                                # se obtiene el valor de la key
                                value = indexByIdSlug[key]
                                # hace un split de la key con el caracter "/"
                                key_split = key.split("/")
                                # se hace un split del value con el caracter "/"
                                value_split = value.split("/")
                                # se hace un conteo de los elementos de key_split y value_split y asignamos a sportCatalog_tree , teniendo en cuenta el orden de gerarquia [categoryIds, regionIds, competitionIds, eventId]
                                # Ejemplo: "1/14/16/f-rkgznc0f6ewqfpnw_now2g":"futbol/alemania/alemania-2-bundesliga/greuther-furth-1-fc-kaiserslautern?eventId=f-RKGznC0f6EWQFpNW_nOW2g"  => {"1": { categoryIds:"1", "categoryName": "futbol", "regionIds": { "14": { regionIds: "14", "regionName": "alemania", "competitionIds": { "16": { competitionIds: "16", "competitionName": "alemania-2-bundesliga", "eventIds": { "f-rkgznc0f6ewqfpnw_now2g": { eventId: "f-rkgznc0f6ewqfpnw_now2g", "eventName": "greuther-furth-1-fc-kaiserslautern" } } } } } } }
                                # ten presente que un key y un value puede tener 1 o mas elementos separados por el caracter "/" es decir que el split puede tener uno o mas elementos
                                if len(value_split) >= len(key_split):
                                    for i in range(len(key_split)):
                                        # verifico el nivel de jerarquia [categoryIds, regionIds, competitionIds, eventId]
                                        if i == 0:
                                            # obtengo el key 0
                                            k = key_split[0]
                                            # obtengo el value 0
                                            v = value_split[0]
                                            # verifico si el key no esta en sportCatalog_tree
                                            if k not in sportCatalog_tree:
                                                # añado el key al diccionario
                                                sportCatalog_tree[key_split[i]] = {"categoryId": k, "categoryName": v, "regionIds": {}}
                                        elif i == 1:
                                            # obtengo el key 0
                                            k_0 = key_split[0]
                                            # obtengo el value 0
                                            v_0 = value_split[0]
                                            # obtengo el key 1
                                            k_1 = key_split[1]
                                            # obtengo el value 1
                                            v_1 = value_split[1]
                                            # verifico si el key no esta en sportCatalog_tree
                                            if k_1 not in sportCatalog_tree[k_0]["regionIds"]:
                                                # añado el key al diccionario
                                                sportCatalog_tree[k_0]["regionIds"][k_1] = {"regionId": k_1, "regionName": v_1, "competitionIds": {}}
                                        elif i == 2:
                                            # obtengo el key 0
                                            k_0 = key_split[0]
                                            # obtengo el value 0
                                            v_0 = value_split[0]
                                            # obtengo el key 1
                                            k_1 = key_split[1]
                                            # obtengo el value 1
                                            v_1 = value_split[1]
                                            # obtengo el key 2
                                            k_2 = key_split[2]
                                            # obtengo el value 2
                                            v_2 = value_split[2]
                                            # verifico si el key no esta en sportCatalog_tree
                                            if k_2 not in sportCatalog_tree[k_0]["regionIds"][k_1]["competitionIds"]:
                                                # añado el key al diccionario
                                                sportCatalog_tree[k_0]["regionIds"][k_1]["competitionIds"][k_2] = {"competitionId": k_2, "competitionName": v_2, "eventIds": {}}
                                        elif i == 3:
                                            # obtengo el key 0
                                            k_0 = key_split[0]
                                            # obtengo el value 0
                                            v_0 = value_split[0]
                                            # obtengo el key 1
                                            k_1 = key_split[1]
                                            # obtengo el value 1
                                            v_1 = value_split[1]
                                            # obtengo el key 2
                                            k_2 = key_split[2]
                                            # obtengo el value 2
                                            v_2 = value_split[2]
                                            # obtengo el key 3
                                            k_3 = key_split[3]
                                            # obtengo el value 3
                                            v_3 = value_split[3]
                                            # verifico si el key no esta en sportCatalog_tree
                                            if k_3 not in sportCatalog_tree[k_0]["regionIds"][k_1]["competitionIds"][k_2]["eventIds"]:
                                                # añado el key al diccionario
                                                sportCatalog_tree[k_0]["regionIds"][k_1]["competitionIds"][k_2]["eventIds"][k_3] = {"eventId": k_3, "eventName": v_3}
                            # verifica si sportCatalog_tree no esta vacio
                            if sportCatalog_tree:
                                # guardo el diccionario en un archivo json
                                with open("sportCatalog.json", "w") as file:
                                    json.dump(sportCatalog_tree, file, indent=4)
                                    print("Archivo guardado como sportCatalog.json")        

                                        
                        
                                
