import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

betsson_config_file_path = "exploracion_manual\config_betsson.json"

betsson_partidos_Prematch_file_path = "exploracion_manual\partidos_Prematch.json"

EVENT_PHASE_PREMATCH = "Prematch"
# Variables de entorno
USUARIO = os.getenv("USUARIO")
PASSWORD = os.getenv("PASSWORD")

ARCHIVO_FUTBOL=os.getenv("ARCHIVO_FUTBOL")
ARCHIVO_TENIS=os.getenv("ARCHIVO_TENIS")
ARCHIVO_TENIS_DE_MESA=os.getenv("ARCHIVO_TENIS_DE_MESA")

LINK_CASA_DE_APUESTA = "https://www.betsson.co/"
APUESTAS_DEPORTIVAS = f"{LINK_CASA_DE_APUESTA}apuestas-deportivas/"

DEPORTES_DE_APUESTAS = {
    #"EN VIVO": {"ID": None, "LINK": f"{APUESTAS_DEPORTIVAS}apuestas-en-vivo", "DEPORTE": "EN VIVO"},
    "FUTBOL":  {"ID": 1, "LINK": f"{APUESTAS_DEPORTIVAS}futbol", "DEPORTE": "FUTBOL"},
    "TENIS":   {"ID": 11, "LINK": f"{APUESTAS_DEPORTIVAS}tenis", "DEPORTE": "TENIS"},
    "TENIS DE MESA": {"ID": 138, "LINK": f"{APUESTAS_DEPORTIVAS}tenis-de-mesa", "DEPORTE": "TENIS DE MESA"},
    "BASQUETBOL": {"ID": 4, "LINK": f"{APUESTAS_DEPORTIVAS}baloncesto", "DEPORTE": "BASQUETBOL"},
    "ESPORTS": {"ID": 119, "LINK": f"{APUESTAS_DEPORTIVAS}esports", "DEPORTE": "ESPORTS"},
    "VOLEY":   {"ID": 9, "LINK": f"{APUESTAS_DEPORTIVAS}voley", "DEPORTE": "VOLEY"},
    "FUTBOL AMERICANO": {"ID": 10, "LINK": f"{APUESTAS_DEPORTIVAS}futbol-americano", "DEPORTE": "FUTBOL AMERICANO"},
    "HOCKEY":  {"ID": 2, "LINK": f"{APUESTAS_DEPORTIVAS}hockey-sobre-hielo", "DEPORTE": "HOCKEY"},
    "MMA":     {"ID": 53, "LINK": f"{APUESTAS_DEPORTIVAS}artes-marciales-mixtas", "DEPORTE": "MMA"},
    "BEISBOL": {"ID": 19, "LINK": f"{APUESTAS_DEPORTIVAS}beisbol", "DEPORTE": "BEISBOL"},
}

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