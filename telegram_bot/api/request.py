from typing import Union

from colorama import Fore
import requests
from aiogram.types import InlineKeyboardMarkup

from keyboard.inline import choose_cities_keyboard
from model.types import HotelInfo, HotelPhoto, Destination, Coordinates, Price, Reviews

LocationsV3Search = "https://hotels4.p.rapidapi.com/locations/v3/search"
PropertiesV2List = "https://hotels4.p.rapidapi.com/properties/v2/list"
PropertiesV2Details = "https://hotels4.p.rapidapi.com/properties/v2/detail"
UrlForTest = "https://hotels4.p.rapidapi.com/v2/get-meta-data"

headers = {
    "X-RapidAPI-Key": '',
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def parse_properties(properties: list, headers_: dict):
    """
    Функция переобразует список отелей прямиком из АПИ в список состоящий из типов данных HotelInfo.

    :param properties: список отелей из апи запроса
    :type properties: list
    :param headers_: заголовки для конкретного юзера
    :type headers_: dict

    :return: список из типов данных HotelInfo содержащий информацию об отелях.
    :rtype: list
    """
    return [create_hotel_info(hotel, headers_) for hotel in properties]


def make_headers(api_key: str) -> dict:
    """
    Функция для создния заголовков под конкретного юзера

    :param api_key: АПИ ключ пользователя
    :type api_key: str

    :return: словарь с заголовками пользователя
    :rtype: dict
    """
    headers_ = headers
    headers_['X-RapidAPI-Key'] = api_key
    return headers_


def test_repuest(api_key: str):
    """
    Функция для проверки действительности ключа при регистрации пользователя

    :param api_key: АПИ ключ пользователя
    :type api_key: str

    :return: True - если ключ рабочий. False - если ключ не рабочий
    :rtype: bool
    """
    response = requests.get(UrlForTest, headers=make_headers(api_key))
    return True if response.status_code == 200 else False


def create_hotel_info(hotel: dict, headers_: dict) -> HotelInfo:
    """
    Функция для переоброзования данных об отеле в спец. объект

    :param hotel: данные об отеле
    :type hotel: dict

    :param headers_: заголовки для конкретного юзера
    :type headers_: dict

    :return: возвращает объект HotelInfo
    :rtype: HotelInfo
    """
    hotel_detail = get_hotel_detail_request(hotel['id'], headers_)
    hotel_info = HotelInfo(
        id=int(hotel['id']),
        name=hotel['name'],
        destination=Destination(unit=hotel['destinationInfo']['distanceFromDestination']['unit'],
                                value=hotel['destinationInfo']['distanceFromDestination']['value']),
        cord=Coordinates(latitude=hotel['mapMarker']['latLong']['latitude'],
                         longitude=hotel['mapMarker']['latLong']['longitude']),
        price=Price(amount=round(hotel['price']['lead']['amount']),
                    code=hotel['price']['lead']['currencyInfo']['code'],
                    symbol=hotel['price']['lead']['currencyInfo']['symbol']),
        reviews=Reviews(score=hotel['reviews']['score'], total=hotel['reviews']['total']),
        photos=hotel_detail[0],
        addres=hotel_detail[1],
        needtoknow=hotel_detail[2]
    )
    return hotel_info


def get_city_request(city_name: str, api_key: str) -> InlineKeyboardMarkup:
    """
    Функция для оточнения локации.

    :param city_name: название места введенного пользователем
    :type city_name: str

    :param api_key: АПИ ключ конкретного юзера
    :type api_key: str

    :return: возвращает клавиатуру с возможными вариантами локаций, для уточнения
    :rtype: InlineKeyboardMarkup
    """
    querystring = {"q": f"{city_name}", "locale": "ru_RU"}
    response = requests.get(LocationsV3Search, headers=make_headers(api_key), params=querystring).json()
    try:
        response['sr'][0]
    except IndexError:
        raise PermissionError('К сожалению, такой город не найден. Напиши другой)')
    else:
        cities = list()
        for dest in response['sr']:
            if dest['type'] in ('CITY', 'NEIGHBORHOOD', 'REGION', 'POI'):
                cities.append({'city_name': dest['regionNames']['fullName'],
                               'destination_id': dest['gaiaId'] if 'gaiaId' in dest.keys() else dest['hotelId']})

        return choose_cities_keyboard(cities)


def get_hotels_request(hotel_data: dict, key: str) -> Union[list[HotelInfo], HotelInfo]:
    """
    Основная функция для отправки запросов на получение отелей.

    :param hotel_data: данные введенные пользователем для посика отелей
    :type hotel_data: dict

    :param key: АПИ ключ конкретного юзера
    :type key: str

    :return: возвращает либо СПИСОК из типов данных HotelInfo, либо один объект - HotelInfo
    :rtype: Union[list[HotelInfo], HotelInfo]

    :raises ValueError: Если АПИ вернул некорректные данные, то вызывается это исключение и поиск отелей прекращается.
    """
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "checkInDate": {
            "day": hotel_data['check_in'].day,
            "month": hotel_data['check_in'].month,
            "year": hotel_data['check_in'].year
        },
        "checkOutDate": {
            "day": hotel_data['check_out'].day,
            "month": hotel_data['check_out'].month,
            "year": hotel_data['check_out'].year
        },
        "rooms": [
            {
                "adults": 2,
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 20000,
        "sort": "PRICE_LOW_TO_HIGH",
        "filters": {"price": {
            "max": 999999,
            "min": 1
        }}
    }
    headers_ = make_headers(key)
    if 'region_id' in hotel_data:
        payload['destination'] = dict(regionId=hotel_data['region_id'])
    else:
        payload['destination'] = dict(
            coordinates=dict(latitude=hotel_data['latitude'], longitude=hotel_data['longitude']))
    if hotel_data['cmd'] == 'to_high':
        payload['resultsSize'] = hotel_data['result_size']
        payload['filters']['price']['max'] = hotel_data['max_price']
        payload['filters']['price']['min'] = hotel_data['min_price']
    response = requests.post(PropertiesV2List, json=payload, headers=headers_)
    print(Fore.GREEN + 'STATUS:', Fore.BLUE + f'{response.status_code}')
    result = response.json()

    try:
        properties = result['data']['propertySearch']['properties']
    except (TypeError, KeyError):
        try:
            print(result['errors'][0]['extensions']['event']['message'])
        except (KeyError, TypeError):
            print('Какая то другая ошибка')
        raise ValueError('АПИ не вернул ожидаемое значение - список отелей')

    else:
        match hotel_data['cmd']:
            case 'to_high':
                hotels = parse_properties(properties, headers_)
                return sorted(hotels, key=lambda x: x.price.amount)
            case 'lowest':
                return [create_hotel_info(properties[0], headers_)]
            case 'highest':
                return [create_hotel_info(properties[-1], headers_)]


def get_hotel_detail_request(hotel_id: str, headers_: dict) -> tuple[list[HotelPhoto], str, list]:
    """
    Функция для получения подробной информации об отеле.

    :param hotel_id: айди отеля
    :type hotel_id: str

    :param headers_: заголовки конкретного юзера
    :type headers_: str

    :return: возвращает сет состощий из 10 фоток отеля, адреса отеля и информации "Need To Know"
    :rtype: tuple[list[HotelPhoto], str, list]

    """
    payload = {"currency": "USD", "locale": "ru_RU", "propertyId": hotel_id}
    response = requests.post(PropertiesV2Details, json=payload, headers=headers_)
    response = response.json()

    images_data = response['data']['propertyInfo']['propertyGallery']['images']
    images = [HotelPhoto(url=image['image']['url'], description=image['image']['description']) for image in images_data]

    addres = response['data']['propertyInfo']['summary']['location']['address']['addressLine']
    needtoknow = response['data']['propertyInfo']['summary']['policies']['needToKnow']['body']

    return images[:10], addres, needtoknow
