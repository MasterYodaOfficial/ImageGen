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
            text=f"{tariff.title}, {tariff.price_rub} Руб.",
            callback_data=str(tariff.id)
        )
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()

def make_payment_buttons() -> InlineKeyboardMarkup:
    """Кнопки для выбора способа оплаты"""
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 ЮKassa", callback_data="yookassa")
    kb.button(text="🪙 Крипта", callback_data="crypto")
    kb.adjust(1)
    return kb.as_markup()

def make_pay_link_button(url: str = None) -> InlineKeyboardMarkup:
    """Кнопка оплатить"""
    kb = InlineKeyboardBuilder()
    if not url:
        kb.button(text="💳 Оплатить", callback_data='pay')
    else:
        kb.button(text="💳 Оплатить", url=url)
    return kb.as_markup()

def make_formate_buttons() -> InlineKeyboardMarkup:
    """Кнопка для выбора формата изображения"""
    kb = InlineKeyboardBuilder()
    kb.button(text="🧍 Вертикальный", callback_data="Вертикальный")
    kb.button(text="🌄 Горизонтальный", callback_data="Горизонтальный")
    kb.button(text="🔲 Квадратный", callback_data="Квадратный")
    kb.adjust(1)
    return kb.as_markup()

def continue_prompt_buttons() -> InlineKeyboardMarkup:
    """Кнопки для подтверждения генерации"""
    kb = InlineKeyboardBuilder()
    kb.button(text="Начать генерацию", callback_data="start_gen")
    kb.button(text="Начать заново", callback_data="restart_gen")
    kb.adjust(1)
    return kb.as_markup()