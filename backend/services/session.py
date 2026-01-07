"""Session management for bot users - tracks which player UUID they're acting as."""

from typing import Optional

# In-memory session store: telegram_id -> player_uuid
_sessions: dict[int, str] = {}


def get_active_uuid(telegram_id: int) -> Optional[str]:
    """Get the active player UUID for a Telegram user, or None if using default."""
    return _sessions.get(telegram_id)


def set_active_uuid(telegram_id: int, player_uuid: str) -> None:
    """Set the active player UUID for a Telegram user."""
    _sessions[telegram_id] = player_uuid.upper()


def clear_session(telegram_id: int) -> None:
    """Clear session - user will use their Telegram-linked account."""
    _sessions.pop(telegram_id, None)


def get_current_user(telegram_id: int, sheets_service):
    """Get the current active user for a Telegram user.

    Returns the switched-to user if session exists, otherwise Telegram-linked user.
    """
    active_uuid = get_active_uuid(telegram_id)
    if active_uuid:
        return sheets_service.get_user_by_uuid(active_uuid)
    return sheets_service.get_user_by_telegram_id(telegram_id)
