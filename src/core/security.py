import re
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class SecurityManager:
    """Maneja la seguridad de la aplicación"""

    @staticmethod
    def hash_password(password: str) -> str:
        if not password or len(password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        try:
            return pwd_context.verify(password, password_hash)
        except Exception:
            return False

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.algorithm)

    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])
            username: Optional[str] = payload.get("sub")
            return username
        except JWTError:
            return None

    @staticmethod
    def generate_auth_token() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_ruc(ruc: str) -> bool:
        if not ruc or len(ruc) != 13:
            return False
        return ruc.isdigit()

    @staticmethod
    def validate_invoice_number(invoice_number: str) -> bool:
        pattern = r'^\d{3}-\d{3}-\d{9}$'
        return bool(re.match(pattern, invoice_number))

    @staticmethod
    def sanitize_input(input_str: str, max_length: int = 255) -> str:
        if not isinstance(input_str, str):
            raise ValueError("Input debe ser string")
        return input_str.strip()[:max_length]
