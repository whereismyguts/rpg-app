from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from services.sheets import sheets_service
from services.session import get_current_user

router = Router()


@router.message(Command("balance"))
async def cmd_balance(message: Message):
    user = get_current_user(message.from_user.id, sheets_service)
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
    user = get_current_user(callback.from_user.id, sheets_service)
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
