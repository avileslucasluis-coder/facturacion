#!/usr/bin/env python3
"""
Script de demostración de la API REST con IA
Prueba todos los endpoints sin necesidad de la interfaz web
"""

import requests
import json
from datetime import datetime, timedelta

# Configuración
API_BASE = "http://localhost:8000/api"
USERNAME = "testuser"

# Colores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_section(title):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}{Colors.ENDC}\n")

def print_success(msg):
    print(f"{Colors.OKGREEN}✓ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}✗ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.OKCYAN}ℹ {msg}{Colors.ENDC}")

def print_response(response):
    try:
        print(json.dumps(response, indent=2, ensure_ascii=False))
    except:
        print(response)

# ============================================================================
# TESTS DE API
# ============================================================================

def test_health_check():
    """Verificar estado de la API"""
    print_section("1. VERIFICAR ESTADO DE LA API")
    
    try:
        response = requests.get(f"{API_BASE}/health")
        print_success("API está disponible")
        print_response(response.json())
        return True
    except Exception as e:
        print_error(f"No se pudo conectar a la API: {e}")
        print_info("¿Está el servidor iniciado? Ejecuta: python -m uvicorn api:app --reload")
        return False

def test_login():
    """Prueba de login"""
    print_section("2. AUTENTICACIÓN - LOGIN")
    
    try:
        payload = {
            "username": USERNAME,
            "password": "password123"
        }
        response = requests.post(f"{API_BASE}/auth/login", json=payload)
        data = response.json()
        
        if data.get('success'):
            print_success("Login exitoso")
            print_response(data)
            return True
        else:
            print_error(f"Login fallido: {data.get('detail', 'Error desconocido')}")
            print_info("¿Has registrado el usuario? Desde python: s.register('testuser', 'password123')")
            return False
    except Exception as e:
        print_error(f"Error en login: {e}")
        return False

def test_create_product():
    """Crear un producto"""
    print_section("3. GESTIÓN DE PRODUCTOS - CREAR")
    
    try:
        payload = {
            "name": "Laptop Dell XPS",
            "price": 1200.00,
            "tax_rate": 0.12
        }
        response = requests.post(
            f"{API_BASE}/products?username={USERNAME}",
            json=payload
        )
        data = response.json()
        
        if data.get('success'):
            print_success("Producto creado exitosamente")
            print_response(data)
            return data.get('product_id')
        else:
            print_error(f"Error al crear producto: {data.get('detail')}")
            return None
    except Exception as e:
        print_error(f"Error: {e}")
        return None

def test_create_invoice():
    """Crear una factura"""
    print_section("4. GESTIÓN DE FACTURAS - CREAR")
    
    try:
        payload = {
            "invoice_number": "001-001-000000001"
        }
        response = requests.post(
            f"{API_BASE}/invoices?username={USERNAME}",
            json=payload
        )
        data = response.json()
        
        if data.get('success'):
            print_success("Factura creada exitosamente")
            print_response(data)
            return data.get('invoice_id')
        else:
            print_error(f"Error al crear factura: {data.get('detail')}")
            return None
    except Exception as e:
        print_error(f"Error: {e}")
        return None

def test_add_invoice_item(invoice_id, product_id):
    """Añadir item a factura"""
    print_section("5. GESTIÓN DE FACTURAS - AÑADIR ITEMS")
    
    try:
        payload = {
            "product_id": product_id,
            "description": "Laptop profesional para desarrollo",
            "quantity": 2,
            "unit_price": 1200.00,
            "tax_rate": 0.12
        }
        response = requests.post(
            f"{API_BASE}/invoices/{invoice_id}/items?username={USERNAME}",
            json=payload
        )
        data = response.json()
        
        if data.get('success'):
            print_success("Item añadido a factura")
            print_response(data)
            return True
        else:
            print_error(f"Error: {data.get('detail')}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_get_invoice(invoice_id):
    """Obtener datos de factura"""
    print_section("6. GESTIÓN DE FACTURAS - OBTENER DETALLES")
    
    try:
        response = requests.get(
            f"{API_BASE}/invoices/{invoice_id}?username={USERNAME}"
        )
        data = response.json()
        
        if data.get('success'):
            print_success("Factura obtenida")
            print_response(data)
            return True
        else:
            print_error(f"Error: {data.get('detail')}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_finalize_invoice(invoice_id):
    """Finalizar una factura"""
    print_section("7. GESTIÓN DE FACTURAS - FINALIZAR")
    
    try:
        response = requests.post(
            f"{API_BASE}/invoices/{invoice_id}/finalize?username={USERNAME}"
        )
        data = response.json()
        
        if data.get('success'):
            print_success("Factura finalizada")
            print_response(data)
            return True
        else:
            print_error(f"Error: {data.get('detail')}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_analyze_invoice(invoice_id):
    """Analizar factura con IA"""
    print_section("8. IA - ANALIZAR FACTURA")
    
    try:
        payload = {"invoice_id": invoice_id}
        response = requests.post(
            f"{API_BASE}/ai/analyze-invoice?username={USERNAME}",
            json=payload
        )
        data = response.json()
        
        print_info("Análisis de IA:")
        print_response(data)
        return True
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_suggest_price():
    """Sugerir precio con IA"""
    print_section("9. IA - SUGERIR PRECIO")
    
    try:
        response = requests.post(
            f"{API_BASE}/ai/suggest-price?product_name=Monitor%20LED%204K&username={USERNAME}"
        )
        data = response.json()
        
        print_info("Sugerencia de precio:")
        print_response(data)
        return True
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_sales_insights():
    """Obtener insights de ventas con IA"""
    print_section("10. IA - INSIGHTS DE VENTAS")
    
    try:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        payload = {
            "start_date": start_date,
            "end_date": end_date
        }
        response = requests.post(
            f"{API_BASE}/ai/sales-insights?username={USERNAME}",
            json=payload
        )
        data = response.json()
        
        print_info(f"Insights de ventas ({start_date} a {end_date}):")
        print_response(data)
        return True
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_sales_report():
    """Generar reporte de ventas"""
    print_section("11. REPORTES - REPORTE DE VENTAS")
    
    try:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        payload = {
            "start_date": start_date,
            "end_date": end_date
        }
        response = requests.post(
            f"{API_BASE}/reports/sales?username={USERNAME}",
            json=payload
        )
        data = response.json()
        
        print_info(f"Reporte de ventas ({start_date} a {end_date}):")
        print_response(data)
        return True
    except Exception as e:
        print_error(f"Error: {e}")
        return False

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Ejecuta todos los tests"""
    
    print(f"""{Colors.HEADER}{Colors.BOLD}
╔════════════════════════════════════════════════════════════════╗
║          DEMOSTRACIÓN DE API REST CON IA                       ║
║     Sistema de Facturación para Ecuador                        ║
╚════════════════════════════════════════════════════════════════╝
{Colors.ENDC}
    """)
    
    # 1. Verificar conexión
    if not test_health_check():
        return
    
    # 2. Login
    if not test_login():
        print_error("No se puede continuar sin autenticación")
        return
    
    # 3. Crear producto
    product_id = test_create_product()
    if not product_id:
        print_error("No se pudo crear producto")
        return
    
    # 4. Crear factura
    invoice_id = test_create_invoice()
    if not invoice_id:
        print_error("No se pudo crear factura")
        return
    
    # 5. Añadir items
    if not test_add_invoice_item(invoice_id, product_id):
        print_error("No se pudo añadir items")
        return
    
    # 6. Obtener detalles
    test_get_invoice(invoice_id)
    
    # 7. Finalizar
    test_finalize_invoice(invoice_id)
    
    # 8. Análisis de IA
    test_analyze_invoice(invoice_id)
    
    # 9. Sugerencia de precio
    test_suggest_price()
    
    # 10. Insights
    test_sales_insights()
    
    # 11. Reporte
    test_sales_report()
    
    print_section("✅ DEMOSTRACIÓN COMPLETADA")
    print(f"""
{Colors.OKGREEN}Todos los endpoints funcionaron correctamente!

Próximos pasos:
  1. Abre http://localhost:8000/index.html en tu navegador
  2. Login con: testuser / password123
  3. Crea facturas y usa las características de IA
  4. Genera reportes para análisis

Documentación:
  - http://localhost:8000/docs (Swagger UI)
  - http://localhost:8000/redoc (ReDoc)
  - WEB_GUIDE.md (Guía completa)
{Colors.ENDC}
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Demostración interrumpida por el usuario{Colors.ENDC}")
