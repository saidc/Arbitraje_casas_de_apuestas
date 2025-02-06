import os
import json
import requests
from bs4 import BeautifulSoup

Count = 0

def obtener_contenido_de_table(table):
    return {"table": table.name}

def obtener_contenido_de_div(div):
    return {"div": div.name}

def obtener_contenido_de_ul(ul):
    return {"ul": ul.name}

# obtener informacion de apuestas de un partido
def obtener_informacion_de_apuesta(apuesta):
    #obtener de apuesta un atributo data-mkt_id
    apuesta_id = str(apuesta['data-mkt_id'])

    apuesta_name = None 
    tipo_de_contenido = None
    contenido = None
    fetch_url = None

    for ch in apuesta.children:
        if ch.name == "h6":
            # obtener un hijo con etiqueta span con class="mkt-name"
            h6 = [span for span in ch.children if span.name == "span" ] #and span['class'] == "mkt-name"]
            # h6 es una lista, obtener el primer elemento de la lista si la longitud es mayor a cero
            apuesta_name = h6[0].text if len(h6) > 0 else None
            
        elif ch.name == "div":
            tags_name = [tag.name for tag in ch.children if tag.name is not None]
            if len(tags_name) > 0:
                tag_name = tags_name[0]
                if tag_name == "table":
                    tipo_de_contenido = "table"
                    contenido = obtener_contenido_de_table(ch)
                elif tag_name == "div":
                    tipo_de_contenido = "div"
                    contenido = obtener_contenido_de_div(ch)
                elif tag_name == "ul":
                    tipo_de_contenido = "ul"
                    contenido = obtener_contenido_de_ul(ch)
            
    
    if tipo_de_contenido is None and 'data-fetch_url' in apuesta.attrs:
        fetch_url = str(apuesta['data-fetch_url'])
        return {"id": apuesta_id, "name": apuesta_name, "fetch_url": fetch_url}
    else:
        return {"id": apuesta_id, "name": apuesta_name, "tipo_de_contenido": tipo_de_contenido, "contenido": contenido}
    

# obtener informacion de apuestas de un partido
def solicitar_apuestas(partido_id, apuestas_url):
    payload = {}
    headers = {}
    
    print("apuestas_url: ", apuestas_url)

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
                # del divs obtener las etiquetas hijas
                apuestas = divs.findChildren("div", recursive=False)
                
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

partido_id = 24961161
url = "https://apuestas.wplay.co/es/e/24961161/Celtic-v-Bayern-Munich"

apuestas = solicitar_apuestas(partido_id, url)
# guardar las apuestas en un archivo json
with open(f"apuestas_{partido_id}.json", "w", encoding="utf-8") as file:
    json.dump(apuestas, file, indent=4)

print(f"Se han guardado las apuestas en el archivo apuestas_{partido_id}.json")

# https://apuestas.wplay.co/web_nr?use_interactive_correct_score_layout=N&mkt_id=623277034&key=sportsbook.cms.handlers.get_mkt_content
# https://apuestas.wplay.co/web_nr?use_interactive_correct_score_layout=N&mkt_id=623277110&key=sportsbook.cms.handlers.get_mkt_content
"""
:authority:apuestas.wplay.co
:method:GET
:path:/web_nr?use_interactive_correct_score_layout=N&mkt_id=623277034&key=sportsbook.cms.handlers.get_mkt_content
:scheme:https
accept:*/*
accept-encoding:gzip, deflate, br, zstd
accept-language:es-419,es;q=0.9,ru;q=0.8
cache-control:no-cache
cookie:GN_TZ_MODE=A-5; GN_PRC=%22DEC%22; GN_REGISTERED=Y; GN_SPORTS_REDIRECT=Y; GN_TREGION="83-HlFSu-nXvSr9JOG7sNnXyYdICck2p0jfnyzNC6oU="; GN_WPLAY_SPORTS=Y; _gcl_au=1.1.1763528229.1738552798; _fbp=fb.1.1738552798107.903523006836543467; _ga=GA1.1.1509873554.1738552798; _global=CO,0,BOGOTA,5000,0; GN_SESSTRACKING=0782e3fb-74d9-488d-aee5-922dd5d8f8e3; GN_SESSION=1738768896869; GN_POPUP_MODAL_COOKIE=N; GN_BETSLIP_WPLAY="KFyq2XlgsLevVD-Dd_I1cODDP7w7-6bMMv3or_PTn8k8gLOXO9-wvwpX1iTy1x8SDN0oaWiwZ7cBs3Qzgueq21DCpsOXrrUc4qYJBF9UweF_oLOJgahC9OuUVTYn6Wfk_UCuPQQ6aauFLJGsVozIMcjbqzWiq0VQ6TUiJ0dVdeOUukbcCz3wSP0__kEiLe1LmSFLWSc5Aryyfm3uD9GQQk5IrLv8_cSapVXKS27XjHypfVy02nSbrqGH_JtujaBFDAQx2dQztGS9JimJqbTDRcAjqzpp81p37u1f02KefvaILS2_4yYkW71udBsPY3fZGYFkVp-_Id1266GvwmlL8Iz0q8e9VCBaacGk5rmAAfk6ekjR0-hvS021yzQ9T_ufTujsO-53o-SRDMOeAMffyBxZxmQiwp2phyZncftKeigx6rsbSVwg6_Ee2dCBR7duHngD4BqRpedtA0giHYoIlYi5x1PkWhKFLOnZzBErwFU0CQxsXFjxqVNR9BmbVBWs-bTohst2FCWYb-UjmmF8Ip27O8DrggIMVKbpzT5GpHY="; GN_BS_OPTIONS_WPLAY=%7B%22bet_views%22%3A%7B%22hidden%22%3A%5B%5D%7D%2C%22prc_change_policy%22%3Anull%2C%22views%22%3A%7B%22hidden%22%3A%5B%22sgl%22%2C%22acc%22%2C%22sys%22%2C%22fc%22%5D%2C%22vtype%22%3A%22standard%22%7D%2C%22stake_inc%22%3Anull%2C%22ew_opt%22%3A%7B%7D%2C%22qb_stake%22%3A5000%2C%22stakes%22%3A%7B%7D%7D; GN_KIOSK=; _ga_3WYELKH4S2=GS1.1.1738768893.10.1.1738769021.35.0.0; cto_bundle=8D4PqV85ZWZkSmxvTnR1MmZqTUZJUHEwRkVzVEpWR21sa1liVlozMVZMZzRzeXRjOWtIWm1OWUp0TEpVTWh2Q3hCaUdKUWNsbk4lMkI3ZmdqejcwSEJqbkU5RDRrcGFsbiUyRlBaSHNrYmhmUnQ0b3JhNWQ3ekc1RGwxN3pkbUFSVWNwRkR2Qld4aFVmQVM3OUJQUnNmQzdBTDZvaUZNallpV0R4RmF0SjhvTUs3WWRhUEFPalRoVEIybEZxSjZicjZaYUZsdzQwRVBVS3p2MEhRMEslMkJxVWhlWFM3dkF3JTNEJTNE; GN_PUSH_METHOD=1; __cf_bm=3JyFnWE7x1ZEVJKFFnI8O8NapEJeOJpJGmaRq.aneYE-1738784164-1.0.1.1-sUP8prKJF7aERUkT2GueLMdn8BtB9jxy4YcumTUoar8N3kis4aj40X07li64OHPUILt2nPr2Mf1qKg1BM0x_pQ
pragma:no-cache
priority:u=1, i
referer:https://apuestas.wplay.co/es/e/24930939/Aguilas-Doradas-Rionegro-v-Independiente-Santa-Fe
sec-ch-ua:"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"
sec-ch-ua-mobile:?0
sec-ch-ua-platform:"Windows"
sec-fetch-dest:empty
sec-fetch-mode:cors
sec-fetch-site:same-origin
user-agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36
x-requested-with:XMLHttpRequest
"""
