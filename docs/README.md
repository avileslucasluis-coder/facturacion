# Sistema de Facturación - Documentación

## 📋 Descripción General

Sistema de facturación profesional en Python con soporte para múltiples usuarios, integración con SRI Ecuador, gestión segura de datos y reportes de ventas.

### Características Principales

✅ **Seguridad**
- Contraseñas hasheadas con PBKDF2-SHA256
- Validación de entradas
- Protección contra SQL Injection
- Auditoría de acciones

✅ **Gestión de Facturas**
- Creación y edición de facturas
- Gestión de items en facturas
- Cálculo automático de totales e impuestos
- Estados de factura (draft, finalized, authorized)

✅ **SRI Ecuador**
- Integración preparada para validación con SRI
- Generación de XML según estándares SRI
- Soporte para certificados digitales
- Códigos de autorización

✅ **Reportes**
- Generación de reportes de ventas por período
- Estadísticas de ingresos
- Consultas por estado de factura

✅ **Multi-usuario**
- Aislamiento de datos por usuario
- Control de acceso basado en autenticación
- Logs de auditoría detallados

---

## 🏗️ Estructura del Proyecto

```
facturacionnow/
├── backend.py              # Capa de base de datos
├── security.py             # Gestión de seguridad
├── sri_validator.py        # Integración SRI Ecuador
├── billing_service.py      # Servicio principal (lógica de negocio)
├── ui.py                   # Interfaz interactiva de línea de comandos
├── example.py              # Ejemplo y demostración
├── parte1.py               # Script de inicio
└── README.md               # Este archivo
```

### Descripción de Módulos

#### `backend.py`
**Responsabilidad**: Gestión de base de datos SQLite

**Clases**:
- `Database`: Maneja todas las operaciones de CRUD

**Métodos principales**:
- `add_user()`: Registra nuevo usuario
- `create_invoice()`: Crea factura
- `add_product()`: Añade producto al catálogo
- `add_invoice_item()`: Añade item a factura
- `log_audit()`: Registra acciones en auditoría

#### `security.py`
**Responsabilidad**: Implementación de características de seguridad

**Clases**:
- `SecurityManager`: Maneja contraseñas, tokens y validaciones

**Métodos principales**:
- `hash_password()`: Hashea contraseña de forma segura
- `verify_password()`: Verifica contraseña contra hash
- `validate_email()`: Valida email
- `validate_ruc()`: Valida RUC de Ecuador
- `validate_invoice_number()`: Valida formato de factura

#### `sri_validator.py`
**Responsabilidad**: Integración con SRI Ecuador

**Clases**:
- `SRIValidator`: Maneja validación y firma de facturas

**Métodos principales**:
- `generate_invoice_xml()`: Genera XML en formato SRI
- `sign_invoice()`: Firma digitalmente factura
- `validate_with_sri()`: Envía a SRI para validación
- `get_authorization_status()`: Consulta estado de autorización

#### `billing_service.py`
**Responsabilidad**: Lógica de negocio principal

**Clases**:
- `BillingService`: Orquesta todas las operaciones

**Métodos principales**:
- `register()`: Registra nuevo usuario
- `login()`: Autentica usuario
- `create_invoice()`: Crea factura nueva
- `finalize_invoice()`: Finaliza factura
- `submit_to_sri()`: Envía factura a SRI
- `generate_sales_report()`: Genera reporte de ventas

#### `ui.py`
**Responsabilidad**: Interfaz de línea de comandos interactiva

**Clases**:
- `BillingUI`: Menú interactivo

**Funciones principales**:
- Menú de registro e login
- Crear facturas y productos
- Ver resúmenes
- Enviar a SRI
- Generar reportes

---

## 🚀 Instalación y Uso

### Requisitos
- Python 3.7+
- SQLite3 (incluido en Python)

### Instalación

No hay dependencias externas para la funcionalidad básica:

```bash
# Clonar o descargar el proyecto
cd facturacionnow

# El proyecto está listo para usar
```

### Uso - Opción 1: Interfaz Interactiva

```bash
python ui.py
```

Esto abre un menú interactivo donde puede:
1. Registrar usuario
2. Iniciar sesión
3. Crear facturas
4. Añadir productos
5. Generar reportes

### Uso - Opción 2: Ejemplo Automático

```bash
python example.py
```

Ejecuta una demostración completa que:
- Registra usuarios
- Crea catalogos de productos
- Genera facturas
- Calcula totales
- Envia a SRI
- Genera reportes

### Uso - Opción 3: Como Módulo

```python
from billing_service import BillingService

# Inicializar
service = BillingService()

# Registrar usuario
service.register("usuario1", "password123", "user@example.com", "1234567890001")

# Iniciar sesión
service.login("usuario1", "password123")

# Crear factura
invoice_id, msg = service.create_invoice("001-001-000000001")

# Añadir producto
product_id, msg = service.add_product("Laptop", 800.00)

# Añadir item a factura
service.add_item_to_invoice(invoice_id, product_id, "Laptop Dell", 1, 800.00)

# Ver resumen
summary, msg = service.get_invoice_summary(invoice_id)

# Enviar a SRI
success, msg = service.submit_to_sri(invoice_id)

# Generar reporte
report, msg = service.generate_sales_report("2024-01-01", "2024-12-31")
```

---

## 💾 Base de Datos

El sistema utiliza SQLite3 con las siguientes tablas:

### `users`
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE,
    ruc TEXT UNIQUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

### `invoices`
```sql
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    invoice_number TEXT UNIQUE NOT NULL,
    date TEXT NOT NULL,
    subtotal REAL,
    tax REAL,
    total REAL,
    status TEXT,
    sri_validation_status TEXT,
    sri_authorization_code TEXT,
    created_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
```

### `products`
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    tax_rate REAL DEFAULT 0.12,
    created_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
```

### `invoice_items`
```sql
CREATE TABLE invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    product_id INTEGER,
    description TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    subtotal REAL NOT NULL,
    tax REAL,
    total REAL NOT NULL,
    FOREIGN KEY(invoice_id) REFERENCES invoices(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
)
```

### `audit_log`
```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
```

---

## 🔐 Seguridad

### Contraseñas
- Utilizan PBKDF2-SHA256 con salt aleatorio (16 bytes)
- 100,000 iteraciones para resistir ataques de fuerza bruta
- Las contraseñas nunca se almacenan en texto plano

### Validaciones
- SQL Injection: Todas las consultas usan parameterized queries
- Validación de entrada en todos los campos
- RUC validado según formato Ecuador (13 dígitos)
- Email validado con expresión regular
- Facturas requieren formato específico (XXX-XXX-XXXXXXXXXX)

### Auditoría
- Todas las acciones importantes se registran
- Logs incluyen usuario, acción y timestamp
- Consulta de logs disponible para auditoría

---

## 📊 Próximas Mejoras

### Integración SRI (en desarrollo)
La integración SRI está preparada pero requiere:
- Certificado digital (.p12) del contribuyente
- Credenciales de acceso al SRI
- Librería `signxml` para firmar digitalmente

### Para activar SRI en producción:
```bash
pip install signxml requests cryptography lxml
```

Luego:
```python
service.sri_validator.set_certificate('/path/to/cert.p12', 'password')
```

### Otras mejoras recomendadas
- [ ] API REST con FastAPI/Flask
- [ ] Base de datos PostgreSQL (para producción)
- [ ] Sistema de pagos integrado
- [ ] Plantillas de PDF para facturas
- [ ] Integración con email
- [ ] Dashboard web
- [ ] 2FA (autenticación de dos factores)
- [ ] Encriptación de datos sensibles

---

## 🧪 Testing

Para ejecutar pruebas:

```python
# Prueba de registro
from billing_service import BillingService

service = BillingService('test.db')

# Caso 1: Registro válido
success, msg = service.register("testuser", "password123")
assert success, "El registro debe ser exitoso"

# Caso 2: Contraseña corta
success, msg = service.register("testuser2", "123")
assert not success, "Debe rechazar contraseña corta"

# Caso 3: RUC inválido
success, msg = service.register("testuser3", "password123", ruc="123")
assert not success, "Debe rechazar RUC inválido"
```

---

## 📝 Notas

### Entorno DEV vs PROD
- **DEV**: Usa URLs de prueba del SRI, sin validación real
- **PROD**: Usa URLs de producción del SRI, validación real

### Formato de Factura
Ecuador requiere el formato: `XXX-XXX-XXXXXXXXXX`
Donde:
- Primeros 3 dígitos: Establecimiento
- Próximos 3 dígitos: Punto de emisión
- Últimos 9 dígitos: Número secuencial

### Impuestos
- IVA estándar: 12%
- Configurable por producto
- Cálculo automático en items

---

## 📄 Licencia

Este proyecto es de código abierto. Úsalo libremente.

## 📞 Soporte

Para más información sobre:
- **SRI Ecuador**: https://www.sri.gob.ec/
- **Facturación electrónica**: Ver regulaciones del SRI
- **Python**: https://www.python.org/

---

## 🎯 Resumen de Funcionalidades Implementadas

| Característica | Estado | Detalles |
|---|---|---|
| Registro de usuarios | ✅ Implementado | Validación completa, contraseñas seguras |
| Autenticación | ✅ Implementado | Login/logout con sesiones |
| Gestión de facturas | ✅ Implementado | CRUD completo |
| Gestión de productos | ✅ Implementado | Catálogo por usuario |
| Cálculo de impuestos | ✅ Implementado | Automático, configurable |
| SRI Ecuador | ⚠️ Preparado | Interfaz lista, requiere certificado |
| Reportes | ✅ Implementado | Por período, por usuario |
| Auditoría | ✅ Implementado | Log completo de acciones |
| Aislamiento de datos | ✅ Implementado | Por usuario |
| Seguridad | ✅ Implementado | Hashing, validación, SQL injection protection |

---

**Versión**: 2.0  
**Fecha**: 2024  
**Estado**: Producción-ready (excepto integración SRI)
