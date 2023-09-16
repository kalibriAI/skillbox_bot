from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def scroll_hotel_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает и возвращает клавиатуру для пролистывания отелей.

    :return: Клавиатура для пролистывания отелей.
    :rtype: ReplyKeyboardMarkup
    """

    kb = [[KeyboardButton(text='<'), KeyboardButton(text='>')], [KeyboardButton(text='Выбрать✅')]]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите способ подачи"
    )
    return keyboard
