from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder

from SkillboxProject.telegram_bot.model.types import HotelInfo


def choose_cities_keyboard(cities: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for city in cities:
        builder.add(InlineKeyboardButton(text=city['city_name'], callback_data=f'dest{city["destination_id"]}'))
    builder.adjust(1)
    return builder.as_markup()


def choose_search_type() -> InlineKeyboardMarkup:
    kb = [[InlineKeyboardButton(text='По Координатам', callback_data='search_by_cord')],
          [InlineKeyboardButton(text='По Городам', callback_data='search_by_city')],
          [InlineKeyboardButton(text='По текущей локации', callback_data='search_by_location')]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def choose_sort_type() -> InlineKeyboardMarkup:
    kb = [[InlineKeyboardButton(text='По Цене(по возрастанию)', callback_data='sort_to_high')],
          [InlineKeyboardButton(text='Самый дешевый', callback_data='sort_lowest')],
          [InlineKeyboardButton(text='Самый дорогой', callback_data='sort_highest')]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def make_hotel_page(data: dict) -> tuple[list, str]:
    index = data['scroll_index']
    try:
        current_hotel: HotelInfo = data['hotels'][index]
    except TypeError:
        raise IndexError('')
    else:
        photos = current_hotel.photos
        media_group = []
        total_quantity = len(data['hotels'])
        needtoknow = '\n\n'.join(current_hotel.needtoknow)
        caption = f"🏨Отель номер - <b>{index + 1} / {total_quantity}</b>\n\n     ✏️Название:  <b>{current_hotel.name}</b>\n     🚗Расстояние: <b>{current_hotel.destination.value} {current_hotel.destination.unit}</b>\n     ⚙️Координаты:\n          <b>Широта: {current_hotel.cord.latitude}\n          Долгота: {current_hotel.cord.longitude}</b>\n     💵Стоимость: <b>[{current_hotel.price.amount}] {current_hotel.price.amount * data['total_days']}{current_hotel.price.symbol} - {current_hotel.price.code}</b>\n     ⭐️Оценки:\n          <b>🏆Средняя оценка: {current_hotel.reviews.score}\n          👨‍👨‍👦Кол-во оценок: {current_hotel.reviews.total}</b>\n     📍Адрес: <b>{current_hotel.addres}</b>\n\n     <b>❗️Нужно знать: </b>\n{needtoknow}"
        for obj in photos[:10]:
            media_group.append(InputMediaPhoto(media=obj.url))
        return media_group, caption
