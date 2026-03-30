"""
FastAPI Backend para Sistema de Facturación con IA
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from src.core.security import SecurityManager, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from src.core.sri_validator import SRIValidator
from typing import Optional, List
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv

# Servicios
from src.services.billing_service import BillingService
from src.services.ai_service import AIService

# ==============================
# CONFIG INICIAL
# ==============================

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rutas del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# ==============================
# APP
# ==============================

app = FastAPI(
    title="Sistema de Facturación con IA",
    version="2.0"
)

# Static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", include_in_schema=False)
async def root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return RedirectResponse(url="/docs")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# SERVICIOS
# ==============================

billing_service = BillingService()
ai_service = AIService()

# ==============================
# USUARIOS DE PRUEBA
# ==============================

def crear_usuarios_prueba():
    for username, email in [("testuser", "test@test.com"), ("empresa1", "empresa1@test.com")]:
        existing = billing_service.db.get_user(username)
        if existing:
            continue
        success, _ = billing_service.register(username, "password123", email, None)
        if not success:
            logger.info(f"Usuario de prueba {username} ya existe o ya está registrado")

crear_usuarios_prueba()

# ==============================
# MODELOS
# ==============================

class UserRegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserLoginRequest(BaseModel):
    username: str
    password: str

class ProductRequest(BaseModel):
    name: str
    price: float
    tax_rate: float = 0.12

class CreateInvoiceRequest(BaseModel):
    invoice_number: str

class AddInvoiceItemRequest(BaseModel):
    product_id: Optional[int] = None
    description: str
    quantity: int
    unit_price: float
    tax_rate: float = 0.12

class AIAnalysisRequest(BaseModel):
    invoice_id: int
    token: Optional[str] = None

class SuggestPriceRequest(BaseModel):
    product_name: str
    token: Optional[str] = None

class RetentionItemRequest(BaseModel):
    tax_type: str = 'IVA'
    tax_rate: float = 0.12
    base_amount: float
    retained_amount: Optional[float] = None

class RetentionRequest(BaseModel):
    retention_number: str
    retention_type: str  # income (104) o purchase (103)
    provider_ruc: str
    provider_name: str
    date: str
    invoice_id: Optional[int] = None
    items: Optional[List[RetentionItemRequest]] = []

class DateRangeRequest(BaseModel):
    start_date: str
    end_date: str

class RetentionReportRequest(BaseModel):
    start_date: str
    end_date: str
    report_type: str = '104'
    provider_ruc: Optional[str] = None

class UserRoleUpdateRequest(BaseModel):
    role: str

# ==============================
# AUTH
# ==============================

sessions = {}
TOKEN_EXPIRY_HOURS = 8

def create_session(username: str, user_id: int) -> str:
    token = SecurityManager.generate_auth_token()
    sessions[token] = {
        "username": username,
        "user_id": user_id,
        "created_at": datetime.utcnow()
    }
    return token

def get_current_user(token: str = Depends(oauth2_scheme)):
    username = SecurityManager.verify_token(token)
    if not username:
        session = sessions.get(token)
        if session:
            username = session.get('username')

    if not username:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    user = billing_service.db.get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    billing_service.current_user = user
    billing_service.current_user_id = user['id']
    if user.get('ruc'):
        billing_service.sri_validator = SRIValidator(user['ruc'])
    else:
        billing_service.sri_validator = None

    return user




@app.post("/api/auth/register")
def register(data: UserRegisterRequest):
    success, message = billing_service.register(data.username, data.password, data.email)
    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"success": True, "message": message}

@app.post("/api/auth/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    success, message = billing_service.login(form_data.username, form_data.password)
    if not success:
        raise HTTPException(status_code=401, detail=message)

    user_record = billing_service.db.get_user(form_data.username)
    if not user_record:
        raise HTTPException(status_code=401, detail="Usuario no encontrado después de token")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = SecurityManager.create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )

    session_token = create_session(form_data.username, user_record['id'])

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": form_data.username,
        "session_token": session_token
    }

@app.post("/api/auth/login")
def login(data: UserLoginRequest):
    success, message = billing_service.login(data.username, data.password)
    if not success:
        raise HTTPException(status_code=401, detail=message)

    user_record = billing_service.db.get_user(data.username)
    if not user_record:
        raise HTTPException(status_code=401, detail="Usuario no encontrado después de login")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = SecurityManager.create_access_token(
        data={"sub": data.username}, expires_delta=access_token_expires
    )

    session_token = create_session(data.username, user_record['id'])

    return {
        "success": True,
        "username": data.username,
        "access_token": access_token,
        "token_type": "bearer",
        "session_token": session_token
    }

@app.get("/api/auth/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user.get('username'),
        "email": current_user.get('email'),
        "role": current_user.get('role'),
        "ruc": current_user.get('ruc'),
        "company_name": current_user.get('company_name'),
        "phone": current_user.get('phone')
    }

@app.post('/api/auth/logout')
def logout(current_user: dict = Depends(get_current_user)):
    billing_service.logout()
    return {"success": True, "message": "Cierre de sesión exitoso"}

# ==============================
# FACTURAS
# ==============================

@app.post("/api/invoices")
def create_invoice(data: CreateInvoiceRequest, current_user: dict = Depends(get_current_user)):
    invoice_id, msg = billing_service.create_invoice(data.invoice_number)
    if not invoice_id:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "invoice_id": invoice_id, "message": msg}

@app.get("/api/invoices")
def list_invoices(current_user: dict = Depends(get_current_user)):
    invoices, msg = billing_service.list_invoices()
    if invoices is None:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "invoices": invoices}

# ==============================
# PRODUCTOS
# ==============================

@app.post("/api/products")
def create_product(data: ProductRequest, current_user: dict = Depends(get_current_user)):
    pid, msg = billing_service.add_product(data.name, data.price, data.tax_rate)
    if not pid:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "product_id": pid, "message": msg}

@app.get("/api/products")
def list_products(current_user: dict = Depends(get_current_user)):
    products, msg = billing_service.list_products()
    if products is None:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "products": products}

@app.get("/api/providers")
def list_providers(current_user: dict = Depends(get_current_user)):
    providers, msg = billing_service.list_providers()
    if providers is None:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "providers": providers}

@app.post("/api/providers")
def create_provider(data: dict, current_user: dict = Depends(get_current_user)):
    name = data.get('name')
    ruc = data.get('ruc')
    email = data.get('email')
    phone = data.get('phone')
    address = data.get('address')
    provider_id, msg = billing_service.add_provider(name, ruc, email, phone, address)
    if not provider_id:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "provider_id": provider_id, "message": msg}

@app.get("/api/admin/users")
def admin_list_users(current_user: dict = Depends(get_current_user)):
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Acceso no autorizado")
    users, msg = billing_service.get_users()
    if users is None:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "users": users}

@app.patch("/api/admin/users/{user_id}/role")
def admin_set_user_role(user_id: int, data: UserRoleUpdateRequest, current_user: dict = Depends(get_current_user)):
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Acceso no autorizado")
    ok, msg = billing_service.set_user_role(user_id, data.role)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}

@app.get("/api/inventory/aggregate")
def inventory_aggregate(current_user: dict = Depends(get_current_user)):
    inventory, msg = billing_service.get_inventory_aggregation()
    if inventory is None:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "inventory": inventory}

@app.post("/api/retentions")
def create_retention(data: RetentionRequest, current_user: dict = Depends(get_current_user)):
    retention_id, msg = billing_service.create_retention(data.retention_number, data.retention_type, data.provider_ruc, data.provider_name, data.date, data.invoice_id)
    if not retention_id:
        raise HTTPException(status_code=400, detail=msg)

    for item in data.items or []:
        retained = item.retained_amount if item.retained_amount is not None else item.base_amount * item.tax_rate
        ok, item_msg = billing_service.add_retention_item(retention_id, item.tax_type, item.tax_rate, item.base_amount, retained)
        if not ok:
            raise HTTPException(status_code=400, detail=item_msg)

    summary, _ = billing_service.get_retention_summary(retention_id)
    return {"success": True, "retention_id": retention_id, "summary": summary}

@app.get("/api/retentions")
def list_retentions(current_user: dict = Depends(get_current_user)):
    retentions, msg = billing_service.list_retentions()
    if retentions is None:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "retentions": retentions}

@app.post("/api/report/103")
def report_103(data: DateRangeRequest, current_user: dict = Depends(get_current_user)):
    report, msg = billing_service.get_retention_report(data.start_date, data.end_date, report_type='103')
    if report is None:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "report": report}

@app.post("/api/report/104")
def report_104(data: DateRangeRequest, current_user: dict = Depends(get_current_user)):
    report, msg = billing_service.get_retention_report(data.start_date, data.end_date, report_type='104')
    if report is None:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "report": report}

@app.post("/api/report/retentions")
def report_retention(data: RetentionReportRequest, current_user: dict = Depends(get_current_user)):
    report, msg = billing_service.get_retention_report(data.start_date, data.end_date, data.report_type, data.provider_ruc)
    if report is None:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "report": report}

@app.post("/api/sri/sign-invoice")
def sri_sign_invoice(data: AIAnalysisRequest, current_user: dict = Depends(get_current_user)):
    result, msg = billing_service.sign_and_validate_invoice(data.invoice_id)
    if result is None:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "sri": result}

@app.post("/api/invoices/bulk-upload")
async def bulk_upload_invoices(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    content = (await file.read()).decode('utf-8')
    results, msg = billing_service.bulk_upload_invoices(content)
    if results is None:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "results": results}

# ==============================
# IA
# ==============================

@app.post("/api/invoices/{invoice_id}/items")
def add_invoice_item(invoice_id: int, data: AddInvoiceItemRequest, current_user: dict = Depends(get_current_user)):
    success, msg = billing_service.add_invoice_item(
        invoice_id,
        data.product_id,
        data.description,
        data.quantity,
        data.unit_price,
        data.tax_rate
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}

@app.websocket("/api/ai/realtime")
async def ai_realtime(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            prompt = data.get("prompt")
            if not prompt:
                await websocket.send_json({"error": "prompt es requerido"})
                continue
            result = ai_service.realtime_assistant(prompt)
            await websocket.send_json({
                "response": result,
                "timestamp": datetime.utcnow().isoformat()
            })
    except WebSocketDisconnect:
        logger.info("WebSocket AI realtime disconnected")

@app.post("/api/ai/analyze-invoice")
def analyze(data: AIAnalysisRequest, current_user: dict = Depends(get_current_user)):
    summary, _ = billing_service.get_invoice_summary(data.invoice_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    result = ai_service.analyze_invoice(summary)

    return {
        "analysis": result["analysis"],
        "suggestions": result["suggestions"],
        "risk": result["risk_level"]
    }

@app.post("/api/ai/suggest-price")
def suggest_price(data: SuggestPriceRequest, current_user: dict = Depends(get_current_user)):
    result = ai_service.suggest_product_price(data.product_name)
    return result

def resolve_user(token: Optional[str] = None, current_user: Optional[dict] = None):
    if current_user:
        return current_user
    if token:
        username = SecurityManager.verify_token(token)
        if not username:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
        user = billing_service.db.get_user(username)
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return user
    raise HTTPException(status_code=401, detail="Autenticación requerida")


@app.post("/api/ai/suggest-price/public")
def suggest_price_public(data: SuggestPriceRequest):
    result = ai_service.suggest_product_price(data.product_name)
    return result
def suggest_price_public(data: SuggestPriceRequest):
    result = ai_service.suggest_product_price(data.product_name)
    return result


@app.post("/api/ai/analyze-invoice/public")
def analyze_public(data: AIAnalysisRequest):
    summary, _ = billing_service.get_invoice_summary(data.invoice_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    result = ai_service.analyze_invoice(summary)
    return {
        "analysis": result["analysis"],
        "suggestions": result["suggestions"],
        "risk": result["risk_level"]
    }


@app.get("/api/ai/status")
def ai_status():
    return {
        "available": ai_service.is_available(),
        "model": ai_service.model,
        "session_count": len(sessions)
    }

# ==============================
# SALUD
# ==============================

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "time": datetime.now().isoformat()
    }

# ==============================
# ERRORES
# ==============================

@app.exception_handler(Exception)
async def error_handler(request, exc):
    logger.error(str(exc))
    return JSONResponse(
        status_code=500,
        content={"error": "Error interno"}
    )

# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)