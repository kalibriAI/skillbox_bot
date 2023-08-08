import requests
import json
from pprint import pprint
from colorama import Fore

from SkillboxProject.telegram_bot.keyboard.inline import choose_cities_keyboard
from SkillboxProject.telegram_bot.model.types import HotelInfo, HotelPhoto, Destination, Coordinates, Price, Reviews

LocationsV3Search = "https://hotels4.p.rapidapi.com/locations/v3/search"
PropertiesV2List = "https://hotels4.p.rapidapi.com/properties/v2/list"
PropertiesV2Details = "https://hotels4.p.rapidapi.com/properties/v2/detail"

headers = {
    "X-RapidAPI-Key": "2cce231b72msh85a89e1f3891c45p16902ajsnb46cbcd7a9e0",
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def create_hotel_info(hotel: dict) -> HotelInfo:
    hotel_detail = get_hotel_detail_request(hotel['id'])
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


def get_city_request(city_name: str):
    querystring = {"q": f"{city_name}", "locale": "ru_RU"}
    response = requests.get(LocationsV3Search, headers=headers, params=querystring).json()
    if response['sr']:
        cities = list()
        for dest in response['sr']:
            if dest['type'] in ('CITY', 'NEIGHBORHOOD', 'REGION', 'POI'):
                cities.append({'city_name': dest['regionNames']['fullName'],
                               'destination_id': dest['gaiaId'] if 'gaiaId' in dest.keys() else dest['hotelId']})
    else:
        raise PermissionError('К сожалению, такой город не найден. Напиши другой)')

    return choose_cities_keyboard(cities)


def get_hotels_request(hotel_data: dict):
    payload = {
        "currency": 'USD',
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
                "adults": 2
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 999999999,
        "sort": 'PRICE_LOW_TO_HIGH',
        "filters": {"price": {
            "max": 999999999,
            "min": 1
        }}
    }
    if 'region_id' in hotel_data:
        payload['destination'] = dict(regionId=hotel_data['region_id'])
    else:
        payload['destination'] = dict(
            coordinates=dict(latitude=hotel_data['latitude'], longitude=hotel_data['longitude']))

    if hotel_data['cmd'] in ['lowest', 'highest']:
        response = requests.post(PropertiesV2List, json=payload, headers=headers)
        print(Fore.GREEN + 'STATUS:', Fore.BLUE + f'{response.status_code}')
        response = response.json()
        match hotel_data['cmd']:
            case 'lowest':
                hotel = response['data']['propertySearch']['properties'][0]
                return [create_hotel_info(hotel)]
            case 'highest':
                hotel = response['data']['propertySearch']['properties'][-1]
                return [create_hotel_info(hotel)]
    else:
        payload['resultsSize'] = hotel_data['result_size'] if hotel_data['cmd'] == 'to_high' else 99999999
        payload['filters']['price']['max'] = hotel_data['max_price']
        payload['filters']['price']['min'] = hotel_data['min_price']
        response = requests.post(PropertiesV2List, json=payload, headers=headers)
        print(Fore.GREEN + 'STATUS:', Fore.BLUE + f'{response.status_code}')
        response = response.json()
        properties = response['data']['propertySearch']['properties']
        hotels = []
        match hotel_data['cmd']:
            case 'to_high':
                for hotel in properties:
                    hotels.append(create_hotel_info(hotel))
                return sorted(hotels, key=lambda x: x.price.amount, reverse=False)
            case 'to_low':
                try:
                    properties = properties[::-1][:hotel_data['result_size']]
                except IndexError:
                    properties = properties[::-1]
                    for hotel in properties:
                        hotels.append(create_hotel_info(hotel))
                    return sorted(hotels, key=lambda x: x.price.amount, reverse=True)
                else:
                    for hotel in properties:
                        hotels.append(create_hotel_info(hotel))
                    return sorted(hotels, key=lambda x: x.price.amount, reverse=True)



def get_hotel_detail_request(hotel_id: str) -> tuple[list[HotelPhoto], str, list]:
    payload = {
        "currency": "USD",
        "locale": "ru_RU",
        "propertyId": hotel_id
    }

    response = requests.post(PropertiesV2Details, json=payload, headers=headers).json()

    images_data = response['data']['propertyInfo']['propertyGallery']['images']
    images = []

    for image in images_data:
        images.append(HotelPhoto(url=image['image']['url'], description=image['image']['description']))

    addres = response['data']['propertyInfo']['summary']['location']['address']['addressLine']
    needtoknow = response['data']['propertyInfo']['summary']['policies']['needToKnow']['body']

    return images, addres, needtoknow
