from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.services.billing_service import BillingService
from src.routers.dependencies import get_current_user

router = APIRouter()


class DateRangeRequest(BaseModel):
    start_date: str
    end_date: str


class RetentionFilterRequest(DateRangeRequest):
    retention_type: Optional[str] = None
    provider_ruc: Optional[str] = None


@router.post("/sales")
def sales_report(request: DateRangeRequest, current_user: dict = Depends(get_current_user)):
    service = BillingService()
    service.current_user = current_user
    service.current_user_id = current_user["id"]
    report = service.db.get_sales_report(current_user["id"], request.start_date, request.end_date)
    return {"report": report}


@router.get("/inventory")
def inventory_report(current_user: dict = Depends(get_current_user)):
    service = BillingService()
    service.current_user = current_user
    service.current_user_id = current_user["id"]
    inventory = service.db.aggregate_inventory(current_user["id"])
    return {"inventory": inventory}


@router.post("/purchase-sales")
def purchase_sales_report(request: DateRangeRequest, current_user: dict = Depends(get_current_user)):
    service = BillingService()
    service.current_user = current_user
    service.current_user_id = current_user["id"]
    data = service.db.get_purchase_sales_report(current_user["id"], request.start_date, request.end_date)
    return data


@router.post("/retentions")
def retention_report(request: RetentionFilterRequest, current_user: dict = Depends(get_current_user)):
    service = BillingService()
    service.current_user = current_user
    service.current_user_id = current_user["id"]
    data = service.db.get_retention_report(
        current_user["id"], request.start_date, request.end_date, request.retention_type, request.provider_ruc
    )
    return data
