import requests
from config import DEPORTES_DE_APUESTAS, LINK_CASA_DE_APUESTA, APUESTAS_DEPORTIVAS, USUARIO, PASSWORD
from datetime import datetime, timedelta

# Validar el tiempo de vida del token
def token_expirado(tiempo_vida_segundos):
    expiracion = datetime.now() + timedelta(seconds=tiempo_vida_segundos)
    return datetime.now() >= expiracion

# Simular un navegador en las solicitudes
def crear_headers(auth_token=None, session_token=None):
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "x-obg-channel": "Web",
        "x-obg-country-code": "CO",
        "x-obg-device": "Desktop",
    }
    if auth_token:
        headers["sessiontoken"] = auth_token
    if session_token:
        headers["sessiontoken"] = session_token
    return headers

# Obtener sessionToken
def obtener_session_token(auth_token):
    url = f"{LINK_CASA_DE_APUESTA}api/v1/single-sign-on-sessions/"
    payload = {
        "type": "up",
        "loginSource": "Web",
        "username": USUARIO,
        "password": PASSWORD,
        "shouldRememberUser": True,
    }
    headers = crear_headers(auth_token=auth_token)
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("sessionToken"), data.get("timeToLiveSeconds")
    else:
        raise Exception(f"Error al obtener sessionToken: {response.status_code}, {response.json()}")

# Autenticación para obtener tokens
def autenticar(username, password):
    
    url = f"{LINK_CASA_DE_APUESTA}api/v2/authentication-transaction"
    payload = {
        "authenticationType": "UsernamePassword",
        "username": username,
        "password": password,
    }
    headers = crear_headers()
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("authenticationToken")
    else:
        raise Exception(f"Error en autenticación: {response.status_code} - {response.json()}")    

# Consultar balance para verificar sessionToken
def consultar_balance(session_token):
    url = f"{LINK_CASA_DE_APUESTA}api/v2/wallet/balance/"
    headers = crear_headers(session_token=session_token)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["balance"]
    else:
        return {"error": "El sessionToken no es válido o ha expirado", "status": response.status_code, "response": response.json()}
