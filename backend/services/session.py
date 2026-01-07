"""Session management for bot users - tracks which player UUID they're logged in as."""

from typing import Optional

# In-memory session store: telegram_id -> player_uuid
_sessions: dict[int, str] = {}


def get_active_uuid(telegram_id: int) -> Optional[str]:
    """Get the logged-in player UUID for a Telegram user, or None if not logged in."""
    return _sessions.get(telegram_id)


def set_active_uuid(telegram_id: int, player_uuid: str) -> None:
    """Set the logged-in player UUID for a Telegram user."""
    _sessions[telegram_id] = player_uuid.upper()


def clear_session(telegram_id: int) -> None:
    """Clear session - user must login again."""
    _sessions.pop(telegram_id, None)


def is_logged_in(telegram_id: int) -> bool:
    """Check if user is logged in."""
    return telegram_id in _sessions


def get_current_user(telegram_id: int, sheets_service):
    """Get the current logged-in user for a Telegram user.

    Returns the user if logged in, otherwise None.
    """
    active_uuid = get_active_uuid(telegram_id)
    if active_uuid:
        return sheets_service.get_user_by_uuid(active_uuid)
    return None
