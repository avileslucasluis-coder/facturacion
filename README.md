# Facturación Electrónica Empresarial

Plataforma modular de facturación y gestión administrativa para pymes en Ecuador.
Este sistema está construido con **FastAPI**, **SQLite**, **HTML/CSS/JS** y una capa de IA que consulta datos reales del negocio.

## ✅ Qué incluye

- Autenticación profesional con **JWT Bearer**
- Backend modular con **routers** y **servicios**
- Frontend administrativo funcional con panel, productos, facturas y proveedores
- Base de datos lista para facturación electrónica (SRI)
- IA útil, verificable y tolerante a falta de OpenAI
- Pruebas con **pytest**
- Pipeline de CI con **GitHub Actions**
- Contenedor Docker listo para producción

## 🧱 Tecnologías

- Python 3.12
- FastAPI
- SQLite
- SQLAlchemy (para futuro escalado)
- passlib + bcrypt
- python-jose
- reportlab / lxml
- HTML / CSS / JavaScript

## 📁 Estructura del proyecto

```
facturacionnow/
├── src/
│   ├── api.py              # Entrada compatible y wrapper a src.main
│   ├── main.py             # Aplicación FastAPI principal
│   ├── core/
│   │   ├── config.py       # Configuración y variables de entorno
│   │   ├── security.py     # JWT y hashing seguro
│   │   ├── sri_validator.py
│   │   └── backend.py      # Capa de datos y acceso a SQLite
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py     # Alias a la implementación de la capa de datos
│   ├── routers/            # Endpoints REST organizados
│   └── services/           # Lógica de negocio y servicios IA
├── static/
│   ├── index.html          # Frontend administrativo
│   ├── css/style.css
│   └── js/app.js
├── data/
│   └── billing_system.db
├── tests/
│   └── test_app.py
├── .github/workflows/python-app.yml
├── Dockerfile
├── .dockerignore
├── requirements.txt
└── README.md
```

## ⚙️ Instalación local

1. Clona el repositorio

```bash
git clone https://github.com/avileslucasluis-coder/facturacion.git
cd facturacionnow
```

2. Crea y activa el entorno virtual

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

3. Instala dependencias

```bash
pip install -r requirements.txt
```

4. Crea un archivo `.env`

```env
JWT_SECRET_KEY=un_valor_muy_seguro
OPENAI_API_KEY=
DATABASE_URL=sqlite:///data/billing_system.db
```

## ▶️ Ejecutar local

```bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

Accede a la app en:

```text
http://localhost:8000
```

Documentación de la API:

```text
http://localhost:8000/docs
```

## 🔐 Usuarios de prueba

- Usuario: `testuser`
- Contraseña: `password123`

> Si no existe, crea uno nuevo con el endpoint de registro.

## 📡 Endpoints principales

- `POST /api/auth/register` — Registrar usuario
- `POST /api/auth/login` — Iniciar sesión
- `GET /api/auth/me` — Datos del usuario actual
- `GET /api/products` — Listar productos
- `POST /api/products` — Crear producto
- `GET /api/invoices` — Listar facturas
- `POST /api/invoices` — Crear factura
- `POST /api/invoices/{invoice_id}/items` — Añadir item a factura
- `GET /api/providers` — Listar proveedores
- `POST /api/providers` — Crear proveedor
- `POST /api/ai/analyze-invoice` — Analizar factura con IA
- `POST /api/ai/suggest-price` — Sugerir precio

## 🧪 Pruebas

```bash
pytest -q
```

## 🐳 Docker

Construir imagen:

```bash
docker build -t facturacionnow .
```

Iniciar contenedor:

```bash
docker run -p 8000:8000 -e JWT_SECRET_KEY=mi_secreto facturacionnow
```

## 📌 Notas de producción

- Revisa `JWT_SECRET_KEY` antes de desplegar
- Cambia `DATABASE_URL` a PostgreSQL cuando el proyecto escale
- El endpoint `/api/documents/placeholders` está listo para integrar el SRI oficial
- El frontend usa `Bearer token` y `fetchWithAuth()`

## ✅ Estado actual

- Backend modular y listo
- Frontend administrativo funcional
- Autenticación JWT real
- Base de datos preparada para facturación y retenciones
- CI/CD con GitHub Actions
- Docker listo
