from typing import NamedTuple


class Destination(NamedTuple):
    unit: str
    value: int


class Reviews(NamedTuple):
    score: int
    total: int


class HotelPhoto(NamedTuple):
    url: str
    description: str


class Coordinates(NamedTuple):
    latitude: int
    longitude: int


class PriceRange(NamedTuple):
    max: int
    min: int


class CheckInOutDate(NamedTuple):
    day: int
    month: int
    year: int


class Price(NamedTuple):
    amount: int
    code: str
    symbol: str


class HotelInfo(NamedTuple):
    id: int
    name: str
    destination: Destination
    cord: Coordinates
    price: Price
    reviews: Reviews
    photos: list[HotelPhoto]
    addres: str
    needtoknow: list
