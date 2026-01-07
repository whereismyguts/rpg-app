"""Switch account handlers."""

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from services.sheets import sheets_service
from services.session import set_active_uuid, clear_session, get_active_uuid
from bot.keyboards import main_menu_keyboard

router = Router()


@router.message(Command("switch"))
async def cmd_switch(message: Message, command: CommandObject):
    """Switch to a different player account by UUID."""
    if not command.args:
        await message.answer(
            "SWITCH ACCOUNT\n"
            "==============\n\n"
            "Usage: /switch <PLAYER_ID>\n\n"
            "Example: /switch TEST0002\n\n"
            "Use /myaccount to return to your own account."
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
        f"ACCOUNT SWITCHED\n"
        f"================\n\n"
        f"Now acting as: {target_user['name']}\n"
        f"Player ID: {target_user['player_uuid']}\n"
        f"Balance: {target_user['balance']} caps\n\n"
        f"Use /myaccount to return to your own account.",
        reply_markup=main_menu_keyboard()
    )


@router.message(Command("myaccount"))
async def cmd_myaccount(message: Message):
    """Return to own Telegram-linked account."""
    active_uuid = get_active_uuid(message.from_user.id)

    if not active_uuid:
        user = sheets_service.get_user_by_telegram_id(message.from_user.id)
        if user:
            await message.answer(
                f"You're already using your own account.\n\n"
                f"Name: {user['name']}\n"
                f"Player ID: {user['player_uuid']}\n"
                f"Balance: {user['balance']} caps",
                reply_markup=main_menu_keyboard()
            )
        else:
            await message.answer("Not registered. Use /start first.")
        return

    clear_session(message.from_user.id)

    user = sheets_service.get_user_by_telegram_id(message.from_user.id)
    if user:
        await message.answer(
            f"RETURNED TO OWN ACCOUNT\n"
            f"=======================\n\n"
            f"Name: {user['name']}\n"
            f"Player ID: {user['player_uuid']}\n"
            f"Balance: {user['balance']} caps",
            reply_markup=main_menu_keyboard()
        )
    else:
        await message.answer("Not registered. Use /start first.")
