ids = {"eventIds":[
          "f-QFVna7cEe0CZ2TQ3m_aeEw",
          "f-P-zFxKf9MEOPNP__JAU6Ag",
          "f-AijGlzyJ5UmAFfdocSrVRQ",
          "f-dmLrl7kkZ0CkEZPeR9vo4g",
          "f-VCPNtKR0DUeGJjJk5J-LzQ",
          "f-w1ZZjnA4xEO7Kb1Kg_iOxQ",
          "f-o-o0d2m6fE-w5WOO8ozbyQ",
          "f-H_61UF-ISkORdLSMbtkgBw",
          "f-CDV-JwgPPUGkK0k3EpXE6w",
          "f-MRAsau2sRUS3nA2jjl4zwA",
          "f-S_eonfP9mkCIoVf0BPml9Q",
          "f-foNM6dDBsUunp_kts705SQ",
          "f-Rngoyx2DXEaAT0zuK2VFUA",
          "f-dFTy_RZzbUy8DyYDTLZaeA",
          "f-Lz9uczOSX0WpiAByC3HZ4A",
          "f-Lt21_RX8LESrKwAxN8bGPA",
          "f-pjWHjUWAhkO6YBgGCBXisQ",
          "f-lq-Gvj9Ih0eOw7yzRMz-GA"
       ]}

# recorrer lista de ids y añadirla a una nueva variable json con el id como key
# y un diccionario vacio como value
lista_de_partidos = { id: {} for id in ids["eventIds"] }


#from betsson_co.scraping import obtener_apuestas, obtener_partidos
#import json
#
#import time
#categoryId=11
#competitionId=6134 # id de la liga
#eventPhase="Prematch"
##indicar que se va a cargar la lista de partidos 
#print("Cargando lista de partidos")
#response = obtener_partidos(categoryId,competitionId,eventPhase)
#print("Lista de partidos cargada")
##print(response)
## guardar response en un archivo json
#with open('obtener_partidos.json', 'w') as file:
#    json.dump(response, file)
#print("se guardo la lista de partidos en obtener_partidos.json")

#time.sleep(5)
#print("Cargando lista de apuestas")
#eventId = "f-S_eonfP9mkCIoVf0BPml9Q" # id de un partido 
##"https://www.betsson.co/api/sb/v1/widgets/view/v1?configurationKey=sportsbook.event.v2&eventId=f-S_eonfP9mkCIoVf0BPml9Q&excludedWidgetKeys=sportsbook.events-table-mini"
#response = obtener_apuestas(eventId) # Obtenemos las apuestas de un partido
#print("Lista de apuestas cargada")
#
## guardar response en un archivo json
#with open('obtener_apuestas.json', 'w') as file:
#    json.dump(response, file)
#
#print("se guardo la lista de apuestas en obtener_apuestas.json")
