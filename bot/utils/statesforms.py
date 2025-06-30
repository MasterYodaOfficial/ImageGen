from aiogram.fsm.state import StatesGroup, State


class StepForm(StatesGroup):
    """
    Машина состояний передвижения в меню
    """

    # Покупка тарифа
    COMMAND = State()
    CHOOSING_TARIFF = State()
    CHOOSING_PAYMENT_METHOD = State()
    CONFIRM_PURCHASE = State()

    # Генерация изображения
    CHOOSE_IMAGE_FORMAT = State()       # Выбор формата изображения
    CHOOSING_MODEL = State()            # Выбор модели для генерации
    ENTER_PROMPT = State()              # Ввод текстового описания (промта)
    CONFIRM_GENERATION = State()        # Подтверждение генерации или начать сначала

    # Для админской рассылки
    WAITING_BROADCAST_MESSAGE = State()
    CONFIRM_BROADCAST = State()

