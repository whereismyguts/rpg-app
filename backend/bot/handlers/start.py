from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from services.sheets import sheets_service
from bot.keyboards import webapp_keyboard, main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    user = sheets_service.get_user_by_telegram_id(user_id)

    if not user:
        # Register new user
        name = message.from_user.full_name
        user = sheets_service.create_user(user_id, name)
        await message.answer(
            f"VAULT-TEC INDUSTRIES\n"
            f"==================\n\n"
            f"Welcome, {name}!\n\n"
            f"Your Player ID: {user['player_uuid']}\n"
            f"Starting balance: {user['balance']} caps\n\n"
            f"Use /help for available commands.",
            reply_markup=main_menu_keyboard(),
        )
    else:
        await message.answer(
            f"VAULT-TEC TERMINAL\n"
            f"==================\n\n"
            f"Welcome back, {user['name']}!\n"
            f"Balance: {user['balance']} caps",
            reply_markup=main_menu_keyboard(),
        )
