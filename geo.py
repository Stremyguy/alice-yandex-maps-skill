import requests
from math import sin, cos, sqrt, atan2, radians


def get_coordinates(city: str) -> list:
    url = "https://geocode-maps.yandex.ru/1.x/"

    params = {
        'geocode': city,
        'format': 'json',
        'apikey': "8013b162-6b42-4997-9691-77b7074026e0"
    }

    response = requests.get(url, params)
    json = response.json()
    point_str = json['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
    point_array = [float(x) for x in point_str.split(' ')]

    return point_array


def get_country(city: str) -> dict:
    url = "https://geocode-maps.yandex.ru/1.x/"

    params = {
        'geocode': city,
        'format': 'json',
        'apikey': "8013b162-6b42-4997-9691-77b7074026e0"
    }

    response = requests.get(url, params)
    json = response.json()

    return \
        json['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
            'GeocoderMetaData'][
            'AddressDetails']['Country']['CountryName']


def get_geo_info(city_name: str, type_info: str) -> list | dict | None:
    if type_info not in ["country", "coordinates"]:
        return
    
    url = "https://geocode-maps.yandex.ru/1.x/"

    params = {
        "geocode": city_name,
        "format": "json",
        "apikey": "8013b162-6b42-4997-9691-77b7074026e0"
    }
    
    response = requests.get(url, params)
    json = response.json()
    
    if type_info == "country":
        return \
        json["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
            "GeocoderMetaData"][
            "AddressDetails"]["Country"]["CountryName"]
    elif type_info == "coordinates":
        point_str = json["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        point_array = [float(x) for x in point_str.split()]

        return point_array


def get_distance(p1: float, p2: float) -> float:
    R = 6373.0

    lon1 = radians(p1[0])
    lat1 = radians(p1[1])
    lon2 = radians(p2[0])
    lat2 = radians(p2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance
