from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.services.billing_service import BillingService
from src.routers.dependencies import get_current_user

router = APIRouter()


class ProviderCreateRequest(BaseModel):
    name: str
    ruc: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


@router.get("")
def list_providers(current_user: dict = Depends(get_current_user)):
    service = BillingService()
    service.current_user = current_user
    service.current_user_id = current_user["id"]
    providers, message = service.list_providers()
    if providers is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message)
    return {"providers": providers}


@router.post("")
def add_provider(data: ProviderCreateRequest, current_user: dict = Depends(get_current_user)):
    service = BillingService()
    service.current_user = current_user
    service.current_user_id = current_user["id"]
    provider_id, message = service.add_provider(
        data.name,
        data.ruc,
        data.email,
        data.phone,
        data.address,
    )
    if not provider_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return {"success": True, "provider_id": provider_id, "message": message}
