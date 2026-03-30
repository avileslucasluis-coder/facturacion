from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.services.billing_service import BillingService
from src.routers.dependencies import get_current_user

router = APIRouter()


class EmissionSheetRequest(BaseModel):
    establishment_code: str
    emission_point: str
    document_type: str
    start_number: int
    end_number: int
    sri_authorization_code: Optional[str] = None
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None


class DocumentNumberRequest(BaseModel):
    document_type: str


@router.post("/emission-sheets")
def create_emission_sheet(request: EmissionSheetRequest, current_user: dict = Depends(get_current_user)):
    billing_service = BillingService()
    billing_service.current_user = current_user
    billing_service.current_user_id = current_user["id"]
    sheet_id = billing_service.db.create_emission_sheet(
        current_user["id"],
        request.establishment_code,
        request.emission_point,
        request.document_type,
        request.start_number,
        request.end_number,
        request.sri_authorization_code,
        request.valid_from,
        request.valid_until,
    )
    if not sheet_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo crear hoja de emisión")
    return {"success": True, "sheet_id": sheet_id}


@router.get("/emission-sheets")
def list_emission_sheets(current_user: dict = Depends(get_current_user)):
    billing_service = BillingService()
    billing_service.current_user = current_user
    billing_service.current_user_id = current_user["id"]
    sheets = billing_service.db.get_emission_sheets(current_user["id"])
    return {"emission_sheets": sheets}


@router.post("/next-number")
def next_document_number(request: DocumentNumberRequest, current_user: dict = Depends(get_current_user)):
    billing_service = BillingService()
    billing_service.current_user = current_user
    billing_service.current_user_id = current_user["id"]
    next_number = billing_service.db.get_next_document_number(current_user["id"], request.document_type)
    if not next_number:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay números disponibles o no existe la hoja de emisión")
    return {"next_number": next_number}


@router.get("/placeholders")
def document_placeholders():
    return {
        "message": "Las funciones de generación de XML y solicitud de autorización SRI están preparadas como base técnica. Integra el servicio oficial del SRI aquí.",
        "status": "pending_integration",
    }
