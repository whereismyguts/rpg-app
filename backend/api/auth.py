from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import hashlib
import hmac
import urllib.parse

from config.settings import settings
from services.sheets import sheets_service

router = APIRouter()


class LoginRequest(BaseModel):
    init_data: Optional[str] = None  # Telegram WebApp initData (for future onboarding)
    player_uuid: Optional[str] = None  # UUID from QR code or manual input
    password: Optional[str] = None  # Optional password


class LoginResponse(BaseModel):
    player_uuid: str
    name: str
    balance: float
    profession: str
    band: str


def validate_webapp_data(init_data: str) -> Optional[dict]:
    """Validate Telegram WebApp initData."""
    try:
        parsed = dict(urllib.parse.parse_qsl(init_data))
        received_hash = parsed.pop("hash", None)

        if not received_hash:
            return None

        # Sort and create data check string
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(parsed.items())
        )

        # Create secret key
        secret_key = hmac.new(
            b"WebAppData",
            settings.bot_token.encode(),
            hashlib.sha256,
        ).digest()

        # Calculate hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        if calculated_hash == received_hash:
            return parsed
        return None
    except Exception:
        return None


def parse_user_from_init_data(parsed_data: dict) -> Optional[int]:
    """Extract user_id from parsed initData."""
    import json
    try:
        user_str = parsed_data.get("user")
        if user_str:
            user_data = json.loads(user_str)
            return user_data.get("id")
    except Exception:
        pass
    return None


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    user = None

    # Option 1: Telegram WebApp auth
    if request.init_data:
        parsed_data = validate_webapp_data(request.init_data)
        if not parsed_data:
            raise HTTPException(401, "Invalid WebApp signature")

        user_id = parse_user_from_init_data(parsed_data)
        if user_id:
            user = sheets_service.get_user_by_telegram_id(user_id)

    # Option 2: UUID-based login
    elif request.player_uuid:
        user = sheets_service.get_user_by_uuid(request.player_uuid.upper())

    if not user:
        raise HTTPException(404, "User not found")

    # Optional password check
    if settings.password_enabled:
        if not request.password or request.password != settings.app_password:
            raise HTTPException(401, "Invalid password")

    return LoginResponse(
        player_uuid=user["player_uuid"],
        name=user["name"],
        balance=user["balance"],
        profession=user.get("profession", ""),
        band=user.get("band", ""),
    )
