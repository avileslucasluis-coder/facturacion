from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.services.ai_service import AIService
from src.services.billing_service import BillingService
from src.routers.dependencies import get_current_user

router = APIRouter()

a = AIService()


class AnalyzeInvoiceRequest(BaseModel):
    invoice_id: int


class SuggestPriceRequest(BaseModel):
    product_name: str


class DateRangeRequest(BaseModel):
    start_date: str
    end_date: str


@router.post("/analyze-invoice")
def analyze_invoice(request: AnalyzeInvoiceRequest, current_user: dict = Depends(get_current_user)):
    billing_service = BillingService()
    billing_service.current_user = current_user
    billing_service.current_user_id = current_user["id"]
    invoice = billing_service.db.get_invoice(request.invoice_id)
    if not invoice or invoice["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    items = billing_service.db.get_invoice_items(request.invoice_id)
    result = a.analyze_invoice({"invoice": invoice, "items": items})
    return {"analysis": result}


@router.post("/suggest-price")
def suggest_price(request: SuggestPriceRequest, current_user: dict = Depends(get_current_user)):
    result = a.suggest_product_price(request.product_name)
    return {"suggestion": result}


@router.post("/sales-insights")
def sales_insights(request: DateRangeRequest, current_user: dict = Depends(get_current_user)):
    billing_service = BillingService()
    billing_service.current_user = current_user
    billing_service.current_user_id = current_user["id"]
    sales = billing_service.db.get_all_invoices(current_user["id"])
    sales = [sale for sale in sales if request.start_date <= sale["date"] <= request.end_date]
    result = a.analyze_sales(sales)
    return {"insights": result}


@router.get("/status")
def ai_status():
    return {"available": a.is_available(), "openai_key": bool(a.api_key)}
