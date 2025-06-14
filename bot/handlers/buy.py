from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.database.session import get_session
from bot.database.crud.crud_user import get_or_create_user
from bot.utils.messages import buy_message
from bot.database.crud.crud_tariffs import get_active_tariffs
from bot.keyboards.inlines import make_tariff_buttons

async def buy_command(message: Message, state: FSMContext):
    async with get_session() as session:
        # Добавляем в БД
        user, new = await get_or_create_user(session, message.from_user)
        tariffs = await get_active_tariffs()

        await message.answer(
            text=buy_message,
            reply_markup=make_tariff_buttons(
                tariffs=tariffs
            )
        )
        await state.clear()
