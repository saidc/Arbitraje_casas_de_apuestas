import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

Betsson = "Betsson"

betsson_config_file_path = "exploracion_manual\config_betsson.json"

betsson_partidos_Prematch_file_path = "exploracion_manual\partidos_Prematch.json"

EVENT_PHASE_PREMATCH = "Prematch"

LINK_CASA_DE_APUESTA = "https://www.betsson.co/"
APUESTAS_DEPORTIVAS = f"{LINK_CASA_DE_APUESTA}apuestas-deportivas/"

BETSSON_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'brandid': '2d543995-acff-41c1-bc73-9ec46bd70602',
    'cloudfront-viewer-country': 'CO',
    'marketcode': 'co',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

BETSSON_HEADERS_LIGAS = {
  'Brandid': '2d543995-acff-41c1-bc73-9ec46bd70602',
  'Marketcode': 'co',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

BETSSON_HEADERS_SCRAPING_DEPORTES = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.37'}


