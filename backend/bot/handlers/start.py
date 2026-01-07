from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from services.sheets import sheets_service
from services.session import get_current_user, is_logged_in
from bot.keyboards import webapp_keyboard, main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = get_current_user(message.from_user.id, sheets_service)

    if user:
        await message.answer(
            f"VAULT-TEC TERMINAL\n"
            f"==================\n\n"
            f"Logged in as: {user['name']}\n"
            f"Player ID: {user['player_uuid']}\n"
            f"Balance: {user['balance']} caps",
            reply_markup=main_menu_keyboard(),
        )
    else:
        await message.answer(
            f"VAULT-TEC TERMINAL\n"
            f"==================\n\n"
            f"Authentication required.\n\n"
            f"Options:\n"
            f"• Send a photo of your QR code\n"
            f"• Use /login <PLAYER_ID>\n\n"
            f"Example: /login TEST0001"
        )
