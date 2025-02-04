

# Obtener deportes en rivalo - prematch - Request Method: GET
HEADER = {
    "accept":'application/json',
    "credentials":'include',
    "referer":'https://www.rivalo.co/es/sportsbook',
    "sec-ch-ua":'"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    "sec-ch-ua-mobile":'?0',
    "sec-ch-ua-platform":'"Windows"',
    "user-agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    "x-betr-brand":'rivalo.co',
    "x-betr-operator":'matchserv',
    "x-correlation-id":'642c028d-391c-4734-aa92-9b6d4870ca00',
    "x-locale":'en',
    "x-request-id":'d286036f-a313-46af-ace9-9a8b95579d25',
    "referrer": "https://www.rivalo.co/es/sportsbook",
    "mode": "cors",
}

URL = "https://www.rivalo.co/api/offer/v3/sports?live=false"

"""
fetch("https://www.rivalo.co/api/offer/v3/sports?live=false", {
  "headers": {
    "accept": "application/json",
    "credentials": "include",
    "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "x-betr-brand": "rivalo.co",
    "x-betr-operator": "matchserv",
    "x-correlation-id": "642c028d-391c-4734-aa92-9b6d4870ca00",
    "x-locale": "en",
    "x-request-id": "d286036f-a313-46af-ace9-9a8b95579d25"
  },
  "referrer": "https://www.rivalo.co/es/sportsbook",
  "referrerPolicy": "strict-origin-when-cross-origin",
  "body": null,
  "method": "GET",
  "mode": "cors",
  "credentials": "omit"
});
"""
# convertir fetch de arriba a codigo de python con request
import requests
referrer = "https://www.rivalo.co/es/sportsbook"
# añadir referrer al request 
