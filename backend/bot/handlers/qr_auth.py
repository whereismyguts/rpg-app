"""QR code authorization handler."""

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import StateFilter

from services.sheets import sheets_service
from services.qr_decoder import decode_qr_from_bytes
from services.session import login_user
from bot.keyboards import main_menu_keyboard

router = Router()


@router.message(F.photo, StateFilter(None))
async def handle_photo(message: Message, bot: Bot):
    """Handle photo messages - try to decode QR and login as that player."""
    # Get the largest photo
    photo = message.photo[-1]

    # Download photo
    file = await bot.get_file(photo.file_id)
    file_bytes = await bot.download_file(file.file_path)

    # Read bytes
    image_bytes = file_bytes.read()

    # Try to decode QR
    qr_data = decode_qr_from_bytes(image_bytes)

    if not qr_data:
        await message.answer(
            "QR CODE NOT DETECTED\n"
            "====================\n\n"
            "Could not find a valid QR code in the image.\n"
            "Please send a clear photo of the player's QR code."
        )
        return

    # Look up the player by UUID
    player_uuid = qr_data.strip().upper()
    user = sheets_service.get_user_by_uuid(player_uuid)

    if not user:
        await message.answer(
            "PLAYER NOT FOUND\n"
            "================\n\n"
            f"No player found with ID: {player_uuid}\n"
            "The QR code may be invalid or the player doesn't exist."
        )
        return

    # Login as this player
    login_user(message.from_user.id, player_uuid, sheets_service)

    await message.answer(
        f"LOGIN SUCCESSFUL\n"
        f"================\n\n"
        f"Welcome, {user['name']}!\n"
        f"Player ID: {user['player_uuid']}\n"
        f"Balance: {user['balance']} caps\n"
        f"Profession: {user.get('profession') or 'None'}\n"
        f"Band: {user.get('band') or 'None'}\n\n"
        f"Use /logout to sign out.",
        reply_markup=main_menu_keyboard()
    )
