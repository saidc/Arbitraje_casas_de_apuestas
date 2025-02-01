import requests
import re
import base64
from bs4 import BeautifulSoup
import random
import concurrent.futures

PROXIES = [
    "91.235.158.209:7578:user253212:zs9cdf",
    "91.235.158.131:7578:user253212:zs9cdf",
    "91.235.158.177:7578:user253212:zs9cdf",
    "91.235.158.176:7578:user253212:zs9cdf",
    "91.235.158.237:7578:user253212:zs9cdf",
    "91.235.158.149:7578:user253212:zs9cdf",
    "91.235.158.210:7578:user253212:zs9cdf",
    "91.235.158.129:7578:user253212:zs9cdf",
    "91.235.158.3:7578:user253212:zs9cdf" ,
    "91.235.158.90:7578:user253212:zs9cdf",
]

def test_proxies2(https=False):
    """Prueba cada proxy en la lista y muestra cuál funciona."""
    working_proxies = []
    for proxy in PROXIES:
        proxy_dict = {"http": f"http://{proxy}", "https": f"https://{proxy}"} if https else {"http": f"http://{proxy}"}
        try:
            print(f"Probando proxy: {proxy}")
            url = "http://httpbin.org/ip"
            #response = requests.get("http://httpbin.org/ip", proxies=proxy_dict, timeout=5)
            response = requests.request(method="GET", url=url, proxies=proxy_dict, timeout=2)
            if response.status_code == 200:
                print(f"✅ Proxy funcional: {proxy}")
                working_proxies.append(proxy_dict)
            else:
                print(f"❌ Proxy rechazado: {proxy}")
        except Exception as e:
            print(f"❌ Proxy fallido: {proxy} -> {e}")

    print(f"\nProxies funcionales: {working_proxies}")
    return working_proxies

def test_proxy(proxy, https=False):
    """Prueba un solo proxy y devuelve si es funcional."""
    proxy_dict = {"http": f"http://{proxy}", "https": f"https://{proxy}"} if https else {"http": f"http://{proxy}"}
    try:
        print(f"Probando proxy: {proxy}")
        url = "http://httpbin.org/ip"
        response = requests.get(url, proxies=proxy_dict, timeout=10)
        if response.status_code == 200:
            print(f"✅ Proxy funcional: {proxy}")
            return proxy_dict  # Devuelve el proxy si es funcional
    except Exception as e:
        print(f"❌ Proxy fallido: {proxy} -> {e}")
    return None  # Devuelve None si el proxy falla

def test_proxies_concurrent(https=False, max_threads=4):
    """Ejecuta la prueba de proxies usando múltiples hilos para agilizar el proceso."""
    working_proxies = []

    # Usar ThreadPoolExecutor para paralelizar las pruebas
    with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
        futures = {executor.submit(test_proxy, proxy, https): proxy for proxy in PROXIES}

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                working_proxies.append(result)

    print(f"\n✅ Proxies funcionales: {working_proxies}")
    return working_proxies

#working_proxies = test_proxies(https=False)
# Ejecutar la prueba con concurrencia
working_proxies = test_proxies_concurrent(https=False, max_threads=8)

# URL del listado de proxies para Colombia
url = "http://free-proxy.cz/es/proxylist/country/CO/all/ping/all"

# Intentar obtener el contenido de la página con cada proxy hasta encontrar uno funcional
tryes = 0
max_tryes = 10
while tryes < max_tryes and len(working_proxies) > 0:
    payload = {}
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        'host': 'free-proxy.cz',
        'connection': 'keep-alive',
        'accept-encoding': 'gzip, deflate',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
    }
    # tomar un proxy de la lista de proxies funcionales de forma aleatoria usando random.choice
    proxy_dict = random.choice(working_proxies)
    print("proxy_dict: ",proxy_dict)
    try:
        #response = requests.get(url, headers=headers, data=payload, proxies=proxy_dict, timeout=5)
        response = requests.request(method="GET", url=url, headers=headers, data=payload, proxies=proxy_dict, timeout=12)

        print(response.status_code)
        if response.status_code == 200:
            print("✅ Proxy funcional: ", proxy_dict)
            print(response.text)
            break
        else:
            print(response.text)
    except Exception as e:
        print(f"❌ Proxy fallido: {proxy_dict} -> {e}")

    tryes += 1


## Parsear el contenido con BeautifulSoup
#soup = BeautifulSoup(response.text, "html.parser")
#
## Lista para almacenar los proxies extraídos
#proxies = []
#
## Buscar todas las etiquetas <script> que contienen las IPs codificadas en Base64
#for script in soup.find_all("script"):
#    match = re.search(r'Base64.decode\("([^"]+)"\)', script.text)
#    if match:
#        ip = base64.b64decode(match.group(1)).decode("utf-8")
#        # Buscar el puerto en la columna siguiente a la IP
#        port_tag = script.parent.find_next_sibling("td")
#        port = port_tag.text.strip() if port_tag else "N/A"
#        proxies.append(f"{ip}:{port}")
#
## Mostrar los proxies extraídos
#for proxy in proxies:
#    print(proxy)
