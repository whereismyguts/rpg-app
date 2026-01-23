from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.sheets import sheets_service

router = APIRouter()


class TransferRequest(BaseModel):
    from_uuid: str
    to_uuid: str
    amount: int


class TransferResponse(BaseModel):
    success: bool
    new_balance: int
    transferred: int
    to_name: str


@router.post("/send", response_model=TransferResponse)
async def send_money(request: TransferRequest):
    if request.amount <= 0:
        raise HTTPException(400, "Amount must be positive")

    from_uuid = request.from_uuid.upper()
    to_uuid = request.to_uuid.upper()

    if from_uuid == to_uuid:
        raise HTTPException(400, "Cannot send to yourself")

    sender = sheets_service.get_user_by_uuid(from_uuid)
    receiver = sheets_service.get_user_by_uuid(to_uuid)

    if not sender:
        raise HTTPException(404, "Sender not found")
    if not receiver:
        raise HTTPException(404, "Receiver not found")
    if sender["balance"] < request.amount:
        raise HTTPException(400, "Insufficient funds")

    # Execute transfer
    new_sender_balance = sender["balance"] - request.amount
    new_receiver_balance = receiver["balance"] + request.amount

    sheets_service.update_balance(from_uuid, new_sender_balance)
    sheets_service.update_balance(to_uuid, new_receiver_balance)

    return TransferResponse(
        success=True,
        new_balance=new_sender_balance,
        transferred=request.amount,
        to_name=receiver["name"],
    )
