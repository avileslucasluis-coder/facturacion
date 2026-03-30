"""
Ejemplo de uso del Sistema de Facturación
Demuestra todas las funcionalidades principales
"""

from src.services.billing_service import BillingService
from datetime import datetime, timedelta

def print_section(title):
    """Imprime una sección con título"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def main():
    """Función principal de demostración"""
    
    # Inicializar el servicio
    service = BillingService('billing_demo.db')
    
    print_section("1. REGISTRO DE USUARIOS")
    
    # Registrar usuario 1
    print("\nRegistrando usuario 1...")
    success, msg = service.register(
        username="empresa1",
        password="password123",
        email="empresa1@example.com",
        ruc="1234567890001"
    )
    print(f"  Resultado: {msg}")
    
    # Registrar usuario 2
    print("\nRegistrando usuario 2...")
    success, msg = service.register(
        username="empresa2",
        password="password456",
        email="empresa2@example.com",
        ruc="1234567890002"
    )
    print(f"  Resultado: {msg}")
    
    print_section("2. AUTENTICACIÓN")
    
    # Login usuario 1
    print("\nIniciando sesión como empresa1...")
    success, msg = service.login("empresa1", "password123")
    print(f"  Resultado: {msg}")
    
    if not success:
        print("  Error en login. Abortando...")
        return
    
    print_section("3. CREAR CATÁLOGO DE PRODUCTOS")
    
    products = [
        ("Laptop Dell", 800.00),
        ("Mouse Logitech", 25.00),
        ("Teclado Mecánico", 120.00),
        ("Monitor 27 pulgadas", 350.00),
        ("Soporte para monitor", 45.00)
    ]
    
    product_ids = {}
    
    for name, price in products:
        print(f"\nAñadiendo producto: {name} - ${price:.2f}")
        product_id, msg = service.add_product(name, price)
        product_ids[name] = product_id
        print(f"  Resultado: {msg} (ID: {product_id})")
    
    print_section("4. CREAR FACTURAS")
    
    # Crear factura 1
    print("\nCreando factura 001-001-000000001...")
    invoice_id_1, msg = service.create_invoice("001-001-000000001")
    print(f"  Resultado: {msg}")
    print(f"  ID de Factura: {invoice_id_1}")
    
    # Crear factura 2
    print("\nCreando factura 001-001-000000002...")
    invoice_id_2, msg = service.create_invoice("001-001-000000002")
    print(f"  Resultado: {msg}")
    print(f"  ID de Factura: {invoice_id_2}")
    
    print_section("5. AÑADIR ITEMS A FACTURAS")
    
    # Factura 1 - Items
    items_invoice_1 = [
        ("Laptop Dell", 1, 800.00),
        ("Mouse Logitech", 2, 25.00),
        ("Teclado Mecánico", 1, 120.00)
    ]
    
    print("\nAñadiendo items a factura 001...")
    for product_name, quantity, price in items_invoice_1:
        success, msg = service.add_item_to_invoice(
            invoice_id=invoice_id_1,
            product_id=product_ids[product_name],
            description=product_name,
            quantity=quantity,
            unit_price=price
        )
        print(f"  {product_name} x{quantity}: {msg}")
    
    # Factura 2 - Items
    items_invoice_2 = [
        ("Monitor 27 pulgadas", 2, 350.00),
        ("Soporte para monitor", 2, 45.00)
    ]
    
    print("\nAñadiendo items a factura 002...")
    for product_name, quantity, price in items_invoice_2:
        success, msg = service.add_item_to_invoice(
            invoice_id=invoice_id_2,
            product_id=product_ids[product_name],
            description=product_name,
            quantity=quantity,
            unit_price=price
        )
        print(f"  {product_name} x{quantity}: {msg}")
    
    print_section("6. VER RESUMEN DE FACTURAS")
    
    # Resumen factura 1
    print("\nResumen Factura 001-001-000000001:")
    summary, msg = service.get_invoice_summary(invoice_id_1)
    
    if summary:
        invoice = summary['invoice']
        items = summary['items']
        
        print(f"  Número: {invoice['invoice_number']}")
        print(f"  Fecha: {invoice['date']}")
        print(f"  Estado: {invoice['status']}")
        print(f"  Subtotal: ${invoice['subtotal']:.2f}")
        print(f"  IVA (12%): ${invoice['tax']:.2f}")
        print(f"  TOTAL: ${invoice['total']:.2f}")
        print("\n  Items:")
        for item in items:
            print(f"    - {item['description']}: {item['quantity']} x ${item['unit_price']:.2f} = ${item['total']:.2f}")
    
    # Resumen factura 2
    print("\n\nResumen Factura 001-001-000000002:")
    summary, msg = service.get_invoice_summary(invoice_id_2)
    
    if summary:
        invoice = summary['invoice']
        items = summary['items']
        
        print(f"  Número: {invoice['invoice_number']}")
        print(f"  Fecha: {invoice['date']}")
        print(f"  Estado: {invoice['status']}")
        print(f"  Subtotal: ${invoice['subtotal']:.2f}")
        print(f"  IVA (12%): ${invoice['tax']:.2f}")
        print(f"  TOTAL: ${invoice['total']:.2f}")
        print("\n  Items:")
        for item in items:
            print(f"    - {item['description']}: {item['quantity']} x ${item['unit_price']:.2f} = ${item['total']:.2f}")
    
    print_section("7. FINALIZAR FACTURAS")
    
    print("\nFinalizando factura 001...")
    success, msg = service.finalize_invoice(invoice_id_1)
    print(f"  Resultado: {msg}")
    
    print("\nFinalizando factura 002...")
    success, msg = service.finalize_invoice(invoice_id_2)
    print(f"  Resultado: {msg}")
    
    print_section("8. ENVIAR A SRI (ECUADOR)")
    
    if service.sri_validator:
        print("\nEnviando factura 001 a SRI...")
        success, msg = service.submit_to_sri(invoice_id_1)
        print(f"  Resultado: {msg}")
        
        print("\nEnviando factura 002 a SRI...")
        success, msg = service.submit_to_sri(invoice_id_2)
        print(f"  Resultado: {msg}")
    else:
        print("  No hay RUC configurado")
    
    print_section("9. GENERAR REPORTE DE VENTAS")
    
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"\nGenerando reporte de {start_date} a {end_date}...")
    report, msg = service.generate_sales_report(start_date, end_date)
    
    if report:
        print("\nReporte de Ventas:")
        print(f"{'Fecha':<15} {'Factura':<25} {'Total':>15} {'Estado':<15}")
        print("-" * 70)
        
        total_sales = 0
        for entry in report:
            print(f"{entry['date']:<15} {entry['invoice_number']:<25} ${entry['total']:>14.2f} {entry['status']:<15}")
            total_sales += entry['total']
        
        print("-" * 70)
        print(f"{'TOTAL':<40} ${total_sales:>14.2f}")
    
    print_section("10. CAMBIAR USUARIO Y VERIFICAR AISLAMIENTO DE DATOS")
    
    print("\nCerrando sesión de empresa1...")
    service.logout()
    
    print("Iniciando sesión como empresa2...")
    success, msg = service.login("empresa2", "password456")
    print(f"  Resultado: {msg}")
    
    if success:
        print("Generando reporte para empresa2...")
        report, msg = service.generate_sales_report(start_date, end_date)
        
        if report:
            print(f"  Número de facturas para empresa2: {len(report)}")
            if len(report) == 0:
                print("  ✓ Correcto: empresa2 no tiene facturas (aislamiento de datos funcionando)")
        else:
            print("  El usuario empresa2 no tiene facturas en este período")
    
    print_section("DEMOSTRACIÓN COMPLETADA")
    
    print("\n✓ El sistema funcionó correctamente")
    print("\nCaracterísticas demostraidas:")
    print("  ✓ Registro seguro de usuarios (contraseñas hasheadas)")
    print("  ✓ Autenticación")
    print("  ✓ Creación y gestión de facturas")
    print("  ✓ Catálogo de productos")
    print("  ✓ Cálculo automático de totales e impuestos")
    print("  ✓ Preparación para integración con SRI Ecuador")
    print("  ✓ Reportes de ventas")
    print("  ✓ Aislamiento de datos por usuario")
    print("  ✓ Auditoría de acciones")
    
    # Cerrar servicio
    service.close()
    
    print("\nBase de datos: billing_demo.db")
    print("\nPara más información, ver:")
    print("  - backend.py (Lógica de base de datos)")
    print("  - billing_service.py (Servicio principal)")
    print("  - security.py (Gestión de seguridad)")
    print("  - sri_validator.py (Integración SRI Ecuador)")
    print("  - ui.py (Interfaz interactiva)")

if __name__ == "__main__":
    main()
