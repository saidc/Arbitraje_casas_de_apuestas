import os
import json
import requests
from dotenv import load_dotenv
from Betsson import autenticar, token_expirado, obtener_session_token, consultar_balance
from config import USUARIO, PASSWORD

# Validar si el archivo de credenciales existe
def cargar_credenciales():
    try:
        with open("credenciales.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Guardar credenciales actualizadas
def guardar_credenciales(credenciales):
    with open("credenciales.json", "w") as file:
        json.dump(credenciales, file, indent=4)


# Flujo principal
if __name__ == "__main__":
    try:
        # Cargar credenciales existentes
        credenciales = cargar_credenciales()

        # Revisar autenticación
        if "authenticationToken" not in credenciales:
            print(f"Autenticando usuario... {USUARIO} - {PASSWORD}")
            credenciales["authenticationToken"] = autenticar(USUARIO, PASSWORD)

        # Revisar sessionToken
        if "sessionToken" not in credenciales or token_expirado(credenciales.get("timeToLiveSeconds", 0)):
            print("Obteniendo sessionToken...")
            session_token, tiempo_vida = obtener_session_token(credenciales["authenticationToken"])
            credenciales["sessionToken"] = session_token
            credenciales["timeToLiveSeconds"] = tiempo_vida
        
        # Guardar credenciales actualizadas
        guardar_credenciales(credenciales)

        # Verificar balance con el sessionToken
        balance = consultar_balance(credenciales["sessionToken"])
        print(f"Balance: {balance}")

    except Exception as e:
        print(f"Error: {e}")