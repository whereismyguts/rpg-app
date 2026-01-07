"""Session management - uses Google Sheets to track telegram_id -> player links."""

from typing import Optional


def login_user(telegram_id: int, player_uuid: str, sheets_service) -> bool:
    """Login: link telegram_id to player in Google Sheets."""
    return sheets_service.link_telegram_to_player(telegram_id, player_uuid)


def logout_user(telegram_id: int, sheets_service) -> bool:
    """Logout: unlink telegram_id from player in Google Sheets."""
    return sheets_service.unlink_telegram(telegram_id)


def get_current_user(telegram_id: int, sheets_service):
    """Get the current logged-in user for a Telegram user.

    Returns the user if logged in (telegram_id linked in sheet), otherwise None.
    """
    return sheets_service.get_user_by_telegram_id(telegram_id)


def is_logged_in(telegram_id: int, sheets_service) -> bool:
    """Check if user is logged in."""
    return get_current_user(telegram_id, sheets_service) is not None
