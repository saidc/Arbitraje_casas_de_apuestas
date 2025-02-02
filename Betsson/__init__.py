
from Betsson.Betsson_config import BETSSON_HEADERS, BETSSON_HEADERS_SCRAPING_DEPORTES, Betsson
from bs4 import BeautifulSoup
from config import PROXIES
import itertools
import datetime
import requests
import time 
import json
import threading

global proxy_cycle, proxies_usados, VALOR_MAXIMO_DE_USO, VALOR_MAXIMO_DE_TIMEOUT 

Betsson_EVENT_PHASE_PREMATCH = "Prematch"
FORMATO_FECHA_ACTUAL = "%Y-%m-%dT%H:%M:%SZ"

VALOR_MAXIMO_DE_USO = 100
VALOR_MAXIMO_DE_TIMEOUT = 300 # 5 MINUTOS

# Crear un iterador circular para rotar proxies
proxy_cycle = PROXIES.copy()
# variable para seguimiento del uso de proxys
proxies_usados = {}

def corrimiento_izquierda(lista):
    if len(lista) > 1:
        return lista[1:] + [lista[0]]
    return lista  # Si la lista tiene 0 o 1 elementos, no hay cambio

def format_proxy(proxy):
    """Convierte una cadena IP:PORT:USER:PASSWORD en un diccionario de proxies"""
    if proxy is None:
        return None
    if proxy == "LOCAL":
        return "LOCAL"

    # Separar la cadena en sus componentes IP, PORT, USER, PASSWORD usando ":" como separador
    ip, port, user, password = proxy.split(":")
    # Formatear la cadena en el formato correcto para proxies
    proxy_url = f"http://{user}:{password}@{ip}:{port}"
    # Devolver el diccionario de proxies
    return {"http": proxy_url, "https": proxy_url}

def get_next_proxy():
    """Devuelve el siguiente proxy de la lista."""
    global proxy_cycle, proxies_usados

    for proxy in proxy_cycle:
        if proxy in proxies_usados:
            if "available" in proxies_usados[proxy]:
                if proxies_usados[proxy]["available"]:
                    return format_proxy(proxy) , proxy
        else:
            proxies_usados[proxy] = {"available": True, "lastupdate": time.time(), "uses_count": 0, "max_timeout": time.time() + VALOR_MAXIMO_DE_TIMEOUT, "1_timeout": time.time() + 1}
            return format_proxy(proxy) , proxy
    return None,None

def actualizar_proxie_usado(proxy_id):
    global proxies_usados, VALOR_MAXIMO_DE_USO, VALOR_MAXIMO_DE_TIMEOUT 
    
    # verificar si el proxi usado actualmente esta en los proxyes usados
    if proxy_id not in proxies_usados:
        proxies_usados[proxy_id] = {"available": True, "lastupdate": time.time(), "uses_count": 0, "max_timeout": time.time() + VALOR_MAXIMO_DE_TIMEOUT, "1_timeout": time.time() + 1}
    
    # asignar la fecha de ultimo uso del proxy
    proxies_usados[proxy_id]["lastupdate"] = time.time()
    # verifica si el contador de usos del proxy existe y se aumenta en 1, de lo contrario se crea y se le asigna el valor de 1 
    proxies_usados[proxy_id]["uses_count"] = 1 if "uses_count" not in proxies_usados[proxy_id] else proxies_usados[proxy_id]["uses_count"] + 1
    
    # verifica si max_timeout no existe, se crea con un valor de VALOR_MAXIMO_DE_TIMEOUT a futuro del tiempo actual, de lo contrario se deja el valor actual 
    proxies_usados[proxy_id]["max_timeout"] = time.time() + VALOR_MAXIMO_DE_TIMEOUT if "max_timeout" not in proxies_usados[proxy_id] else proxies_usados[proxy_id]["max_timeout"]
    # verificar si 1_timeout no existe para asignarle 1 segundo mas adelante, de lo contrario le deja el mismo valor
    proxies_usados[proxy_id]["1_timeout"]   = time.time() + 1   if "1_timeout" not in proxies_usados[proxy_id] else proxies_usados[proxy_id]["1_timeout"]
    # verifica si el proxy esta diponible viendo si tiene mas de VALOR_MAXIMO_DE_USO usos en menos de 5 minutos
    proxies_usados[proxy_id]["available"] = True if "available" not in proxies_usados[proxy_id] else not( proxies_usados[proxy_id]["uses_count"] >= VALOR_MAXIMO_DE_USO and proxies_usados[proxy_id]["max_timeout"] - time.time() > 0 )
    # verifica si max_timeout ha terminado para 
    if proxies_usados[proxy_id]["max_timeout"] - time.time() <= 0:
        # asigno a max_timeout el valor a futuro de VALOR_MAXIMO_DE_TIMEOUT
        proxies_usados[proxy_id]["max_timeout"] = time.time() + VALOR_MAXIMO_DE_TIMEOUT
        # reinicio el numero de usos a 1
        proxies_usados[proxy_id]["uses_count"] = 1
        # y colocamos el proxi como disponible actualmente 
        proxies_usados[proxy_id]["available"] = True

def temporizador_de_avilitador_de_proxy(proxy_id):
    global proxies_usados, VALOR_MAXIMO_DE_USO, VALOR_MAXIMO_DE_TIMEOUT 
    print(f"el proxy {proxy_id} Esta bloqueado y entra en periodo de espera")
    
    # asignar la fecha de ultimo uso del proxy
    proxies_usados[proxy_id]["lastupdate"] = time.time()
    # indicamos el tiempo que debe de esperar el proxy para poder volver activarse
    proxies_usados[proxy_id]["max_timeout"] = time.time() + VALOR_MAXIMO_DE_TIMEOUT if "max_timeout" not in proxies_usados[proxy_id] else proxies_usados[proxy_id]["max_timeout"]
    # proxies_usados[proxy_id]["available"] 
    # asignar la fecha de ultimo uso del proxy 
    # proxies_usados[proxy_id]["lastupdate"] 
    while proxies_usados[proxy_id]["max_timeout"] - time.time() > 0:
        # hacer que se espere VALOR_MAXIMO_DE_TIMEOUT en el hilo actual
        time.sleep( VALOR_MAXIMO_DE_TIMEOUT )
    # se habilita el proxi de nuevo
    proxies_usados[proxy_id]["available"] = True
    print(f"el proxy {proxy_id} puede usarse nuevamente")

def is_traffic_error(response_text):
    """Verifica si la respuesta contiene un mensaje de error de tráfico."""
    soup = BeautifulSoup(response_text, "html.parser")
    
    # Buscar "request could not be satisfied" en h2
    error_tags = soup.find_all("h2")
    for tag in error_tags:
        if "request could not be satisfied" in tag.text.lower():
            return True
    
    # Buscar "too much traffic" en el cuerpo del texto
    if "too much traffic" in soup.text.lower():
        return True
    
    return False

def make_get_request(url, headers, payload, max_retries=10, wait_time=20, min_interval=0.1):
    """
    Realiza una solicitud GET con reintentos en caso de errores por tráfico.
    :param url: URL de la solicitud
    :param headers: Headers de la solicitud
    :param payload: Datos de la solicitud
    :param max_retries: Número máximo de intentos en caso de error
    :param wait_time: Tiempo de espera entre intentos en segundos (incremental)
    :param min_interval: Tiempo mínimo de espera entre solicitudes para evitar bloqueos
    :return: Respuesta en formato JSON si tiene éxito, None si falla permanentemente
    """
    # obtener el tiempo actual, como tiempo de inicio para medir el tiempo de ejecucion de la funcion
    start_time = time.time()
    global proxy_cycle, proxies_usados
    # Inicializar el número de reintentos
    retries = 0
    while retries <= max_retries:
        # Esperar antes de hacer la solicitud para evitar solicitudes demasiado frecuentes
        time.sleep(min_interval) 

        # Obtener el siguiente proxy disponible de la lista
        proxy, proxy_id = get_next_proxy()
        try:
            if proxy is None or proxy_id == "LOCAL":
                # Realizar la solicitud GET cuando no hay proxies disponibles
                response = requests.get(url, headers=headers, data=payload, timeout=10)
            else:
                # Realizar la solicitud GET cuando hay proxies disponibles
                response = requests.get(url, headers=headers, data=payload, proxies=proxy, timeout=10)

            # actualiza el proxyes actual
            actualizar_proxie_usado(proxy_id)
                
            # Verificar si la solicitud fue exitosa
            if response.status_code == 200:
                # obtener el tiempo final para medir el tiempo de ejecucion de una solicitud exitosa
                end_time = time.time()
                # calcular el tiempo de ejecucion de una solicitud exitosa
                tiempo_de_ejecucion = end_time - start_time
                print(f"✅ {tiempo_de_ejecucion} Respuesta exitosa de la solicitud: {url} con proxy {proxy}\n")
                
                # Devolver la respuesta en formato JSON
                return response.json()
            # Si se agotan los proxies, esperar y reintentar
            elif proxy is None and proxy_id is None:
                print(f"❌ Error {response.status_code} Se agotaron los proxies. se esperaran {wait_time} segundos...")
                # Esperar un tiempo exponencial antes de reintentar
                time.sleep(wait_time)
                # Incrementar el tiempo de espera exponencialmente
                wait_time *= 2 
                # Incrementar el número de reintentos
                retries += 1
            else:
                if is_traffic_error(response.text):
                    # indicamos que el proxy actual esta bloqueado por lo que este proxy tiene que esperar VALOR_MAXIMO_DE_TIMEOUT 
                    proxies_usados[proxy_id]["available"] = False 
                    # crear un hilo que cuente el tiempo de espera para el proxy actual, si el hilo principal se cierra el hilo secundario tambien
                    #threading.Thread(target=temporizador_de_avilitador_de_proxy, args=(proxy_id,)).start()
                    threading.Thread(target=temporizador_de_avilitador_de_proxy, args=(proxy_id,), daemon=True).start()
                    # Si hay un error de tráfico, cambiar de proxy y reintenta la solicitud
                    print(f"❌ Error {response.status_code} por tráfico. Cambiando de proxy {proxy}...")
                else:
                    print(f"❌ Error {response.status_code} desconocido: {response.text}")
                    return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de solicitud {e} se hara un nuevo intento...")
            retries += 1
    # obtener el tiempo final para medir el tiempo de ejecucion de una solicitud exitosa
    end_time = time.time()
    # calcular el tiempo de ejecucion de una solicitud exitosa
    tiempo_de_ejecucion = end_time - start_time
    print(f"❌ {tiempo_de_ejecucion} Se agotaron los reintentos para la solicitud: {url} con proxy {proxy}\n")
    return None
    
def Betsson_scraping(url):
    payload = {}
    print(url)
    response = requests.request("GET", url, headers=BETSSON_HEADERS_SCRAPING_DEPORTES, data=payload)
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
                                    # Ejemplo: "1/14/16/f-rkgznc0f6ewqfpnw_now2g":"futbol/alemania/alemania-2-bundesliga/greuther-furth-1-fc-kaiserslautern?eventId=f-RKGznC0f6EWQFpNW_nOW2g"  => {"1": { categoryIds:"1", "categoryName": "futbol", "regionIds": { "14": { regionIds: "14", "regionName": "alemania", "competitionIds": { "16": { competitionIds: "16", "competitionName": "alemania-2-bundesliga", "eventId": { "f-rkgznc0f6ewqfpnw_now2g": { eventId: "f-rkgznc0f6ewqfpnw_now2g", "eventName": "greuther-furth-1-fc-kaiserslautern" } } } } } } }
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
                                            #elif i == 3:
                                            #    # obtengo el key 0
                                            #    k_0 = key_split[0]
                                            #    # obtengo el value 0
                                            #    v_0 = value_split[0]
                                            #    # obtengo el key 1
                                            #    k_1 = key_split[1]
                                            #    # obtengo el value 1
                                            #    v_1 = value_split[1]
                                            #    # obtengo el key 2
                                            #    k_2 = key_split[2]
                                            #    # obtengo el value 2
                                            #    v_2 = value_split[2]
                                            #    # obtengo el key 3
                                            #    k_3 = key_split[3]
                                            #    # obtengo el value 3
                                            #    v_3 = value_split[3]
                                            #    # verifico si el key no esta en sportCatalog_tree
                                            #    if k_3 not in sportCatalog_tree[k_0]["regionIds"][k_1]["competitionIds"][k_2]["eventIds"]:
                                            #        # añado el key al diccionario
                                            #        sportCatalog_tree[k_0]["regionIds"][k_1]["competitionIds"][k_2]["eventIds"][k_3] = {"eventId": k_3, "eventName": v_3}
                                # verifica si sportCatalog_tree no esta vacio
                                if sportCatalog_tree:
                                    return sportCatalog_tree
    return None                            

def procesar_request_obtener_apuestas_Betsson(Betsson_catalog, categoryId, regionId, competitionId, eventId, response):
    catalogo_de_Betsson = Betsson_catalog.copy()
    if response:
        if "data" in response:
            data = response["data"]
            if data:
                if "widgets" in data:
                    if data["widgets"] and isinstance(data["widgets"], list):
                        MarketList = None
                        for widget in data["widgets"]:
                            # buscamos el widget de tipo MarketList
                            if "type" in widget and widget["type"] == "MarketList":
                                MarketList = widget
                                break
                        # verificamos si MarketList es distinto de None    
                        if MarketList:
                            # verificamos si contiene "data"
                            if "data" in MarketList:
                                if MarketList["data"]:
                                    if "skeleton" in MarketList["data"]:
                                        if MarketList["data"]["skeleton"]:
                                            #verificar que skeleton contenga "marketIdByMarketTemplates"
                                            if "marketIdByMarketTemplates" in MarketList["data"]["skeleton"]:
                                                if MarketList["data"]["skeleton"]["marketIdByMarketTemplates"] and  isinstance(MarketList["data"]["skeleton"]["marketIdByMarketTemplates"], list):
                                                    marketTemplateId_for_every_marketId = {}
                                                    #recorrer la lista de marketIdByMarketTemplates
                                                    for marketIdByMarketTemplate in MarketList["data"]["skeleton"]["marketIdByMarketTemplates"]:
                                                        #verificar que marketIdByMarketTemplate contenga "marketTemplateId"
                                                        marketTemplateId = marketIdByMarketTemplate["marketTemplateId"] if "marketTemplateId" in marketIdByMarketTemplate else None
                                                        #verificar que marketIdByMarketTemplate contenga "marketIds"
                                                        marketIds = marketIdByMarketTemplate["marketIds"] if "marketIds" in marketIdByMarketTemplate else None
                                                        #verificar que marketIds sea de tipo lista
                                                        if marketIds and isinstance(marketIds, list) and marketTemplateId:
                                                            # añadimos el marketTemplateId y market Ids a la lista de apuestas en 
                                                            # catalogo_de_deportes[name]["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]
                                                            catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"] = catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"] if "apuestas" in catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId] else {}
                                                            catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"][marketTemplateId] = {
                                                                "marketTemplateId": marketTemplateId, 
                                                                "marketIds": {}
                                                            }
                                                            #recorrer la lista de marketIds
                                                            for marketId in marketIds:
                                                                # añadimos el marketId a la lista de apuestas en 
                                                                # catalogo_de_deportes[name]["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"][marketTemplateId]
                                                                catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"][marketTemplateId]["marketIds"][marketId] = {
                                                                    "marketId": marketId
                                                                }
                                                                # para cada marketId se le asigna su respectivo maketTemplateId
                                                                marketTemplateId_for_every_marketId[marketId] = marketTemplateId
                                                    #verificar que MarketList contenga "data"
                                                    if "data" in MarketList["data"]:
                                                        #verificamos si MarketList["data"]["data"] contiene "markets"
                                                        if "markets" in MarketList["data"]["data"]:
                                                            if MarketList["data"]["data"]["markets"] and isinstance(MarketList["data"]["data"]["markets"], list):
                                                                #recorrer la lista de markets
                                                                for market in MarketList["data"]["data"]["markets"]:
                                                                    #verificar si market contiene "id"
                                                                    marketId = market["id"] if "id" in market else None
                                                                    #verificar si market contiene "marketTemplateId"
                                                                    market_marketTemplateId = market["marketTemplateId"] if "marketTemplateId" in market else None
                                                                    #verificar si market contiene "columnLayout"
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
                                                                    if market_marketTemplateId in catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"]:
                                                                        fecha_actual = datetime.datetime.now()
                                                                        #convertir fecha_actual a string
                                                                        fecha_actual_str = fecha_actual.strftime(FORMATO_FECHA_ACTUAL)
                                                                        # asignar la fecha actual al eventId en catalogo_de_deportes como lastUpdate
                                                                        catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["lastUpdate"] = fecha_actual_str
                                                                        if marketId in catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"][market_marketTemplateId]["marketIds"]:
                                                                            catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"][market_marketTemplateId]["marketIds"][marketId].update({
                                                                                "marketId": marketId,
                                                                                "marketTemplateId": market_marketTemplateId,
                                                                                "columnLayout": columnLayout,
                                                                                "accordionGroup": accordionGroup,
                                                                                "sortOrder": sortOrder,
                                                                                "marketFriendlyName": marketFriendlyName,
                                                                                "label": label,
                                                                                "status": status,
                                                                                "lineValue": lineValue,
                                                                                "lineValueRaw": lineValueRaw
                                                                            })
                                                                if "selections" in MarketList["data"]["data"]:
                                                                    if MarketList["data"]["data"]["selections"] and isinstance(MarketList["data"]["data"]["selections"], list):
                                                                        #recorrer la lista de selections
                                                                        for selection in MarketList["data"]["data"]["selections"]:
                                                                            #verificamos si market contiene "marketId"
                                                                            marketId = selection["marketId"] if "marketId" in selection else None
                                                                            # obtener el marketTemplateId de la lista marketTemplateId_for_every_marketId con la finalidad de asignar el marketTemplateId a la lista de apuestas
                                                                            selection_marketTemplateId = marketTemplateId_for_every_marketId[marketId] if marketId in marketTemplateId_for_every_marketId else None
                                                                            # verificar si selection_marketTemplateId es distinto de None
                                                                            if selection_marketTemplateId:
                                                                                # verificar si marketId esta en catalogo_de_deportes
                                                                                if marketId in catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"][selection_marketTemplateId]["marketIds"]:
                                                                                    # verificar si marketId contiene "odds"
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
                                                                                    # verificamos si apuestas no esta en la lista de apuestas
                                                                                    if "apuestas" not in catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"][selection_marketTemplateId]["marketIds"][marketId]:
                                                                                        catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"][selection_marketTemplateId]["marketIds"][marketId]["apuestas"] = []
                                                                                    
                                                                                    # añadimos la informacion 
                                                                                    catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"][selection_marketTemplateId]["marketIds"][marketId]["apuestas"].append({
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
                                                                        return catalogo_de_Betsson
    return None

def request_obtener_apuestas_Betsson(categoryId, regionId, competitionId, eventId, i, longitud):
    link = f"https://www.betsson.co/api/sb/v1/widgets/view/v1?configurationKey=sportsbook.event.v2&eventId={eventId}&excludedWidgetKeys=sportsbook.events-table-mini"
    print(f"🔍 {i}/{longitud} Obteniendo apuestas de Betsson para eventId")
    response = make_get_request(link, BETSSON_HEADERS, {})
    return { "categoryId": categoryId, "regionId": regionId, "competitionId": competitionId, "eventId": eventId, "response": response}

def obtener_apuestas_Betsson(Betsson_catalog, categoryId, regionId, competitionId, eventId):
    catalogo_de_Betsson = Betsson_catalog.copy()
    #print(link)
    link = f"https://www.betsson.co/api/sb/v1/widgets/view/v1?configurationKey=sportsbook.event.v2&eventId={eventId}&excludedWidgetKeys=sportsbook.events-table-mini"
    response = make_get_request(link, BETSSON_HEADERS, {})
    if response:
        if "data" in response:
            data = response["data"]
            if data:
                if "widgets" in data:
                    if data["widgets"] and isinstance(data["widgets"], list):
                        MarketList = None
                        for widget in data["widgets"]:
                            # buscamos el widget de tipo MarketList
                            if "type" in widget and widget["type"] == "MarketList":
                                MarketList = widget
                                break
                        # verificamos si MarketList es distinto de None    
                        if MarketList:
                            # verificamos si contiene "data"
                            if "data" in MarketList:
                                if MarketList["data"]:
                                    if "skeleton" in MarketList["data"]:
                                        if MarketList["data"]["skeleton"]:
                                            #verificar que skeleton contenga "marketIdByMarketTemplates"
                                            if "marketIdByMarketTemplates" in MarketList["data"]["skeleton"]:
                                                if MarketList["data"]["skeleton"]["marketIdByMarketTemplates"] and  isinstance(MarketList["data"]["skeleton"]["marketIdByMarketTemplates"], list):
                                                    marketTemplateId_for_every_marketId = {}
                                                    #recorrer la lista de marketIdByMarketTemplates
                                                    for marketIdByMarketTemplate in MarketList["data"]["skeleton"]["marketIdByMarketTemplates"]:
                                                        #verificar que marketIdByMarketTemplate contenga "marketTemplateId"
                                                        marketTemplateId = marketIdByMarketTemplate["marketTemplateId"] if "marketTemplateId" in marketIdByMarketTemplate else None
                                                        #verificar que marketIdByMarketTemplate contenga "marketIds"
                                                        marketIds = marketIdByMarketTemplate["marketIds"] if "marketIds" in marketIdByMarketTemplate else None
                                                        #verificar que marketIds sea de tipo lista
                                                        if marketIds and isinstance(marketIds, list) and marketTemplateId:
                                                            # añadimos el marketTemplateId y market Ids a la lista de apuestas en 
                                                            # catalogo_de_deportes[name]["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]
                                                            catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"] = catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"] if "apuestas" in catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId] else {}
                                                            catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"][marketTemplateId] = {
                                                                "marketTemplateId": marketTemplateId, 
                                                                "marketIds": {}
                                                            }
                                                            #recorrer la lista de marketIds
                                                            for marketId in marketIds:
                                                                # añadimos el marketId a la lista de apuestas en 
                                                                # catalogo_de_deportes[name]["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"][marketTemplateId]
                                                                catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"][marketTemplateId]["marketIds"][marketId] = {
                                                                    "marketId": marketId
                                                                }
                                                                # para cada marketId se le asigna su respectivo maketTemplateId
                                                                marketTemplateId_for_every_marketId[marketId] = marketTemplateId
                                                    #verificar que MarketList contenga "data"
                                                    if "data" in MarketList["data"]:
                                                        #verificamos si MarketList["data"]["data"] contiene "markets"
                                                        if "markets" in MarketList["data"]["data"]:
                                                            if MarketList["data"]["data"]["markets"] and isinstance(MarketList["data"]["data"]["markets"], list):
                                                                #recorrer la lista de markets
                                                                for market in MarketList["data"]["data"]["markets"]:
                                                                    #verificar si market contiene "id"
                                                                    marketId = market["id"] if "id" in market else None
                                                                    #verificar si market contiene "marketTemplateId"
                                                                    market_marketTemplateId = market["marketTemplateId"] if "marketTemplateId" in market else None
                                                                    #verificar si market contiene "columnLayout"
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
                                                                    if market_marketTemplateId in catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"]:
                                                                        fecha_actual = datetime.datetime.now()
                                                                        #convertir fecha_actual a string
                                                                        fecha_actual_str = fecha_actual.strftime(FORMATO_FECHA_ACTUAL)
                                                                        # asignar la fecha actual al eventId en catalogo_de_deportes como lastUpdate
                                                                        catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["lastUpdate"] = fecha_actual_str
                                                                        if marketId in catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"][market_marketTemplateId]["marketIds"]:
                                                                            catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"][market_marketTemplateId]["marketIds"][marketId].update({
                                                                                "marketId": marketId,
                                                                                "marketTemplateId": market_marketTemplateId,
                                                                                "columnLayout": columnLayout,
                                                                                "accordionGroup": accordionGroup,
                                                                                "sortOrder": sortOrder,
                                                                                "marketFriendlyName": marketFriendlyName,
                                                                                "label": label,
                                                                                "status": status,
                                                                                "lineValue": lineValue,
                                                                                "lineValueRaw": lineValueRaw
                                                                            })
                                                                if "selections" in MarketList["data"]["data"]:
                                                                    if MarketList["data"]["data"]["selections"] and isinstance(MarketList["data"]["data"]["selections"], list):
                                                                        #recorrer la lista de selections
                                                                        for selection in MarketList["data"]["data"]["selections"]:
                                                                            #verificamos si market contiene "marketId"
                                                                            marketId = selection["marketId"] if "marketId" in selection else None
                                                                            # obtener el marketTemplateId de la lista marketTemplateId_for_every_marketId con la finalidad de asignar el marketTemplateId a la lista de apuestas
                                                                            selection_marketTemplateId = marketTemplateId_for_every_marketId[marketId] if marketId in marketTemplateId_for_every_marketId else None
                                                                            # verificar si selection_marketTemplateId es distinto de None
                                                                            if selection_marketTemplateId:
                                                                                # verificar si marketId esta en catalogo_de_deportes
                                                                                if marketId in catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"][selection_marketTemplateId]["marketIds"]:
                                                                                    # verificar si marketId contiene "odds"
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
                                                                                    # verificamos si apuestas no esta en la lista de apuestas
                                                                                    if "apuestas" not in catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"][selection_marketTemplateId]["marketIds"][marketId]:
                                                                                        catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"][selection_marketTemplateId]["marketIds"][marketId]["apuestas"] = []
                                                                                    
                                                                                    # añadimos la informacion 
                                                                                    catalogo_de_Betsson["Catalogo_de_deportes"][categoryId]["regionIds"][regionId]["competitionIds"][competitionId]["eventIds"][eventId]["apuestas"][selection_marketTemplateId]["marketIds"][marketId]["apuestas"].append({
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
                                                                        return catalogo_de_Betsson
    return None

def request_obtener_partidos_Betsson(categoryId, regionId,competitionId,eventPhase, i, longitud):
    link = f"https://www.betsson.co/api/sb/v1/widgets/events-table/v2?categoryIds={categoryId}&competitionIds={competitionId}&eventPhase={eventPhase}&eventSortBy=StartDate"
    print(f"procesando {i}/{longitud} {link}")
    response = make_get_request(link, BETSSON_HEADERS, {})
    # devolver json con los valores de entrada mas la respuesta obtenida 
    return {"categoryId": categoryId, "regionId":regionId, "competitionId": competitionId, "eventPhase": eventPhase, "response": response}

def procesar_respuesta_obtener_partidos_Betsson(response):
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
        return lista_de_partidos
    return None

def obtener_partidos_Betsson(categoryId,competitionId,eventPhase):
    #rango_de_fechas = generar_rango_fechas()
    #link = "https://www.betsson.co/api/sb/v1/widgets/events-table/v2?categoryIds=138&competitionIds=26430&eventPhase=All&eventSortBy=StartDate&maxMarketCount=3&pageNumber=1&regionIds=1"
    #link = "https://www.betsson.co/api/sb/v1/widgets/events-table/v2?categoryIds=11&competitionIds=23122&eventPhase=Prematch&eventSortBy=StartDate&maxMarketCount=3&pageNumber=1&startsBefore=2025-01-11T04:59:59Z&startsOnOrAfter=2025-01-10T05:00:00Z"
    #print(link)
    link = f"https://www.betsson.co/api/sb/v1/widgets/events-table/v2?categoryIds={categoryId}&competitionIds={competitionId}&eventPhase={eventPhase}&eventSortBy=StartDate"
    response = make_get_request(link, BETSSON_HEADERS, {})
    # obtenermos el json de la respuesta y verificamos si es distinto de None
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
        return lista_de_partidos
    return None

def actualizar_catalogo_deportes_de_Betsson(deportes_seleccionados, catalogo_deportes, actualizacion_de_catalogo_deportes):
    # verificar si catalogo_deportes es un diccionario y actualizacion_de_catalogo_deportes es un diccionario y deportes_seleccionados es una lista
    if isinstance(catalogo_deportes, dict) and isinstance(actualizacion_de_catalogo_deportes, dict) and isinstance(deportes_seleccionados, list):
        # verificar si catalogo_deportes contiene el key Betsson 
        if Betsson not in catalogo_deportes:
            catalogo_deportes[Betsson] = {"name": Betsson, "Catalogo_de_deportes": {}}
        # obtener las keys de catalogo_deportes y las keys de actualizacion_de_catalogo_deportes
        keys_catalogo_deportes = catalogo_deportes[Betsson]["Catalogo_de_deportes"].keys()
        keys_actualizacion_de_catalogo_deportes = [k for k in actualizacion_de_catalogo_deportes.keys() if (len(deportes_seleccionados)== 0 or k in deportes_seleccionados) ]
        # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
        for key in keys_actualizacion_de_catalogo_deportes:
            if key not in keys_catalogo_deportes:
                catalogo_deportes[Betsson]["Catalogo_de_deportes"][key] = actualizacion_de_catalogo_deportes[key]
            else:
                # verificar si catalogo_deportes contiene la key regionIds
                if "regionIds" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]:
                    catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"] = actualizacion_de_catalogo_deportes[key]["regionIds"]
                else:
                    # obtener las keys de regionIds de catalogo_deportes y las keys de regionIds de actualizacion_de_catalogo_deportes
                    keys_regionIds = catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"].keys()
                    keys_actualizacion_regionIds =   actualizacion_de_catalogo_deportes[key]["regionIds"].keys()
                    # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
                    for key_regionIds in keys_actualizacion_regionIds:
                        if key_regionIds not in keys_regionIds:
                            catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]
                        else:
                            # verificar si catalogo_deportes contiene la key competitionIds
                            if "competitionIds" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]:
                                catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"]
                            else:
                                # obtener las keys de competitionIds de catalogo_deportes y las keys de competitionIds de actualizacion_de_catalogo_deportes
                                keys_competitionIds = catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"].keys()
                                keys_actualizacion_competitionIds =   actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"].keys()
                                # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
                                for key_competitionIds in keys_actualizacion_competitionIds:
                                    if key_competitionIds not in keys_competitionIds:
                                        catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]
                                    else:
                                        catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"] = {}
                                        # verificar si catalogo_deportes contiene la key eventIds
                                        #if "eventIds" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]:
                                        #    catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"]
                                        #else:
                                        #    # obtener las keys de eventId de catalogo_deportes y las keys de eventId de actualizacion_de_catalogo_deportes
                                        #    keys_eventId = catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"].keys()
                                        #    keys_actualizacion_eventId =   actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"].keys()
                                        #    # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
                                        #    for key_eventId in keys_actualizacion_eventId:
                                        #        if key_eventId not in keys_eventId:
                                        #            catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"][key_eventId] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"][key_eventId]
                                        #        # --------------------------------------------------------------------------------
    return catalogo_deportes                                                         

"""

def actualizar_catalogo_deportes_de_Betsson(deportes_seleccionados, catalogo_deportes, actualizacion_de_catalogo_deportes):
    # verificar si catalogo_deportes es un diccionario y actualizacion_de_catalogo_deportes es un diccionario y deportes_seleccionados es una lista
    if isinstance(catalogo_deportes, dict) and isinstance(actualizacion_de_catalogo_deportes, dict) and isinstance(deportes_seleccionados, list):
        # verificar si catalogo_deportes contiene el key Betsson 
        if Betsson not in catalogo_deportes:
            catalogo_deportes[Betsson] = {"name": Betsson, "Catalogo_de_deportes": {}}
        # obtener las keys de catalogo_deportes y las keys de actualizacion_de_catalogo_deportes
        keys_catalogo_deportes = catalogo_deportes[Betsson]["Catalogo_de_deportes"].keys()
        keys_actualizacion_de_catalogo_deportes = [k for k in actualizacion_de_catalogo_deportes.keys() if (len(deportes_seleccionados)== 0 or k in deportes_seleccionados) ]
        # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
        for key in keys_actualizacion_de_catalogo_deportes:
            if key not in keys_catalogo_deportes:
                catalogo_deportes[Betsson]["Catalogo_de_deportes"][key] = actualizacion_de_catalogo_deportes[key]
            else:
                # verificar si catalogo_deportes contiene la key regionIds
                if "regionIds" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]:
                    catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"] = actualizacion_de_catalogo_deportes[key]["regionIds"]
                else:
                    # obtener las keys de regionIds de catalogo_deportes y las keys de regionIds de actualizacion_de_catalogo_deportes
                    keys_regionIds = catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"].keys()
                    keys_actualizacion_regionIds =   actualizacion_de_catalogo_deportes[key]["regionIds"].keys()
                    # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
                    for key_regionIds in keys_actualizacion_regionIds:
                        if key_regionIds not in keys_regionIds:
                            catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]
                        else:
                            # verificar si catalogo_deportes contiene la key competitionIds
                            if "competitionIds" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]:
                                catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"]
                            else:
                                # obtener las keys de competitionIds de catalogo_deportes y las keys de competitionIds de actualizacion_de_catalogo_deportes
                                keys_competitionIds = catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"].keys()
                                keys_actualizacion_competitionIds =   actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"].keys()
                                # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
                                for key_competitionIds in keys_actualizacion_competitionIds:
                                    if key_competitionIds not in keys_competitionIds:
                                        catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]
                                    else:
                                        # verificar si catalogo_deportes contiene la key eventIds
                                        if "eventIds" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]:
                                            catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"]
                                        else:
                                            # obtener las keys de eventId de catalogo_deportes y las keys de eventId de actualizacion_de_catalogo_deportes
                                            keys_eventId = catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"].keys()
                                            keys_actualizacion_eventId =   actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"].keys()
                                            # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
                                            for key_eventId in keys_actualizacion_eventId:
                                                if key_eventId not in keys_eventId:
                                                    catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"][key_eventId] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventIds"][key_eventId]
                                                # --------------------------------------------------------------------------------
                                                else:
                                                    # verificar si catalogo_deportes contiene la key apuestas
                                                    if "apuestas" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]:
                                                        catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"]
                                                    else:
                                                        partido_vencido = False
                                                        # verificar si catalogo_deportes contiene la key startDate 
                                                        if "startDate" in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]:
                                                            # verificar si la fecha de startDate ya ha vencido, es decir que es menor a la fecha actual
                                                            startDate = catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["startDate"]
                                                            # convertir en datetime la fecha de startDate
                                                            startDate = datetime.strptime(startDate, "%Y-%m-%dT%H:%M:%S.%fZ")
                                                            # obtener la fecha actual
                                                            fecha_actual = datetime.now()
                                                            # verificar si la fecha de startDate es menor a la fecha actual
                                                            partido_vencido = startDate < fecha_actual

                                                        if not partido_vencido:
                                                            # obtener las keys de apuestas de catalogo_deportes y las keys de apuestas de actualizacion_de_catalogo_deportes
                                                            keys_apuestas = catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"].keys()
                                                            keys_actualizacion_apuestas = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"].keys()
                                                            # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
                                                            for key_apuestas in keys_actualizacion_apuestas:
                                                                if key_apuestas not in keys_apuestas:
                                                                    catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]
                                                                else:
                                                                    # verificar si catalogo_deportes contiene la key marketIds
                                                                    if "marketIds" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]:
                                                                        catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"]
                                                                    else:
                                                                        # obtener las keys de marketIds de catalogo_deportes y las keys de marketIds de actualizacion_de_catalogo_deportes
                                                                        keys_marketIds = catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"].keys()
                                                                        keys_actualizacion_marketIds = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"].keys()
                                                                        # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
                                                                        for key_marketIds in keys_actualizacion_marketIds:
                                                                            if key_marketIds not in keys_marketIds:
                                                                                catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]
                                                                            else: 
                                                                                # verificar si catalogo_deportes contiene la key apuestas
                                                                                if "apuestas" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]:
                                                                                    catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"]
                                                                                else: 
                                                                                    # obtener las keys de apuestas de catalogo_deportes y las keys de apuestas de actualizacion_de_catalogo_deportes
                                                                                    keys_apuestas_2 = catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"].keys()
                                                                                    keys_actualizacion_apuestas_2 = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"].keys()
                                                                                    # verificar si las keys de actualizacion_de_catalogo_deportes no esta en catalogo_deportes
                                                                                    for key_apuestas_2 in keys_actualizacion_apuestas_2:
                                                                                        if key_apuestas_2 not in keys_apuestas_2:
                                                                                            catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]
                                                                                        else:
                                                                                            # verificar si catalogo_deportes contiene la key odds
                                                                                            if "odds" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]:
                                                                                                catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["odds"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["odds"]
                                                                                            else:
                                                                                                # verificar si el valor de odds en actualizacion_de_catalogo_deportes es distinto al valor de odds en catalogo_deportes
                                                                                                if actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["odds"] != catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["odds"]:
                                                                                                    catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["odds"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["odds"]
                                                                                            
                                                                                            # verificar si catalogo_deportes contiene la key status
                                                                                            if "status" not in catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]:
                                                                                                catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["status"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["status"]
                                                                                            else:
                                                                                                # verificar si el valor de status en actualizacion_de_catalogo_deportes es distinto al valor de status en catalogo_deportes
                                                                                                if actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["status"] != catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["status"]:
                                                                                                    catalogo_deportes[Betsson]["Catalogo_de_deportes"][key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["status"] = actualizacion_de_catalogo_deportes[key]["regionIds"][key_regionIds]["competitionIds"][key_competitionIds]["eventId"][key_eventId]["apuestas"][key_apuestas]["marketIds"][key_marketIds]["apuestas"][key_apuestas_2]["status"]
    return catalogo_deportes                                                         

"""
