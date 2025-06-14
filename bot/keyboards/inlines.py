from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List
from bot.database.models import Tariff
from urllib.parse import quote


def make_referral_button(referral_link: str) -> InlineKeyboardMarkup:
    """
    Создает кнопку реферальной ссылки
    """
    keyboard_builder = InlineKeyboardBuilder()
    safe_link = quote(referral_link)
    keyboard_builder.button(
        text='📤 Поделиться',
        url=f'https://t.me/share/url?url={safe_link}'
    )
    return keyboard_builder.as_markup()


def make_tariff_buttons(tariffs: List[Tariff]) -> InlineKeyboardMarkup:
    """
    Создает кнопки для выбора тарифа из базы данных
    """
    keyboard_builder = InlineKeyboardBuilder()
    for tariff in tariffs:
        keyboard_builder.button(
            text=tariff.title,
            callback_data=str(tariff.id)
        )
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()
