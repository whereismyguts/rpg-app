from aiogram.types import WebAppInfo, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.settings import settings


def webapp_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with WebApp button."""
    kb = InlineKeyboardBuilder()
    if settings.webapp_url:
        kb.button(
            text="[ OPEN TERMINAL ]",
            web_app=WebAppInfo(url=settings.webapp_url),
        )
    return kb.as_markup()


def transfer_confirm_keyboard(target_uuid: str, amount: float) -> InlineKeyboardMarkup:
    """Create confirmation keyboard for money transfer."""
    kb = InlineKeyboardBuilder()
    kb.button(text="CONFIRM", callback_data=f"transfer_confirm:{target_uuid}:{amount}")
    kb.button(text="CANCEL", callback_data="transfer_cancel")
    kb.adjust(2)
    return kb.as_markup()


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Create main menu keyboard."""
    kb = InlineKeyboardBuilder()
    kb.button(text="Balance", callback_data="menu_balance")
    kb.button(text="Stats", callback_data="menu_stats")
    kb.button(text="Send Caps", callback_data="menu_send")
    kb.adjust(3)

    if settings.webapp_url:
        kb.button(
            text="[ OPEN TERMINAL ]",
            web_app=WebAppInfo(url=settings.webapp_url),
        )

    return kb.as_markup()
