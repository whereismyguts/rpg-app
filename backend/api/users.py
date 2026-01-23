from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional

from services.sheets import sheets_service
from services.qr import generate_qr_code, generate_qr_image

router = APIRouter()


class UserResponse(BaseModel):
    player_uuid: str
    name: str
    balance: int
    profession: str
    band: str


class AttributeItem(BaseModel):
    name: str
    display_name: str
    value: int
    max_value: int
    description: str


class StatsResponse(BaseModel):
    player_uuid: str
    name: str
    profession: str
    band: str
    attributes: list[AttributeItem]


class QRResponse(BaseModel):
    qr_base64: str


@router.get("/me", response_model=UserResponse)
async def get_current_user(player_uuid: str = Query(...)):
    user = sheets_service.get_user_by_uuid(player_uuid.upper())
    if not user:
        raise HTTPException(404, "User not found")

    return UserResponse(
        player_uuid=user["player_uuid"],
        name=user["name"],
        balance=user["balance"],
        profession=user.get("profession", ""),
        band=user.get("band", ""),
    )


@router.get("/stats", response_model=StatsResponse)
async def get_user_stats(player_uuid: str = Query(...)):
    stats = sheets_service.get_user_stats(player_uuid.upper())
    if not stats:
        raise HTTPException(404, "User not found")

    return StatsResponse(**stats)


@router.get("/qr")
async def get_user_qr(player_uuid: str = Query(...), format: str = Query("base64")):
    """Get QR code for player UUID."""
    user = sheets_service.get_user_by_uuid(player_uuid.upper())
    if not user:
        raise HTTPException(404, "User not found")

    if format == "image":
        image_bytes = generate_qr_image(player_uuid.upper())
        return Response(content=image_bytes, media_type="image/png")

    qr_base64 = generate_qr_code(player_uuid.upper())
    return QRResponse(qr_base64=qr_base64)


@router.get("/lookup", response_model=UserResponse)
async def lookup_user(player_uuid: str = Query(...)):
    """Look up a user by UUID (for transfers)."""
    user = sheets_service.get_user_by_uuid(player_uuid.upper())
    if not user:
        raise HTTPException(404, "User not found")

    return UserResponse(
        player_uuid=user["player_uuid"],
        name=user["name"],
        balance=0,  # Don't expose balance in lookup
        profession=user.get("profession", ""),
        band=user.get("band", ""),
    )
