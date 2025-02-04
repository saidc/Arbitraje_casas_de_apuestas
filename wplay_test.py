import os
import json
import requests
from bs4 import BeautifulSoup

from casas_de_apuestas.Wplay.Wplay_config import link_deportes, link_Wplay



def request_obtener_deportes_Wplay():
    payload = {} 
    headers = {}
    # Realizamos la peticion GET a la pagina de deportes
    response = requests.get(link_deportes, headers=headers, data=payload, timeout=10)
    # si el codigo de respuesta es 200 entonces hacer scraping
    if response.status_code == 200:
        return response
    return None 

global Contador
Contador = 0

def procesar_request_obtener_deportes_Wplay(response):
    global Contador
    # obtener informacion de apuestas de un partido
    def obtener_informacion_de_apuesta(apuesta):
        #obtener de apuesta un atributo data-mkt_id
        apuesta_id = str(apuesta['data-mkt_id'])
        # obtener de apuesta un hijo con etiqueta h6
        tag_h6 = apuesta.findChild("h6")
        # de tag_h6 obtener un hijo con etiqueta span con class="mkt-name" y obtener el texto
        apuesta_name = str(tag_h6.findChild("span", {"class": "mkt-name"}).text)
        #print(apuesta_name)
        return {"id": apuesta_id, "name": apuesta_name}
    
    # obtener informacion de apuestas de un partido
    def solicitar_apuestas(partido_id, apuestas_url):
        payload = {}
        headers = {}
        # Realizamos la peticion GET a la pagina de apuestas
        response = requests.get(apuestas_url, headers=headers, data=payload, timeout=10)
        # si el codigo de respuesta es 200 entonces hacer scraping
        if response.status_code == 200:
            # pasamos el texto de reaponse a un objeto BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            # obtener un div con id="main-area"
            main_area = soup.find("div", {"id": "main-area"})
            # del main_area obtener las etiquetas hijas
            tag_div = main_area.findChildren("div", recursive=False)
            # de tag_div obtener el hijo que tenga como atributo data-msg_stamp
            divs = [div for div in tag_div if 'data-ev_id' in div.attrs]

            if len(divs) > 0:
                div_0 = divs[0]
                # del div_0 obtener las etiquetas hijas
                div_0 = div_0.findChildren("div", recursive=False)

                # de tag_div obtener el hijo que tenga como atributo class
                divs = [div for div in div_0 if not ('class' in div.attrs)]
                if len(divs) > 0:
                    divs = divs[0]
                    #print(divs)
                    # de divs obtener un hijo con etiqueta div
                    apuestas = divs.findChildren("div", recursive=False)
                    #print(apuestas)
                    # verificar si apuestas es de tipo lista
                    if isinstance(apuestas, list):
                        # obtener las apuestas de un partido
                        apuestas = [{str(apuesta['data-mkt_id']):obtener_informacion_de_apuesta(apuesta)} for apuesta in apuestas if 'data-mkt_id' in apuesta.attrs]
                        return apuestas
                    else:
                        print(f"            ❌ Error, apuestas no es de tipo lista, del partido {partido_id}")
                else:
                    print(f"            ❌ Error, divs es None, del partido {partido_id}")
            else:
                print(f"            ❌ Error, apuestas es None, del partido {partido_id}")
        else:
            print(f"            ❌ Error de solicitud de apuestas del partido {partido_id}")
        return []
    
    # obtener informacion de partido
    def obtener_informacion_de_partido(partido):
        global Contador
        Contador += 1
        # obtener el valor de data-mkt_id
        partido_id = str(partido['data-mkt_id'])
        # obtener un hijo con etiqueta td y class="time coupon-scoreboard"
        tag_td_fecha = partido.findChild("td", {"class": "time coupon-scoreboard"})
        # de tag_td_fecha obtener una etiqueta span con class="date" y obtener el texto
        partido_fecha = str(tag_td_fecha.findChild("span", {"class": "date"}).text)
        # de tag_td_fecha obtener una etiqueta span con class="time" y obtener el texto
        partido_hora = str(tag_td_fecha.findChild("span", {"class": "time"}).text)

        # del partido obtener un hijo con etiqueta td y class="mkt-count"
        tag_td_mkt_count = partido.findChild("td", {"class": "mkt-count"})
        # de tag_td_mkt_count obtener un hijo con etiqueta a 
        tag_a = tag_td_mkt_count.findChild("a")
        # del tag_a obtener href y concatenar con link_Wplay
        apuestas_url = f"{link_Wplay}{str(tag_a['href'])}" if 'href' in tag_a.attrs else None
        apuestas = []
        if Contador < 2:
            # obtener informacion de apuestas de un partido
            apuestas = solicitar_apuestas(partido_id, apuestas_url)
        return {"id": partido_id, "fecha": partido_fecha, "hora": partido_hora, "url": apuestas_url, "apuestas": apuestas}
    
    # obtener informacion de partidos de la liga
    def solicitar_partidos(liga_name,liga_url):
        global Contador
        payload = {}
        headers = {}
        # Realizamos la peticion GET a la pagina de la liga
        response = requests.get(liga_url, headers=headers, data=payload, timeout=10)
        # si el codigo de respuesta es 200 entonces hacer scraping
        if response.status_code == 200:
            # pasamos el texto de reaponse a un objeto BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            # obtener un div con id="main-area"
            main_area = soup.find("div", {"id": "main-area"})
            #print("main_area: ", main_area)
            # del main_area obtener las etiquetas hijas
            tag_div = main_area.findChildren("div", recursive=False)
            # de tag_div obtener el hijo que tenga como atributo data-msg_stamp
            divs = [div for div in tag_div if 'data-msg_stamp' in div.attrs]

            if len(divs) > 0:
                partidos = divs[0]
                # de partidos obtener un hijo con etiqueta h4
                tag_h4 = partidos.findChild("h4")
                # del h4 obtener un hijo con etiqueta div
                tag_div = tag_h4.findChild("div")
                # obtener el texto del div
                liga_name2 = str(tag_div.text)
                #print("partidos: ", partidos)
                #return None
                # verificar si liga_name es igual a liga_name2
                if liga_name != liga_name2:
                    print(f"            ❌ el nombre de la liga es {liga_name} es diferente a {liga_name2}")
                else:
                    print(f"            ✅ el nombre de la liga es {liga_name} es igual a {liga_name2}")
                    # de partidos buscar una etiqueta tbody
                    tag_tbody = partidos.find("tbody")
                    # obtener todos los hijos de tbody como children
                    partidos = tag_tbody.findChildren("tr", recursive=False)
                    # verificar si partidos es de tipo lista
                    if isinstance(partidos, list):
                        partidos = [{f"{str(partido['data-mkt_id'])}":obtener_informacion_de_partido(partido)} for partido in partidos if 'data-mkt_id' in partido.attrs ]
                        return partidos
                    else:
                        print(f"            ❌ Error, partidos no es de tipo lista, de la liga {liga_name}")
            else:
                print(f"            ❌ Error, partidos es None, de la liga {liga_name}")
        else:
            print(f"            ❌ Error de solicitud de partidos de la liga {liga_name}")
        return []
        
    # obtener informacion de liga
    def obtener_informacion_de_liga(i,l,liga):
        global Contador
        #Contador += 1
        liga_id = str(liga['data-sb_type_id'])
        # obtener un hijo con etiqueta a
        tag_a = liga.findChild("a")
        # obtener href de la etiqueta a
        liga_url = f"{link_Wplay}{str(tag_a['href'])}" if 'href' in tag_a.attrs else None
        # obtener un hijo con etiqueta span y obtener el texto
        liga_name = str(tag_a.findChild("span").text) if tag_a.findChild("span") else None
        print(f"        {i}/{l} - {liga_name}")
        # obtener informacion de partidos de la liga
        partidos = []
        if Contador < 2:
            partidos = solicitar_partidos(liga_name,liga_url)
        # retornar un diccionario con la informacion de la liga
        return {"name": liga_name, "id": liga_id, "url": liga_url, "partidos": partidos}

    # obtener informacion de region
    def obtener_informacion_de_region(i,l,region):
        region_id = str(region['data-sb_class_id'])
        # de la region obtener un hijo con etiqueta div
        tag_div = region.findChild("div")
        # del div obtener un hijo con etiqueta span y obtener el texto
        region_name = str(tag_div.findChild("span").text)
        print(f"    {i}/{l} - {region_name}")
        # de la region obtener un hijo con etiqueta ul
        tag_ul = region.findChild("ul")
        if tag_ul is None:
            ligas = None
        else:
            # obtener los hijos de la etiqueta ul
            ligas = tag_ul.findChildren("li", recursive=False)
            ligas = {f"{str(liga['data-sb_type_id'])}":obtener_informacion_de_liga(j,len(ligas),liga) for j, liga in enumerate(ligas) if 'data-sb_type_id' in liga.attrs}

        # retornar un diccionario con la informacion de la region
        return { "name": region_name, "id": region_id, "ligas": ligas }
        
    # obtener informacion de deporte
    def obtener_informacion_de_deporte(i,l,deporte):
        # obtener de cada hijo el valor de la variable data-sport_code
        deporte_tag = str(deporte["data-sport_code"])
        #print(deporte_tag)
        # obtener un hijo como children de etiqueta "a" y obtener el texto
        tag_a = deporte.findChild("a")
        # obtener etiqueta span dentro de la etiqueta a
        tag_span = tag_a.findChild("span")
        deporte_name = str(tag_span.text)
        print(f"{i}/{l} - {deporte_name}")
        # obtener href de la etiqueta a
        deporte_url = f"{link_Wplay}{str(tag_a["href"])}" if 'href' in tag_a.attrs else None
        # obtener un hijo con etiqueta ul 
        tag_ul = deporte.findChild("ul")
        if tag_ul is None:
            regiones = None
        else:
            regiones = tag_ul.findChildren("li", recursive=False)
            regiones = {f"{str(region['data-sb_class_id'])}":obtener_informacion_de_region(j,len(regiones),region) for j, region in enumerate(regiones) if 'data-sb_class_id' in region.attrs}
        # retornar un diccionario con la informacion del deporte
        return {"tag": deporte_tag, "name": deporte_name, "url": deporte_url ,"regiones":regiones}
    
    # obtener informacion de los deportes de la pagina
    def get_SPORTS_from_SPORTS_NAV(soup):
        # buscamos un div que contenga data-src_code=SPORTS_NAV
        deportes = soup.find("div", {"data-src_code": "SPORTS_NAV"})
        # obtener un ul con class="hierarchy"
        deportes = deportes.find("ul", {"class": "hierarchy"})
        # obtener todos los hijos como children
        deportes = deportes.findChildren("li", recursive=False)
        # verificar si deportes es de tipo lista 
        if isinstance(deportes, list):
            return deportes
        return None

    catalogo_de_deportes = {}
    # pasamos el texto de reaponse a un objeto BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # obtener los deportes de la pagina
    deportes = get_SPORTS_from_SPORTS_NAV(soup)

    # obtener informacion de cada deporte
    catalogo_de_deportes = {f"{deporte['data-sport_code']}":obtener_informacion_de_deporte(i,len(deportes),deporte) for i, deporte in enumerate(deportes) if 'data-sport_code' in deporte.attrs} 

    return catalogo_de_deportes

response = request_obtener_deportes_Wplay()
catalogo_de_deportes = procesar_request_obtener_deportes_Wplay(response)

print(f"contador: {Contador}")

# verificar si el archivo "deportes_Wplay.json" existe de lo contrario crearlo
if os.path.exists("deportes_Wplay.json"):
    #os.remove("deportes_Wplay.json")
    with open("deportes_Wplay.json", "w") as file:
        json.dump({}, file, indent=4)

# guardar en un archivo json
with open("deportes_Wplay.json", "w") as file:
    json.dump(catalogo_de_deportes, file, indent=4)

print("Archivo deportes_Wplay.json creado con exito!")