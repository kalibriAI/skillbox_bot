from colorama import Fore
import requests
from aiogram.types import InlineKeyboardMarkup
from pprint import pprint

from SkillboxProject.telegram_bot.keyboard.inline import choose_cities_keyboard
from SkillboxProject.telegram_bot.model.types import HotelInfo, HotelPhoto, Destination, Coordinates, Price, Reviews

LocationsV3Search = "https://hotels4.p.rapidapi.com/locations/v3/search"
PropertiesV2List = "https://hotels4.p.rapidapi.com/properties/v2/list"
PropertiesV2Details = "https://hotels4.p.rapidapi.com/properties/v2/detail"
UrlForTest = "https://hotels4.p.rapidapi.com/v2/get-meta-data"

headers = {
    "X-RapidAPI-Key": '',
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def parse_properties(properties: list, headers_):
    return [create_hotel_info(hotel, headers_) for hotel in properties]


def make_headers(api_key: str) -> dict:
    headers_ = headers
    headers_['X-RapidAPI-Key'] = api_key
    return headers_


def test_repuest(api_key: str):
    response = requests.get(UrlForTest, headers=make_headers(api_key))
    return True if response.status_code == 200 else False


def create_hotel_info(hotel: dict, headers_: dict) -> HotelInfo:
    hotel_detail = get_hotel_detail_request(hotel['id'], headers_)
    hotel_info = HotelInfo(
        id=hotel['id'],
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


def get_hotels_request(hotel_data: dict, key: str) -> list[HotelInfo]:
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
    finally:
        with open('log.json', 'w', encoding='utf-8') as file:
            file.write(response.text)


def get_hotel_detail_request(hotel_id: str, headers_: dict) -> tuple[list[HotelPhoto], str, list]:
    payload = {"currency": "USD", "locale": "ru_RU", "propertyId": hotel_id}
    response = requests.post(PropertiesV2Details, json=payload, headers=headers_)
    response = response.json()

    images_data = response['data']['propertyInfo']['propertyGallery']['images']
    images = [HotelPhoto(url=image['image']['url'], description=image['image']['description']) for image in images_data]

    addres = response['data']['propertyInfo']['summary']['location']['address']['addressLine']
    needtoknow = response['data']['propertyInfo']['summary']['policies']['needToKnow']['body']

    return images, addres, needtoknow
