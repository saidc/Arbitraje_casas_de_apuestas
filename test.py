from config import PROXIES
from bs4 import BeautifulSoup
import requests
import json
import time
import itertools
# Lista de proxies disponibles
#PROXIES = [
#    "91.235.158.209:7578:user253212:zs9cdf",
#    "91.235.158.131:7578:user253212:zs9cdf",
#    "91.235.158.177:7578:user253212:zs9cdf",
#    "91.235.158.176:7578:user253212:zs9cdf",
#    "91.235.158.237:7578:user253212:zs9cdf",
#    "91.235.158.149:7578:user253212:zs9cdf",
#    "91.235.158.210:7578:user253212:zs9cdf",
#    "91.235.158.129:7578:user253212:zs9cdf",
#    "91.235.158.3:7578:user253212:zs9cdf",
#    "91.235.158.90:7578:user253212:zs9cdf",
#]
print("PROXIES: ", PROXIES)

# Crear un iterador circular para rotar proxies
proxy_cycle = itertools.cycle(PROXIES)

def format_proxy(proxy):
    """Convierte una cadena IP:PORT:USER:PASSWORD en un diccionario de proxies"""
    ip, port, user, password = proxy.split(":")
    proxy_url = f"http://{user}:{password}@{ip}:{port}"
    return {"http": proxy_url, "https": proxy_url}

def get_next_proxy():
    """Devuelve el siguiente proxy de la lista."""
    proxy = next(proxy_cycle)
    return format_proxy(proxy)

def test_proxies():
    """Prueba cada proxy en la lista y muestra cuál funciona."""
    working_proxies = []
    for proxy in PROXIES:
        proxy_dict = format_proxy(proxy)
        try:
            print(f"Probando proxy: {proxy}")
            response = requests.get("http://httpbin.org/ip", proxies=proxy_dict, timeout=5)
            if response.status_code == 200:
                print(f"✅ Proxy funcional: {proxy}")
                working_proxies.append(proxy)
            else:
                print(f"❌ Proxy rechazado: {proxy}")
        except Exception as e:
            print(f"❌ Proxy fallido: {proxy} -> {e}")

    print(f"\nProxies funcionales: {working_proxies}")

def is_traffic_error(response_text):
    """Verifica si la respuesta contiene un mensaje de error de tráfico."""
    soup = BeautifulSoup(response_text, "html.parser")

    error_tags = soup.find_all("h2")
    for tag in error_tags:
        if "request could not be satisfied" in tag.text.lower():
            return True

    if "too much traffic" in soup.text.lower():
        return True

    return False

def make_get_request(url, headers, payload, max_retries=10, wait_time=10, min_interval=0.1):
    """
    Realiza una solicitud GET con proxies y reintentos en caso de errores por tráfico.
    :param url: URL de la solicitud
    :param headers: Headers de la solicitud
    :param payload: Datos de la solicitud
    :param max_retries: Número máximo de intentos en caso de error
    :param wait_time: Tiempo de espera entre intentos en segundos (incremental)
    :param min_interval: Tiempo mínimo de espera entre solicitudes para evitar bloqueos
    :return: Respuesta en formato JSON si tiene éxito, None si falla permanentemente
    """
    retries = 0
    proxy = get_next_proxy()

    while retries <= max_retries:
        time.sleep(min_interval)  # Espera mínima entre solicitudes
        try:
            response = requests.get(url, headers=headers, data=payload, proxies=proxy, timeout=10)
            
            if response.status_code == 200:
                return response.json()

            if is_traffic_error(response.text):
                print(f"Error {response.status_code} por tráfico. Cambiando de proxy y reintentando...")
                proxy = get_next_proxy()
                time.sleep(wait_time)
                wait_time *= 2  # Incremento exponencial del tiempo de espera
                retries += 1
                continue
            else:
                print(f"Error {response.status_code} desconocido: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión con proxy {proxy}: {e}\n")
            proxy = get_next_proxy()
            retries += 1
            continue

    print("Número máximo de intentos alcanzado. No se pudo obtener una respuesta válida.")
    return None

# 1. Prueba qué proxies funcionan
test_proxies()

# Ejemplo de uso
url = "https://www.betsson.co/api/sb/v1/widgets/events-table/v2?categoryIds=138&competitionIds=25676&eventPhase=Prematch&eventSortBy=StartDate" # https://www.betsson.co/api/sb/v1/widgets/events-table/v2?categoryIds=138&competitionIds=25676&eventPhase=Prematch&eventSortBy=StartDate
headers = {"User-Agent": "Mozilla/5.0"}

BETSSON_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'brandid': '2d543995-acff-41c1-bc73-9ec46bd70602',
    'cloudfront-viewer-country': 'CO',
    'marketcode': 'co',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

payload = {}

response = make_get_request(url, BETSSON_HEADERS, payload)
if response:
    print("Respuesta exitosa:", response)
else:
    print("No se pudo obtener una respuesta válida.")

"""
"""
