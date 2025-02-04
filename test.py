"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import requests

# URL del sitio protegido por Cloudflare
url = "https://www.rivalo.co/api/offer/v3/sports?live=false"

# Configuración de Selenium para evitar detección
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("start-maximized")  # Maximizar ventana
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# Iniciar el navegador
driver = webdriver.Chrome(options=options)
driver.get("https://www.rivalo.co/es/sportsbook")  # Página principal primero

# Esperar a que la página cargue completamente (importante para Cloudflare)
time.sleep(10)

# Desplazarse en la página para simular interacción humana
driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
time.sleep(5)
driver.find_element(By.TAG_NAME, "body").send_keys(Keys.HOME)

# Extraer cookies de Cloudflare
cookies = driver.get_cookies()
cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}

# Cerrar Selenium
driver.quit()

# **Paso 2: Hacer la solicitud con Requests usando las cookies obtenidas**
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Referer": "https://www.rivalo.co/es/sportsbook",
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "es-419,es;q=0.9",
}

# Hacer la solicitud con las cookies extraídas
session = requests.Session()
session.headers.update(headers)
session.cookies.update(cookies_dict)

response = session.get(url)

print("Código de respuesta:", response.status_code)
print("Contenido de la respuesta:", response.text)
"""

from selenium import webdriver

url = "https://www.rivalo.co/api/offer/v3/sports?live=false"

options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=options)
driver.get(url)

page_source = driver.page_source
print(page_source)

driver.quit()


headers = {
  'authority': 'www.rivalo.co',
  'method': 'GET',
  'path': '/api/offer/v3/sports?live=false',
  'scheme': 'https',
  'accept': 'application/json',
  'accept-encoding': 'gzip, deflate, br, zstd',
  'accept-language': 'es-419,es;q=0.9,ru;q=0.8',
  'cookie': 'locale=es; region=CO; _gcl_au=1.1.1895770473.1738544797; _ga=GA1.1.707374560.1738544797; _fbp=fb.1.1738544797503.225513204924537894; _clck=890g7d%7C2%7Cft4%7C0%7C1860; cf_clearance=nIgGvzyDoKCpWGA1uTYFYo8M0MIUxyjZ6CP4RMukMlk-1738546963-1.2.1.1-acVycxAIVoBj7emsiJCTG6zoU.xkMRmXnazNiLC3VJwU1jWwIhYgMyRlTa_aJo36ohWi1aoikN4uYnnAVGjDTSeNwDCavhsMsvrp5.73yE7P0RwmV50_CI_XFp31QKC0wBJVA63fQSZBT6t5zwlr1gPP7f25lPZKicmPP81r2qxb1z.UXLtJwAUAruhhP1_yYcMArY26vX3cQn9FEN37YZLW9HQe2c6tfBfJ3afDtLwAKO_hUpCCPZT7.Uytsqbtn61G76zCX6F7Ofwu_2mFcZJ91.1XZlW3jw41TapVkrM; ph_phc_A2xZKxCDfQF3toaNyFz1p572lBnwv5UyBLRrz14Jyjt_posthog=%7B%22distinct_id%22%3A%220193dd05-81e1-7928-900a-cc4cc6227fee%22%2C%22%24sesid%22%3A%5B1738546967256%2C%220194c979-72d8-7dd0-940d-6308aa128f73%22%2C1738546967256%5D%7D; _ga_J3HBC19ECW=GS1.1.1738544797.1.1.1738546976.47.0.0; _clsk=181y8me%7C1738546976919%7C2%7C1%7Co.clarity.ms%2Fcollect; cto_bundle=WYOrBl9wcUhmYk5UVHpDczlwUDQlMkJWUCUyQkZWQWNuNGVhdGNjMkNWcSUyRnY1eWRUTTU2THRWRVJRYWxvb2ZROXRqRkJXYklaNTBNdjNKTklEelpvMGFNZktmWjc5aFBmQTVnTTVjM3NHSTBVeFNXamg0RnQlMkZqcG5STUFodExlbUd2OGpwdzE3cUhSQzBrdTdUaWtZUFdaeW5tdU1xQSUzRCUzRA',
  'credentials': 'include',
  'priority': 'u=1, i',
  'referer': 'https://www.rivalo.co/es/sportsbook',
  'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
  'x-betr-brand': 'rivalo.co',
  'x-betr-operator': 'matchserv',
  'x-correlation-id': '642c028d-391c-4734-aa92-9b6d4870ca00',
  'x-locale': 'en',
  'x-request-id': 'd286036f-a313-46af-ace9-9a8b95579d25'
}

#session = requests.Session()
#session.headers.update(headers)
#
#response = session.get(url)
#print(response.status_code)
#print(response.text)


#response = requests.get(url, headers=headers)
#
#print(response.status_code)
#print(response.text)


"""
url = "https://www.rivalo.co/api/offer/v3/sports?live=false"

payload = {}
headers = {
  'authority': 'www.rivalo.co',
  'method': 'GET',
  'path': '/api/offer/v3/sports?live=false',
  'scheme': 'https',
  'accept': 'application/json',
  'accept-encoding': 'gzip, deflate, br, zstd',
  'accept-language': 'es-419,es;q=0.9,ru;q=0.8',
  'cookie': 'locale=es; region=CO; _gcl_au=1.1.294506380.1734579943; _ga=GA1.1.1714769973.1734579943; _fbp=fb.1.1734579943413.931140666779587986; _clck=endxfn%7C2%7Cft4%7C0%7C1814; cf_clearance=BXWalbGBvv7odZzFA_DoANxYrhe.Cr3wMH3y1m0Un_g-1738543149-1.2.1.1-n0gA7xAF.4Yd1rtb4CFZysJfxOyRiIWMJmTV7Udv.i1DGPhfhDZXKC4RE0dWttkwQLqrWwvw0jExz4V9zuC6FbeWvJ_D_wJpLFzoZAQYzRTcY8Rv_WMfLnNdC4QrJKaDN80_w298cEwz3kBVtWr8P0xAqNS53gy0i2jfUzrXGkD0_eVwhUtQ9ISscv2ZYn3tz2O4fEqrq2cZ6u9vVv82ObrrycuOAcA0tna0zl8RVZ3ZD6JSU7Cmtq1iY8C0GJUYZeJG6qwLcWPqXIczJgBG_UJP4ZO3d168mx5O71ljwKA; ph_phc_A2xZKxCDfQF3toaNyFz1p572lBnwv5UyBLRrz14Jyjt_posthog=%7B%22distinct_id%22%3A%220193dd05-81e1-7928-900a-cc4cc6227fee%22%2C%22%24sesid%22%3A%5B1738543152742%2C%220194c92f-48c4-7055-986e-667387b1e4b3%22%2C1738542106820%5D%7D; _ga_J3HBC19ECW=GS1.1.1738542104.16.1.1738543194.15.0.0; cto_bundle=dW-FB19wcUhmYk5UVHpDczlwUDQlMkJWUCUyQkZWRUUydXZncWN6clQ4bW9EZ1I3S3RMa0FxQllLcGVveCUyRk0lMkY2RDJSOHFkS0x5SEVWOHdHd0VwRVJyeU5xMzZGdm5KQ3pjamJYSThHQlhXT2hxRXB4WEglMkIlMkY0RDljS0NST3ZERk9GJTJGMVdxRDlaVUl6SGlvNTFTSFR5N1pabDdrbnVQQSUzRCUzRA; _clsk=2v2dwf%7C1738543195118%7C2%7C1%7Co.clarity.ms%2Fcollect',
  'credentials': 'include',
  'priority': 'u=1, i',
  'referer': 'https://www.rivalo.co/es/sportsbook',
  'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
  'x-betr-brand': 'rivalo.co',
  'x-betr-operator': 'matchserv',
  'x-correlation-id': '642c028d-391c-4734-aa92-9b6d4870ca00',
  'x-locale': 'en',
  'x-request-id': 'd286036f-a313-46af-ace9-9a8b95579d25'
}
"""
#response = requests.request("GET", url, headers=headers, data=payload)
#response = requests.get(url, headers=headers, data=payload)
#print(response.status_code)
#texto = response.text
#print(texto)
"""
H�����~�Ng^     T��]��l�X!�Hڐ0I�v������q�ı5�g�����h���IAe���P��*à���۟���Ӡ�4�z���o��D�|���5]�Y�gYǯ4���)?��,����8�,_v��ǋ�^�ץ���'\qN�R��P�/�����a�d�v�迍���p���mTk�'{k�u�5e'|�X��1I����L{S�2~��}�␦��i�T����b���u�`x
�]X���v��+�xR穭�D*��JO�o7�mA�;��ۛ�r|�W�d*��N�!��YM��lA�Ⱥqj�������4b*7�$��*^>�l*���"؇�Z��EvT��tn���!��6���|*K��+=y�8�H2�Ea`+<�o�Q

=ڿTY���\�1��;�-�;�B�'�iسy\�$O.I!�
��VR2��:i�ł�"[����0�r�A4P�8t�_eAFD��yY�ˀ��`H�W9�b,.����=n���D�����@��(]@Y�m�o5���Xt3B���hّPF[b�g��~��۠���yH-&�
L%3%ޤ��BQ*e85�ni�����6��[��@!�^o�q�tU-�
zd��/�-���a���D6t.Z�
�߱��0�!h"�-[n�W
�ᱚF��p�N:������k�2~H�ɞ�E�q瘦�J<9�Ew,�����n/��߻�[��s���7~xP�jkV/a��Ǵ���Ŵ]A�q�����7�7���1�i1��(g������M�VY��}�  3&~eR�^�V�I�
����3�����(0��
�I�6�?FG����v��4�#%/E��B[�WpC�E�1>|��^XϮ^4��D�b2�-�.�u}fm~O��-e�k),^B9L����2�1z,�;~�
�ȓ��("v�cm�N�
(t�®1��i�����t� VHݛ�-֐�
>�=^>���}h�¯�E�"�|� �tMH���]U91+@���;~|:�Y�w��1�|6E��Þ��������Mt�t����~�4l���o/ƃ3Z=9S�X�V^���t�Yw@y��)�G���\G��y��a�~�7|�jFg�8���h
Ӹ&x��)��fڅԣfcL���z�%�\
0��ш�z��n����\q����U�!��z���%a���N���Տ���28�%a:�TMhA����g����8;.NΪ�-�`��^>�0jZ�2���1e�5��:���{Y���a]W�z��b�|2��v�,��pt���4�6�*mW<zK�V-���S���}W�j��'tqo��oRe��Vx4�hKܹ\,˰$
��lF#&��y�Cdڢ���p��-�d�p�|,��D�5oK0{    �^6��nk�Gӿ�!�[�!�ވ[vK�~΁F#�������*?�d�D��;�Sк�K�����l�CX�p��Qw���Ԇ��]V���΢���L������T�8 @Cp��;���Dc��m��TՌ
����y�NÑ��Q�������K�Q`�n�<U��L:�������'_��_���|�{����퓇Uz(3�
_9|$R���(��U�ӏ
9����:�I/�-�CZva��k�    �濧�.;���l�-���A�Y��S{-޹�fg0Y�JQ��t�Jэ~����U:�7���n����6�F'UC�]���h��-UZ�8���8���'�6K�J�UzTe~wr��%�@�m6��.��N�%L�a%�����N��
�͍��4�-eM^Rv��Q��h,�<?�D␦gM&

"""
# convertir respuesta a texto ya que se encuentra en binario
#texto = texto.encode('utf-8')
#print(texto)

