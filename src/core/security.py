import hashlib
import hmac
import secrets
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

# JWT settings
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'supersecretnotreally')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class SecurityManager:
    """Maneja la seguridad de la aplicación"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Genera un hash seguro de la contraseña"""
        if not password or len(password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")

        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${password_hash.hex()}"

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verifica una contraseña contra su hash"""
        try:
            salt, stored_hash = password_hash.split('$')
            computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return hmac.compare_digest(computed_hash.hex(), stored_hash)
        except Exception:
            return False

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError:
            return None

    @staticmethod
    def generate_auth_token() -> str:
        """Genera un token de sesión de respaldo"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida un correo electrónico"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_ruc(ruc: str) -> bool:
        """Valida un RUC de Ecuador (formato básico)"""
        if not ruc or len(ruc) != 13:
            return False
        return ruc.isdigit()

    @staticmethod
    def validate_invoice_number(invoice_number: str) -> bool:
        """Valida el formato del número de factura"""
        import re
        pattern = r'^\d{3}-\d{3}-\d{9}$'
        return re.match(pattern, invoice_number) is not None

    @staticmethod
    def sanitize_input(input_str: str, max_length: int = 255) -> str:
        """Sanitiza entradas del usuario"""
        if not isinstance(input_str, str):
            raise ValueError("Input debe ser string")
        return input_str.strip()[:max_length]

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verifica una contraseña contra su hash"""
        try:
            salt, stored_hash = password_hash.split('$')
            computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return computed_hash.hex() == stored_hash
        except:
            return False

    @staticmethod
    def generate_auth_token() -> str:
        """Genera un token de autenticación"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida un correo electrónico"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_ruc(ruc: str) -> bool:
        """Valida un RUC de Ecuador (formato básico)"""
        # RUC ecuatoriano: 13 dígitos
        if not ruc or len(ruc) != 13:
            return False
        return ruc.isdigit()

    @staticmethod
    def validate_invoice_number(invoice_number: str) -> bool:
        """Valida el formato del número de factura"""
        # Formato: XXX-XXX-XXXXXXXXXX (18 dígitos)
        import re
        pattern = r'^\d{3}-\d{3}-\d{9}$'
        return re.match(pattern, invoice_number) is not None

    @staticmethod
    def sanitize_input(input_str: str, max_length: int = 255) -> str:
        """Sanitiza entradas del usuario"""
        if not isinstance(input_str, str):
            raise ValueError("Input debe ser string")
        return input_str.strip()[:max_length]
