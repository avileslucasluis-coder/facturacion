from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.services.billing_service import BillingService
from src.routers.dependencies import get_current_user

router = APIRouter()


class ProductCreateRequest(BaseModel):
    name: str
    price: float
    tax_rate: Optional[float] = 0.12


@router.get("")
def list_products(current_user: dict = Depends(get_current_user)):
    service = BillingService()
    service.current_user = current_user
    service.current_user_id = current_user["id"]
    products, message = service.list_products()
    if products is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message)
    return {"products": products}


@router.post("")
def add_product(data: ProductCreateRequest, current_user: dict = Depends(get_current_user)):
    service = BillingService()
    service.current_user = current_user
    service.current_user_id = current_user["id"]
    product_id, message = service.add_product(data.name, data.price, data.tax_rate)
    if not product_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return {"success": True, "product_id": product_id, "message": message}


@router.get("/{product_id}")
def get_product(product_id: int, current_user: dict = Depends(get_current_user)):
    service = BillingService()
    service.current_user = current_user
    service.current_user_id = current_user["id"]
    products, _ = service.list_products()
    product = next((item for item in products if item.get("id") == product_id), None)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return {"product": product}
