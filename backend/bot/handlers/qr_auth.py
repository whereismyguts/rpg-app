"""QR code authorization handler."""

from aiogram import Router, F, Bot
from aiogram.types import Message

from services.sheets import sheets_service
from services.qr_decoder import decode_qr_from_bytes
from bot.keyboards import main_menu_keyboard

router = Router()


@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot):
    """Handle photo messages - try to decode QR and authorize user."""
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
            "==================\n\n"
            "Could not find a valid QR code in the image.\n"
            "Please send a clear photo of the player's QR code."
        )
        return

    # Look up the player by UUID
    player_uuid = qr_data.strip().upper()
    target_user = sheets_service.get_user_by_uuid(player_uuid)

    if not target_user:
        await message.answer(
            "PLAYER NOT FOUND\n"
            "================\n\n"
            f"No player found with ID: {player_uuid}\n"
            "The QR code may be invalid or expired."
        )
        return

    # Check if sender is registered
    sender = sheets_service.get_user_by_telegram_id(message.from_user.id)

    if not sender:
        # Register sender first
        sender = sheets_service.create_user(
            message.from_user.id,
            message.from_user.full_name
        )
        await message.answer(
            f"REGISTERED AS NEW PLAYER\n"
            f"========================\n\n"
            f"Welcome, {sender['name']}!\n"
            f"Your ID: {sender['player_uuid']}\n"
            f"Balance: {sender['balance']} caps\n"
        )

    # Check if it's the same user
    if target_user['player_uuid'] == sender['player_uuid']:
        await message.answer(
            "YOUR PROFILE\n"
            "============\n\n"
            f"Name: {target_user['name']}\n"
            f"ID: {target_user['player_uuid']}\n"
            f"Balance: {target_user['balance']} caps\n"
            f"Profession: {target_user.get('profession') or 'None'}\n"
            f"Band: {target_user.get('band') or 'None'}",
            reply_markup=main_menu_keyboard()
        )
        return

    # Show target player info with send option
    await message.answer(
        "PLAYER FOUND\n"
        "============\n\n"
        f"Name: {target_user['name']}\n"
        f"ID: {target_user['player_uuid']}\n"
        f"Profession: {target_user.get('profession') or 'Unknown'}\n"
        f"Band: {target_user.get('band') or 'Unknown'}\n\n"
        f"To send caps, use:\n"
        f"/send {target_user['player_uuid']} <amount>\n\n"
        f"Example: /send {target_user['player_uuid']} 50"
    )
