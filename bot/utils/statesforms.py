from aiogram.fsm.state import StatesGroup, State


class StepForm(StatesGroup):
    """
    Машина состояний передвижения в меню
    """
    COMMAND = State()
    CHOOSING_TARIFF = State()
    CHOOSING_PAYMENT_METHOD = State()
    CONFIRM_PURCHASE = State()