import json
from config import ARCHIVO_FUTBOL, ARCHIVO_TENIS, ARCHIVO_TENIS_DE_MESA
# Validar si el archivo de un partido ya existe
def cargar_archivo_json(nombre_archivo):
    try:
        with open(nombre_archivo, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    
def obtener_partidos_de_futbol():
    return cargar_archivo_json(ARCHIVO_FUTBOL)

def obtener_partidos_de_tenis():
    return cargar_archivo_json(ARCHIVO_TENIS)

def obtener_partidos_de_tenis_de_mesa():
    return cargar_archivo_json(ARCHIVO_TENIS_DE_MESA)

