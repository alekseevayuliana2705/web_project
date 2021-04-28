from io import BytesIO
import requests
from PIL import Image


def search(toponym_long, toponym_lat):
    address_ll = f"{toponym_long}, {toponym_lat}"
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "40d1649f-0493-4b70-98ba-98533de7710b"

    search_params = {
        "apikey": api_key,
        "text": "кафе",
        "lang": "ru_RU",
        "ll": address_ll,
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params)
    if not response:
        pass
    json_response = response.json()
    message_error = ''
    if 'error' in json_response:
        return False
    else:
        # Получаем первую найденную организацию.
        organization = json_response["features"][0]
        # Название организации.
        org_name = organization["properties"]["CompanyMetaData"]["name"]
        # Адрес организации.
        org_address = organization["properties"]["CompanyMetaData"]["address"]
        site = organization["properties"]["CompanyMetaData"]["url"]

        # Получаем координаты ответа.
        point = organization["geometry"]["coordinates"]
        org_point = "{0},{1}".format(point[0], point[1])
        delta = "0.005"

        # Собираем параметры для запроса к StaticMapsAPI:
        message_org = f'Название: {org_name}, Полный адрес: {org_address} Подробная информация на сайте: {site}'
        map_params = {
            # позиционируем карту центром на наш исходный адрес
            "ll": address_ll,
            "spn": ",".join([delta, delta]),
            "l": "map",
            # добавим точку, чтобы указать найденную аптеку
            "pt": "{0},pm2dgl".format(org_point)
        }
        print(message_org)
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        # ... и выполняем запрос
        response = requests.get(map_api_server, params=map_params)
        i = Image.open(BytesIO(
            response.content))
        i.convert("RGB").save("map_cafe.jpg")
        return True


toponym_to_find = input().strip()

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    # обработка ошибочной ситуации
    pass

# Преобразуем ответ в json-объект
json_response = response.json()
# Получаем первый топоним из ответа геокодера.
toponym = json_response["response"]["GeoObjectCollection"][
    "featureMember"][0]["GeoObject"]
# Координаты центра топонима:
toponym_coodrinates = toponym["Point"]["pos"]
# Долгота и широта:
toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

delta = "0.005"

# Собираем параметры для запроса к StaticMapsAPI:
map_params = {
    "ll": ",".join([toponym_longitude, toponym_lattitude]),
    "spn": ",".join([delta, delta]),
    "l": "map"
}

map_api_server = "http://static-maps.yandex.ru/1.x/"
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)
i = Image.open(BytesIO(
response.content))
i.convert("RGB").save("map_user.jpg")
if search(toponym_longitude, toponym_lattitude):
    message = "Отлично!"
else:
    message = 'Ошибка 403'