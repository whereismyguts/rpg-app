from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.sheets import sheets_service
from services.session import get_current_user
from bot.keyboards import transfer_confirm_keyboard

router = Router()

NOT_LOGGED_IN = "Not logged in. Use /login <PLAYER_ID> or send a QR code photo."


class TransferState(StatesGroup):
    waiting_for_uuid = State()
    waiting_for_amount = State()


@router.message(Command("send"))
async def cmd_send(message: Message, state: FSMContext, command: CommandObject):
    user = get_current_user(message.from_user.id, sheets_service)
    if not user:
        await message.answer(NOT_LOGGED_IN)
        return

    # Check if command has arguments: /send UUID amount
    if command.args:
        args = command.args.split()
        if len(args) >= 2:
            target_uuid = args[0].upper()
            try:
                amount = float(args[1])
                # Direct transfer with confirmation
                target = sheets_service.get_user_by_uuid(target_uuid)
                if not target:
                    await message.answer(f"ERROR: Player {target_uuid} not found.")
                    return
                if target_uuid == user["player_uuid"]:
                    await message.answer("ERROR: Cannot send caps to yourself.")
                    return
                if amount <= 0:
                    await message.answer("ERROR: Amount must be positive.")
                    return
                if user["balance"] < amount:
                    await message.answer(f"ERROR: Insufficient funds. Balance: {user['balance']} caps")
                    return

                await message.answer(
                    f"CONFIRM TRANSFER\n"
                    f"================\n\n"
                    f"To: {target['name']}\n"
                    f"Amount: {amount} caps\n\n"
                    f"Confirm?",
                    reply_markup=transfer_confirm_keyboard(target_uuid, amount),
                )
                return
            except ValueError:
                await message.answer("ERROR: Invalid amount. Use: /send UUID amount")
                return
        elif len(args) == 1:
            # Only UUID provided, ask for amount
            target_uuid = args[0].upper()
            target = sheets_service.get_user_by_uuid(target_uuid)
            if not target:
                await message.answer(f"ERROR: Player {target_uuid} not found.")
                return
            if target_uuid == user["player_uuid"]:
                await message.answer("ERROR: Cannot send caps to yourself.")
                return

            await state.update_data(target_uuid=target_uuid, target_name=target["name"])
            await state.set_state(TransferState.waiting_for_amount)
            await message.answer(
                f"Recipient: {target['name']}\n"
                f"Your balance: {user['balance']} caps\n\n"
                f"Enter amount to send:"
            )
            return

    await state.set_state(TransferState.waiting_for_uuid)
    await message.answer(
        "TRANSFER CAPS\n"
        "=============\n\n"
        "Enter recipient's Player ID:\n\n"
        "Or use: /send <UUID> <amount>"
    )


@router.callback_query(F.data == "menu_send")
async def callback_send(callback: CallbackQuery, state: FSMContext):
    user = get_current_user(callback.from_user.id, sheets_service)
    if not user:
        await callback.message.answer(NOT_LOGGED_IN)
        await callback.answer()
        return

    await state.set_state(TransferState.waiting_for_uuid)
    await callback.message.answer(
        "TRANSFER CAPS\n"
        "=============\n\n"
        "Enter recipient's Player ID:"
    )
    await callback.answer()


@router.message(TransferState.waiting_for_uuid)
async def process_uuid(message: Message, state: FSMContext):
    target_uuid = message.text.strip().upper()
    target_user = sheets_service.get_user_by_uuid(target_uuid)

    if not target_user:
        await message.answer(
            "ERROR: Player not found.\n"
            "Please enter a valid Player ID or /cancel"
        )
        return

    sender = get_current_user(message.from_user.id, sheets_service)
    if target_uuid == sender["player_uuid"]:
        await message.answer("ERROR: Cannot send caps to yourself.")
        return

    await state.update_data(target_uuid=target_uuid, target_name=target_user["name"])
    await state.set_state(TransferState.waiting_for_amount)
    await message.answer(
        f"Recipient: {target_user['name']}\n"
        f"Your balance: {sender['balance']} caps\n\n"
        f"Enter amount to send:"
    )


@router.message(TransferState.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except ValueError:
        await message.answer("ERROR: Invalid amount. Enter a number.")
        return

    sender = get_current_user(message.from_user.id, sheets_service)
    if sender["balance"] < amount:
        await message.answer(
            f"ERROR: Insufficient funds.\n"
            f"Your balance: {sender['balance']} caps"
        )
        return

    data = await state.get_data()
    await state.clear()

    await message.answer(
        f"CONFIRM TRANSFER\n"
        f"================\n\n"
        f"To: {data['target_name']}\n"
        f"Amount: {amount} caps\n\n"
        f"Confirm?",
        reply_markup=transfer_confirm_keyboard(data["target_uuid"], amount),
    )


@router.callback_query(F.data.startswith("transfer_confirm:"))
async def confirm_transfer(callback: CallbackQuery):
    parts = callback.data.split(":")
    target_uuid = parts[1]
    amount = float(parts[2])

    sender = get_current_user(callback.from_user.id, sheets_service)
    if not sender:
        await callback.message.edit_text("ERROR: User not found.")
        await callback.answer()
        return

    if sender["balance"] < amount:
        await callback.message.edit_text("ERROR: Insufficient funds.")
        await callback.answer()
        return

    target = sheets_service.get_user_by_uuid(target_uuid)
    if not target:
        await callback.message.edit_text("ERROR: Recipient not found.")
        await callback.answer()
        return

    # Execute transfer
    new_sender_balance = sender["balance"] - amount
    new_target_balance = target["balance"] + amount

    sheets_service.update_balance(sender["player_uuid"], new_sender_balance)
    sheets_service.update_balance(target_uuid, new_target_balance)

    await callback.message.edit_text(
        f"TRANSFER COMPLETE\n"
        f"=================\n\n"
        f"Sent {amount} caps to {target['name']}\n"
        f"New balance: {new_sender_balance} caps"
    )
    await callback.answer("Transfer successful!")


@router.callback_query(F.data == "transfer_cancel")
async def cancel_transfer(callback: CallbackQuery):
    await callback.message.edit_text("Transfer cancelled.")
    await callback.answer()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Operation cancelled.")
