# 🚀 Sistema de Facturación con IA

Sistema web tipo ERP desarrollado con **FastAPI + HTML/JS**, inspirado en plataformas como Contífico y Siigo.
Permite gestionar facturas, productos, inventario y análisis con inteligencia artificial.

---

## 📌 Características

* ✅ Gestión de facturas (crear, editar, listar)
* ✅ Productos e inventario
* ✅ Retenciones y documentos electrónicos
* ✅ Generación de PDF y XML
* ✅ Reportes financieros
* ✅ Subida de archivos (facturas)
* 🤖 Análisis con Inteligencia Artificial
* 🔐 Autenticación de usuarios

---

## 🧱 Tecnologías utilizadas

* Python 3.10+
* FastAPI
* SQLite
* HTML / CSS / JavaScript
* OpenAI API (opcional)

---

## 📁 Estructura del proyecto

```
facturacionnow/
│
├── src/
│   ├── api.py                # Backend principal FastAPI
│   ├── core/                # Seguridad, validaciones, DB
│   ├── services/            # Lógica de negocio
│   └── ui.py                # UI lógica
│
├── static/
│   └── index.html           # Frontend principal
│
├── data/
│   └── billing_system.db    # Base de datos
│
├── .env                     # Variables de entorno
├── requirements.txt         # Dependencias
└── README.md
```

---

## ⚙️ Instalación

### 1. Clonar repositorio

```bash
git clone https://github.com/avileslucasluis-coder/facturacion.git
cd facturacion
```

---

### 2. Crear entorno virtual

```bash
python -m venv .venv
```

Activar entorno:

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux / Mac:**

```bash
source .venv/bin/activate
```

---

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 🔐 Variables de entorno (.env)

Crea un archivo `.env`:

```env
OPENAI_API_KEY=tu_api_key_aqui
```

👉 Si no tienes API KEY, el sistema igual funciona (sin IA avanzada).

---

## ▶️ Ejecutar el proyecto

```bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

---

## 🌐 Acceso

Abrir en navegador:

```text
http://localhost:8000
```

Documentación API:

```text
http://localhost:8000/docs
```

---

## 🔑 Usuario de prueba

```text
Usuario: testuser
Password: password123
```

---

## 🤖 Funciones de IA

* Análisis de facturas
* Sugerencia de precios
* Insights de ventas
* Extracción de datos

---

## 📡 Endpoints principales

| Método | Endpoint                | Descripción      |
| ------ | ----------------------- | ---------------- |
| POST   | /api/auth/login         | Login            |
| GET    | /api/invoices           | Listar facturas  |
| POST   | /api/invoices           | Crear factura    |
| GET    | /api/products           | Listar productos |
| POST   | /api/ai/analyze-invoice | Analizar factura |
| POST   | /api/ai/suggest-price   | Sugerir precio   |

---

## ⚠️ Problemas comunes

### ❌ Error 401 Unauthorized

➡️ Debes enviar el token en headers:

```http
Authorization: Bearer TOKEN
```

---

### ❌ No carga el frontend

➡️ Asegúrate de tener:

```
static/index.html
```

---

### ❌ Error OpenAI

➡️ Verifica tu `.env`

---

## 🚀 Deploy (próximamente)

Puedes desplegar en:

* Render
* Railway
* VPS

---

## 👨‍💻 Autor

**Luis Avilés**
GitHub: https://github.com/avileslucasluis-coder

---

## 📜 Licencia

Uso libre para aprendizaje y proyectos personales.
