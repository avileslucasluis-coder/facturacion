import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.core.config import settings
from src.services.billing_service import BillingService
from src.routers import auth, products, invoices, providers, reports, ai, documents

BASE_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = BASE_DIR / settings.static_dir


@asynccontextmanager
async def lifespan(app: FastAPI):
    service = BillingService()
    default_users = [
        ('testuser', 'test@test.com'),
        ('empresa1', 'empresa1@test.com'),
    ]
    for username, email in default_users:
        if not service.db.get_user(username):
            service.register(username, 'password123', email)
    yield

app = FastAPI(
    title=settings.app_name,
    version="2.0",
    description="Back-end modular y seguro para un sistema empresarial de facturación electrónica en Ecuador.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
async def root():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return RedirectResponse(url="/docs")


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])


app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(invoices.router, prefix="/api/invoices", tags=["invoices"])
app.include_router(providers.router, prefix="/api/providers", tags=["providers"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
