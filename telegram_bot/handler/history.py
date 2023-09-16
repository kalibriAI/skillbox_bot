import json
from pprint import pprint
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InputMediaPhoto
from asyncpg import Pool

from handler.user import show_result
from keyboard.default import scroll_hotel_keyboard
from keyboard.inline import make_hotel_page
from model.types import HotelInfo

hist_router = Router()


@hist_router.message(Command('history'))
async def history_cmd(message: Message, pool: Pool, state):
    async with pool.acquire() as con:
        hotels = await con.fetch('select data from hotels where owner = $1', int(message.from_user.id))

    for hotel in hotels[:10]:
        hotel: HotelInfo = HotelInfo(**json.loads(hotel['data']))
        needtoknow = '\n'.join(hotel.needtoknow)
        media_group = []
        caption = f"✏️Название:  <b>{hotel.name}</b>\n     🚗Расстояние: <b>{hotel.destination[1]} {hotel.destination[0]}</b>\n     ⚙️Координаты:\n          <b>Широта: {hotel.cord[0]}\n          Долгота: {hotel.cord[1]}</b>\n     💵Стоимость: <b>{hotel.price[0]} {hotel.price[2]} - {hotel.price[1]}</b>\n     ⭐️Оценки:\n          <b>🏆Средняя оценка: {hotel.reviews[0]}\n          👨‍👨‍👦Кол-во оценок: {hotel.reviews[1]}</b>\n     📍Адрес: <b>{hotel.addres}</b>\n\n     <b>❗️Нужно знать: </b>\n{needtoknow}"

        for obj in hotel.photos:
            media_group.append(InputMediaPhoto(media=obj[0]))

        await message.answer_media_group(media=media_group)
        await message.answer(text=caption)
