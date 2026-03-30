from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.services.billing_service import BillingService
from src.routers.dependencies import get_current_user

router = APIRouter()


class InvoiceCreateRequest(BaseModel):
    invoice_number: str
    document_type: Optional[str] = "invoice"


class InvoiceItemRequest(BaseModel):
    product_id: Optional[int] = None
    description: str
    quantity: int
    unit_price: float
    tax_rate: Optional[float] = 0.12


@router.get("")
def list_invoices(current_user: dict = Depends(get_current_user)):
    service = BillingService()
    service.current_user = current_user
    service.current_user_id = current_user["id"]
    invoices = service.db.get_all_invoices(current_user["id"])
    return {"invoices": invoices}


@router.post("")
def create_invoice(data: InvoiceCreateRequest, current_user: dict = Depends(get_current_user)):
    service = BillingService()
    service.current_user = current_user
    service.current_user_id = current_user["id"]
    invoice_id, message = service.create_invoice(data.invoice_number)
    if not invoice_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return {"success": True, "invoice_id": invoice_id, "message": message}


@router.get("/{invoice_id}")
def get_invoice(invoice_id: int, current_user: dict = Depends(get_current_user)):
    service = BillingService()
    service.current_user = current_user
    service.current_user_id = current_user["id"]
    invoice = service.db.get_invoice(invoice_id)
    if not invoice or invoice["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada")
    items = service.db.get_invoice_items(invoice_id)
    return {"invoice": invoice, "items": items}


@router.post("/{invoice_id}/items")
def add_invoice_item(
    invoice_id: int,
    data: InvoiceItemRequest,
    current_user: dict = Depends(get_current_user),
):
    service = BillingService()
    service.current_user = current_user
    service.current_user_id = current_user["id"]
    invoice = service.db.get_invoice(invoice_id)
    if not invoice or invoice["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada")

    success = service.db.add_invoice_item(
        invoice_id,
        data.product_id,
        data.description,
        data.quantity,
        data.unit_price,
        data.tax_rate,
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo añadir el item")
    return {"success": True, "message": "Item añadido"}
