from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from src.services.billing_service import BillingService
from src.core.security import SecurityManager
from src.core.config import settings
from src.routers.dependencies import get_current_user

router = APIRouter()


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None
    ruc: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class UserProfileResponse(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    role: str
    ruc: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None


@router.get("/health")
def health_check():
    return {"status": "ok", "service": settings.app_name}


@router.post("/register")
def register(data: RegisterRequest):
    service = BillingService()
    success, message = service.register(
        data.username,
        data.password,
        data.email,
        data.ruc,
        role="user",
        company_name=data.company_name,
        phone=data.phone,
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return {"success": True, "message": message}


@router.post("/login")
def login(data: LoginRequest):
    service = BillingService()
    success, message = service.login(data.username, data.password)
    if not success:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = SecurityManager.create_access_token(
        data={"sub": data.username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": data.username,
        "role": service.current_user.get("role", "user"),
    }


@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    service = BillingService()
    success, message = service.login(form_data.username, form_data.password)
    if not success:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = SecurityManager.create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserProfileResponse)
def read_users_me(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user.get("username"),
        "email": current_user.get("email"),
        "role": current_user.get("role"),
        "ruc": current_user.get("ruc"),
        "company_name": current_user.get("company_name"),
        "phone": current_user.get("phone"),
    }
