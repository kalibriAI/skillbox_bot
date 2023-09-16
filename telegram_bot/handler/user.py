import asyncio
from pprint import pprint

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import datetime
from asyncio import sleep
from asyncpg import Pool
from typing import Union

from model.errors import HotelAlredyRememdered
from states.castom_machine import HotelSearchMachine
from api.request import get_city_request
from model.types import HotelInfo, CheckInOutDate
from api.request import get_hotels_request
from keyboard.inline import choose_sort_type, choose_search_type, make_hotel_page
from keyboard.default import scroll_hotel_keyboard
from service.bfuncs import make_total_days, insert_hotel
from const import *

user_router = Router()


@user_router.message(Command('search'), StateFilter(None))
async def search_cmd(message: Message, state: FSMContext):
    await message.answer(start_message, reply_markup=choose_search_type())
    await state.set_state(HotelSearchMachine.search_type)
    await state.set_state(HotelSearchMachine.search_type)


@user_router.message(Command('stop'), StateFilter('*'))
async def help_cmd(message: Message, state):
    await state.clear()
    await message.answer('Процесс прерван!')


@user_router.callback_query(HotelSearchMachine.search_type, F.data == 'search_by_cord')
async def search_by_cord_query(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(search_by_coordinates_message)
    await state.set_state(HotelSearchMachine.latitude)


@user_router.message(HotelSearchMachine.latitude)
async def input_latitude_cmd(message: Message, state: FSMContext):
    try:
        float(message.text)

    except ValueError:
        await message.answer('Введено неверное значение. Попробуйте еще раз!')

    else:
        if -90 < float(message.text) < 90:
            await message.answer('<b>✅Широта введена верно!</b>\n\n - Теперь нужно ввести <b>долготу</b>:')
            await state.update_data(latitude=float(message.text))
            await state.set_state(HotelSearchMachine.longitude)
            return


@user_router.message(HotelSearchMachine.longitude)
async def input_latitude_cmd(message: Message, state: FSMContext):
    try:
        float(message.text)

    except ValueError:
        await message.answer('Введено неверное значение. Попробуйте еще раз!')

    else:
        if -180 < float(message.text) < 180:
            await message.answer(location_got_succes_message)
            await state.update_data(longitude=float(message.text))
            await state.set_state(HotelSearchMachine.check_in)
            return


@user_router.callback_query(HotelSearchMachine.search_type, F.data == 'search_by_location')
async def search_by_location_query(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        '🔎<b>Выбран поиск по текущему местоположению.</b>\n\n - Теперь Вам нужно отправть вашу гео-локацию:')
    await state.set_state(HotelSearchMachine.location)


@user_router.message(HotelSearchMachine.location, F.location)
async def search_by_location_cmd(message: Message, state: FSMContext):
    await state.update_data(latitude=message.location.latitude, longitude=message.location.longitude)
    await message.answer(location_got_succes_message)
    await state.set_state(HotelSearchMachine.check_in)


@user_router.callback_query(HotelSearchMachine.search_type, F.data == 'search_by_city')
async def search_by_dest_query(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        '🔎<b>Выбран поиск по странам/городам.</b>\n\n - Введите название <b>города или страны</b> строго в формате: латинскими буквами на англ. языке.')
    await state.set_state(HotelSearchMachine.destination)


@user_router.message(HotelSearchMachine.destination)
async def search_by_dest_cmd(message: Message, pool):
    async with pool.acquire() as con:
        key = await con.fetchrow('select key from users where id = $1', message.from_user.id)
    city = message.text
    try:
        await message.answer('🔎📍Уточните местоположение: ', reply_markup=get_city_request(city, key['key']))
    except PermissionError as e:
        await message.answer(str(e))


@user_router.callback_query(F.data.startswith('dest'))
async def destination_callback_query(callback: CallbackQuery, state: FSMContext):
    region_id = callback.data.split('dest')[1]
    await state.update_data(region_id=region_id)
    await callback.message.answer(location_got_succes_message)
    await state.set_state(HotelSearchMachine.check_in)


@user_router.message(HotelSearchMachine.check_in)
async def set_check_in_cmd(message: Message, state: FSMContext):
    try:
        day, month, year = list(map(int, message.text.split('.')))

    except Exception as e:
        print(e)

    else:
        today_year, today_month, today_day = datetime.date.today().year, datetime.date.today().month, datetime.date.today().day
        if ((1 <= day <= 31) and (today_day <= day)) and ((1 <= month <= 12) and (today_month <= month)) and (
                today_year <= year):
            date = CheckInOutDate(day=day, month=month, year=year)
            await state.update_data(check_in=date)
            await message.answer(
                '✅<b>Дата заселения усешно сохранена</b>.\n\n - Теперь введите дату выселения из отеля, по тому же формату:')
            await state.set_state(HotelSearchMachine.check_out)
        else:
            msg = await message.answer('Указана неверная дата!')
            await asyncio.sleep(2)
            await msg.delete()
            await message.delete()


@user_router.message(HotelSearchMachine.check_out)
async def set_check_out_cmd(message: Message, state: FSMContext):
    try:
        day, month, year = list(map(int, message.text.split('.')))

    except Exception as e:
        print(e)

    else:
        data = await state.get_data()
        check_in = data['check_in']
        if ((1 <= day <= 31) and (day >= check_in.day)) and ((1 <= month <= 12) and (month >= check_in.month)) and (
                year >= check_in.year):
            date = CheckInOutDate(day=day, month=month, year=year)
            await state.update_data(check_out=date)
            await message.answer('✅Отлично, теперь вам нужно выбрать как отсортировать отели.',
                                 reply_markup=choose_sort_type())
            await state.set_state(HotelSearchMachine.sort)
        else:
            msg = await message.answer('Указана неверная дата!')
            await asyncio.sleep(2)
            await msg.delete()
            await message.delete()


@user_router.callback_query(F.data.startswith('sort'), HotelSearchMachine.sort)
async def set_sort_type_query(callback: CallbackQuery, state: FSMContext, pool):
    sort_type = callback.data.split('sort_')[1]
    if sort_type in ['lowest', 'highest']:
        await state.update_data(cmd=sort_type)
        await show_result(callback, state, pool)
    else:
        await state.update_data(cmd=sort_type)
        await callback.message.answer(
            '✅<b>Тип сортировки отелей сохранен.</b>\n\nТеперь нужно ввести кол-во отлей.\nПоиск выдаст столько вариантов отелей сколько вы введете, либо же если их будет меньше поиск покажет все. \n\n - Просто введите число:')
        await state.set_state(HotelSearchMachine.result_size)


@user_router.message(HotelSearchMachine.result_size)
async def set_result_size_cmd(message: Message, state: FSMContext):
    try:
        int(message.text)
    except ValueError:
        temp = await message.answer('Ведите число!')
        await asyncio.sleep(2)
        await temp.delete()
        await message.delete()
    else:
        if message.text.isdigit() and int(message.text) <= 30:
            await state.update_data(result_size=int(message.text))
            await message.answer(
                '✅<b>Вид сортировки выбран!</b>\n\n - Теперь введите диапазон цен вашего буджета.\n💵Для начала минимальная цена: ')
            await state.set_state(HotelSearchMachine.min_price)
        else:
            await message.answer(
                'За раз вы можете получить максимум 30 отелей, во избежание долгой загрузки и исчерпания лимита запросов.')


@user_router.message(HotelSearchMachine.min_price)
async def set_min_price_cmd(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(min_price=int(message.text))
        await message.answer('💎Теперь введите максимальную сумму вашего бюджета.')
        await state.set_state(HotelSearchMachine.max_price)


@user_router.message(HotelSearchMachine.max_price)
async def set_max_price_cmd(message: Message, state: FSMContext, pool: Pool):
    if message.text.isdigit():
        await state.update_data(max_price=int(message.text))
        await show_result(message, state, pool)


async def show_result(event: Union[Message, CallbackQuery], state: FSMContext, pool: Pool):
    async with pool.acquire() as con:
        api_key = await con.fetchrow('select key from users where id = $1', event.from_user.id)

    if isinstance(event, CallbackQuery):
        event = event.message

    await event.answer('✅<b>Ввод данных завершен. Ожидайте!</b>\n✉️Это может продолжаться до нескольких минут.')
    data = await state.get_data()
    try:
        hotels = get_hotels_request(data, api_key['key'])
    except ValueError as e:
        print('error - ', e)
        await event.answer(
            '<b>❗️Что то пошле не так. Поиск завершен❗️</b>\n\nВозможо:\n     • не верный ключ апи\n     • закончились запросы\n     • отелей не найдено\n     • по геолокации не найдено отелей!')
    else:
        total_days = make_total_days(data)
        await state.clear()
        await state.update_data(hotels=hotels, scroll_index=0, total_days=total_days)
        data = await state.get_data()
        page = make_hotel_page(data)
        await event.answer('✅<b>Данные успешно получены!</b>', reply_markup=scroll_hotel_keyboard())
        media_group = await event.answer_media_group(media=page[0])
        info = await event.answer(page[1])
        await state.update_data(current_hotel=(media_group, info))


@user_router.message(F.text == '<')
async def scroll_left_button(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    index = data['scroll_index']

    if index >= 1:
        try:
            await state.update_data(scroll_index=index - 1)
            data = await state.get_data()
            page = make_hotel_page(data)
            media_group = await message.answer_media_group(media=page[0])
            info = await message.answer(page[1])
            await state.update_data(current_hotel=(media_group, info))
        except IndexError:
            await state.update_data(scroll_index=index + 1)
            notify = await message.answer('Это первыя страница, вы не можете листать назад!')
            await sleep(2)
            await notify.delete()
        else:
            for msg in data['current_hotel'][0]:
                await msg.delete()
            await data['current_hotel'][1].delete()


@user_router.message(F.text == '>')
async def scroll_left_button(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    index = data['scroll_index']

    try:
        await state.update_data(scroll_index=index + 1)
        data = await state.get_data()

        page = make_hotel_page(data)
        media_group = await message.answer_media_group(media=page[0])
        info = await message.answer(page[1])
        await state.update_data(current_hotel=(media_group, info))
    except IndexError:
        await state.update_data(scroll_index=index - 1)
        notify = await message.answer('Это последняя страница, вы не можете листать вперед!')
        await sleep(2)
        await notify.delete()
    else:
        for msg in data['current_hotel'][0]:
            await msg.delete()
        await data['current_hotel'][1].delete()


@user_router.message(F.text == 'Выбрать✅')
async def choose_hotel_cmd(message: Message, state: FSMContext, pool: Pool):
    data = await state.get_data()
    hotels, index = data['hotels'], data['scroll_index']
    current_hotel: HotelInfo = data['hotels'][index]
    try:
        await insert_hotel(current_hotel, pool, message.from_user.id)
    except HotelAlredyRememdered as eroor:
        error_message = await message.answer(str(eroor))
        await asyncio.sleep(3)
        await error_message.delete()

    else:
        await message.answer(
            f'<b>Выбран отель - {hotels[index].name}</b>\nВы можете посмотреть историю выбранных отолей командой - <code>/history</code>',
            reply_markup=ReplyKeyboardRemove())
        for msg in data['current_hotel'][0]:
            await msg.delete()
        await data['current_hotel'][1].delete()

    finally:
        await message.delete()
