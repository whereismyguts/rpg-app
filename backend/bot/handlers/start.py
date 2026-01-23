from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards import webapp_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "VAULT-TEC TERMINAL\n"
        "==================\n\n"
        "Press the button below to access your account.",
        reply_markup=webapp_keyboard()
    )
