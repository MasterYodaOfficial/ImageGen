from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.database.session import get_session
from bot.database.crud.crud_user import get_or_create_user, get_invited_count, get_total_referral_rewards
from bot.utils.messages import profile_message # balance, referral_count, referral_bonus, user_code, bot_name
from bot.keyboards.inlines import make_referral_button
from bot.utils.keys import BOT_NAME, DEFAULT_GIFT_TOKENS
from bot.logger import logger


async def profile_command(message: Message, state: FSMContext):

    logger.info(f"{message.from_user.id}, {message.from_user.first_name}")

    async with get_session() as session:
        user, new = await get_or_create_user(session, message.from_user)
        invited_count = await get_invited_count(session, user.referral_code) # тут количество приглашенных от данного пользователя
        total_referral_rewards = await get_total_referral_rewards(session, user.referral_code) # тут количество бонусов пользователя
        await message.answer(
            text=profile_message.format(
                balance=user.tokens,
                referral_count=invited_count,
                referral_bonus=total_referral_rewards,
                user_code=user.referral_code,
                bot_name=BOT_NAME,
                gift_tokens=DEFAULT_GIFT_TOKENS
            ),
            reply_markup=make_referral_button(
                referral_link=f"https://t.me/{BOT_NAME}?start={user.referral_code}"
            )
        )
        await state.clear()