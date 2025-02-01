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
    "91.235.158.3:7578:user253212:zs9cdf",
    "91.235.158.90:7578:user253212:zs9cdf",
]
url = "https://www.betsson.co/api/sb/v1/widgets/events-table/v2?categoryIds=138&competitionIds=25676&eventPhase=Prematch&eventSortBy=StartDate" 
BETSSON_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'brandid': '2d543995-acff-41c1-bc73-9ec46bd70602',
    'cloudfront-viewer-country': 'CO',
    'marketcode': 'co',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}
payload = {}

def corrimiento_izquierda(lista):
    if len(lista) > 1:
        return lista[1:] + [lista[0]]
    return lista  # Si la lista tiene 0 o 1 elementos, no hay cambio


def format_proxy(proxy):
    """Convierte una cadena IP:PORT:USER:PASSWORD en un diccionario de proxies"""
    ip, port, user, password = proxy.split(":")
    proxy_url = f"http://{user}:{password}@{ip}:{port}"
    return {"http": proxy_url, "https": proxy_url}


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


#test_proxies()
proxy_cycle = PROXIES.copy()
print(proxy_cycle)
proxy_cycle = corrimiento_izquierda(proxy_cycle)
print(proxy_cycle)