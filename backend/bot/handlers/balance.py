from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from services.sheets import sheets_service

router = Router()


@router.message(Command("balance"))
async def cmd_balance(message: Message):
    user = sheets_service.get_user_by_telegram_id(message.from_user.id)
    if user:
        await message.answer(
            f"BALANCE\n"
            f"=======\n\n"
            f"{user['name']}\n"
            f"Caps: {user['balance']}"
        )
    else:
        await message.answer("Not registered. Use /start first.")


@router.callback_query(F.data == "menu_balance")
async def callback_balance(callback: CallbackQuery):
    user = sheets_service.get_user_by_telegram_id(callback.from_user.id)
    if user:
        await callback.message.answer(
            f"BALANCE\n"
            f"=======\n\n"
            f"{user['name']}\n"
            f"Caps: {user['balance']}"
        )
    else:
        await callback.message.answer("Not registered. Use /start first.")
    await callback.answer()
