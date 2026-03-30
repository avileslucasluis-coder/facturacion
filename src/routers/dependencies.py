from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from src.services.billing_service import BillingService
from src.core.security import SecurityManager
from typing import Optional


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def get_billing_service() -> BillingService:
    return BillingService()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    service: BillingService = Depends(get_billing_service)
):
    username = SecurityManager.verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    user = service.db.get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    service.current_user = user
    service.current_user_id = user['id']
    return user
