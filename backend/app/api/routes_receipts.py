from fastapi import APIRouter

from app.core.errors import AppError
from app.services.repository import get_repository

router = APIRouter()
SANDBOX = "Sandbox — simulated Visa Intelligent Commerce flow."


def _dump(receipt) -> dict:
    payload = receipt.model_dump(mode="json")
    payload["sandbox_label"] = SANDBOX
    return payload


@router.get("/api/receipts/{receipt_id}")
async def get_receipt(receipt_id: str) -> dict:
    receipt = await get_repository().get_receipt(receipt_id)
    if receipt is None:
        raise AppError("RECEIPT_NOT_FOUND", "Receipt not found.", status_code=404)
    return _dump(receipt)


@router.get("/api/public/receipts/{share_id}")
async def get_public_receipt(share_id: str) -> dict:
    receipt = await get_repository().get_receipt_by_share_id(share_id)
    if receipt is None:
        raise AppError("RECEIPT_NOT_FOUND", "Receipt not found.", status_code=404)
    return _dump(receipt)
