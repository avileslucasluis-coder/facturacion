# 🌐 GUÍA DE USO - VERSIÓN WEB CON IA

## ¿Qué es esto?

Sistema profesional de facturación para Ecuador **con Inteligencia Artificial integrada**, accesible desde cualquier navegador web.

---

## 🚀 Instalación Rápida

### Paso 1: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 2: Configurar IA (Opcional pero Recomendado)

Para activar OpenAI (análisis de facturas inteligentes):

1. Registrate en https://openai.com
2. Obtén tu API Key
3. Edita `.env` y añade:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxx
```

Sin configuración, la IA funcionará con análisis simulados.

### Paso 3: Registrar un Usuario (Desde consola)

```bash
python
>>> from billing_service import BillingService
>>> s = BillingService()
>>> s.register("testuser", "password123", "test@example.com", "1234567890001")
>>> exit()
```

### Paso 4: Iniciar el Servidor

**Windows:**
```bash
start_web.bat
```

**Linux/Mac:**
```bash
bash start_web.sh
```

O manualmente:
```bash
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

---

## 🌐 Acceder a la Aplicación

Abre tu navegador en:
- **Interfaz Web:** http://localhost:8000/index.html
- **API Docs:** http://localhost:8000/docs (Swagger)
- **ReDoc:** http://localhost:8000/redoc

---

## 📚 Características Principales

### Dashboard
- Estadísticas de ventas
- Facturas este mes
- Facturas pendientes
- Resumen de actividad

### Gestión de Facturas
- ✅ Crear facturas
- ✅ Añadir items
- ✅ Calcular impuestos automáticamente
- ✅ Finalizar y autorizar con SRI
- ✅ Ver historial

### Gestión de Productos
- ✅ Crear catálogo
- ✅ Gestionar precios
- ✅ Configurar tasas de impuesto

### 🤖 Asistente de IA

#### Analizar Factura
```
Entrada: ID de Factura
Salida:
  - Análisis inteligente del contenido
  - Sugerencias de mejora
  - Nivel de riesgo (bajo/medio/alto)
Ejemplo: "Esta factura tiene un total alto, considera dividirla en múltiples facturas para mejor gestión"
```

#### Sugerir Precio
```
Entrada: Nombre del producto
Salida:
  - Precio recomendado
  - Razonamiento del análisis
Ejemplo: "Para un Laptop: $750-850 es precio competitivo"
```

#### Insights de Ventas
```
Entrada: Período de fechas
Salida:
  - Análisis de tendencias
  - Productos top
  - Recomendaciones
Ejemplo: "Las ventas crecieron 20% este mes, enfócate en productos electrónicos"
```

### Reportes
- Reportes por período
- Filtring por estado
- Exportación de datos

---

## 🔄 Flujo de Trabajo Típico

### 1. Registrarse
```python
# Desde consola
from billing_service import BillingService
s = BillingService()
s.register("miempresa", "contraseña123", "info@empresa.com", "1234567890001")
```

### 2. Iniciar sesión en web
- Abrir http://localhost:8000/index.html
- Login con usuario y contraseña

### 3. Crear productos
- Ir a "Productos"
- Crear catálogo de productos

### 4. Crear factura
- Ir a "Facturas"
- Crear nueva factura (ej: 001-001-000000001)
- Añadir items

### 5. Usar IA para análisis
- Ir a "Asistente IA"
- Analizar factura con IA
- Obtener sugerencias de precios
- Ver insights de ventas

### 6. Generar reportes
- Ir a "Reportes"
- Seleccionar período
- Descargar/ver datos

---

## 📊 API REST Endpoints

### Autenticación
```
POST /api/auth/register
POST /api/auth/login  
POST /api/auth/logout
```

### Facturas
```
POST   /api/invoices                    - Crear factura
GET    /api/invoices/{id}               - Obtener factura
POST   /api/invoices/{id}/items         - Añadir item
POST   /api/invoices/{id}/finalize      - Finalizar
POST   /api/invoices/{id}/submit-sri    - Enviar a SRI
```

### Productos
```
POST   /api/products                    - Crear producto
```

### IA
```
POST   /api/ai/analyze-invoice          - Analizar factura con IA
POST   /api/ai/suggest-price            - Sugerir precio
POST   /api/ai/sales-insights           - Insights de ventas
POST   /api/ai/document-scan            - Procesar documento
```

### Reportes
```
POST   /api/reports/sales               - Generar reporte
```

### Health
```
GET    /api/health                      - Estado de API
```

---

## 🔐 Seguridad

✅ **Contraseñas Hasheadas:**
- PBKDF2-SHA256 con salt aleatorio
- 100,000 iteraciones

✅ **Protección SQL Injection:**
- Todas las queries usan parameterized statements

✅ **CORS Habilitado:**
- Acceso desde cualquier origen (configurable)

✅ **Validaciones:**
- RUC, Email, Número de Factura
- Sanitización de inputs

---

## 🧪 Testing

### Test de Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

### Test de Crear Producto
```bash
curl -X POST "http://localhost:8000/api/products?username=testuser" \
  -H "Content-Type: application/json" \
  -d '{"name":"Laptop","price":800.0}'
```

### Ver Documentación Interactiva
```
http://localhost:8000/docs
```

---

## 📝 Estructura de Archivos (Web)

```
facturacionnow/
├── api.py                  # FastAPI server
├── ai_service.py          # Servicio de IA
├── index.html             # Frontend web
├── requirements.txt       # Dependencias pip
├── .env                   # Configuración
├── start_web.bat          # Script Windows
├── start_web.sh           # Script Linux/Mac
├── backend.py             # Base de datos
├── billing_service.py     # Lógica de negocio
├── security.py            # Seguridad
└── WEB_GUIDE.md           # Esta guía
```

---

## 🆘 Troubleshooting

### "Puerto 8000 ya está en uso"
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### "ModuleNotFoundError: No module named 'fastapi'"
```bash
pip install -r requirements.txt
```

### "OPENAI_API_KEY no configurada"
- Sin esto es OK, las respuestas de IA serán simuladas
- Para IA real, configura en `.env`

### "Login no funciona"
- Asegúrate de haber registrado usuario desde consola
- Verifica usuario y contraseña exactos

---

## 🚀 Próximas Mejoras

- [ ] WebSockets para real-time updates
- [ ] Autenticación JWT con refresh tokens
- [ ] Base de datos PostgreSQL
- [ ] PDF generation de facturas
- [ ] Integración email automático
- [ ] Dashboard móvil responsive
- [ ] Caché Redis
- [ ] Analytics avanzado
- [ ] Integración SRI real
- [ ] Múltiples idiomas

---

## 📞 Soporte

**Documentación API:** http://localhost:8000/docs
**GitHub:** (cuando se publique)

---

## 📄 Licencia

Código abierto - Úsalo libremente

---

**¡Disfruta tu sistema de facturación inteligente! 🎉**
