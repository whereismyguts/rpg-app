from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config.settings import settings


def webapp_keyboard() -> ReplyKeyboardMarkup:
    """Create keyboard with WebApp button only."""
    kb = ReplyKeyboardBuilder()
    if settings.webapp_url:
        kb.button(text="[ OPEN TERMINAL ]", web_app=WebAppInfo(url=settings.webapp_url))
    return kb.as_markup(resize_keyboard=True, is_persistent=True)
