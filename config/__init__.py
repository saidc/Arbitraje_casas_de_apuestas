import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# obtener lista de proxies desde el archivo .env
PROXIES = os.getenv("PROXIES").split(",")

casas_de_apuestas_path = "casas_de_apuestas\casas_de_apuestas.json"
partidos_jugados_path = "casas_de_apuestas\partidos_jugados.json"
catalogo_de_deportes_path = "casas_de_apuestas\catalogo_de_deportes.json"

# dado un listado de nombres crear variables con un valor string vacio con los nombres del listado 
def create_empty_string_variables(list_of_names):
    for name in list_of_names:
        globals()[name["name"]] = name["value"]