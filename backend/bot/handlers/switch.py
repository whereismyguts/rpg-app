"""Login/logout handlers."""

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from services.sheets import sheets_service
from services.session import set_active_uuid, clear_session, is_logged_in
from bot.keyboards import main_menu_keyboard

router = Router()


@router.message(Command("login"))
async def cmd_login(message: Message, command: CommandObject):
    """Login as a player by UUID."""
    if not command.args:
        await message.answer(
            "LOGIN\n"
            "=====\n\n"
            "Usage: /login <PLAYER_ID>\n\n"
            "Example: /login TEST0001\n\n"
            "Or send a photo of your QR code."
        )
        return

    target_uuid = command.args.strip().upper()
    target_user = sheets_service.get_user_by_uuid(target_uuid)

    if not target_user:
        await message.answer(
            f"ERROR: Player {target_uuid} not found.\n"
            "Please check the Player ID and try again."
        )
        return

    set_active_uuid(message.from_user.id, target_uuid)

    await message.answer(
        f"LOGIN SUCCESSFUL\n"
        f"================\n\n"
        f"Welcome, {target_user['name']}!\n"
        f"Player ID: {target_user['player_uuid']}\n"
        f"Balance: {target_user['balance']} caps\n\n"
        f"Use /logout to sign out.",
        reply_markup=main_menu_keyboard()
    )


@router.message(Command("logout"))
async def cmd_logout(message: Message):
    """Logout from current account."""
    if not is_logged_in(message.from_user.id):
        await message.answer(
            "You are not logged in.\n\n"
            "Use /login <PLAYER_ID> or send a QR code photo."
        )
        return

    clear_session(message.from_user.id)

    await message.answer(
        "LOGGED OUT\n"
        "==========\n\n"
        "You have been signed out.\n\n"
        "To login again:\n"
        "• Send a photo of your QR code\n"
        "• Use /login <PLAYER_ID>"
    )
