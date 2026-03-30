"""
Sistema de Facturación - Interfaz de Usuario Interactiva
Este módulo proporciona una interfaz de línea de comandos para el sistema de facturación
"""

from src.services.billing_service import BillingService
from datetime import datetime, timedelta
import os
import sys

class BillingUI:
    """Interfaz de usuario para el sistema de facturación"""
    
    def __init__(self):
        self.service = BillingService()
        self.running = True

    def clear_screen(self):
        """Limpia la pantalla"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title: str):
        """Imprime un encabezado"""
        print("\n" + "="*60)
        print(f"  {title}")
        print("="*60)

    def print_menu(self, options: dict):
        """Imprime un menú de opciones"""
        for key, value in options.items():
            print(f"  {key}. {value}")
        print()

    def main_menu(self):
        """Menú principal"""
        self.clear_screen()
        self.print_header("SISTEMA DE FACTURACIÓN - MENÚ PRINCIPAL")
        
        if not self.service.is_logged_in():
            options = {
                '1': 'Registrar usuario',
                '2': 'Iniciar sesión',
                '3': 'Salir'
            }
            self.print_menu(options)
            
            choice = input("Seleccione una opción: ").strip()
            
            if choice == '1':
                self.register_user()
            elif choice == '2':
                self.login_user()
            elif choice == '3':
                self.running = False
            else:
                print("Opción inválida")
                input("Presione Enter para continuar...")
        else:
            options = {
                '1': 'Crear factura',
                '2': 'Añadir producto',
                '3': 'Añadir item a factura',
                '4': 'Ver resumen de factura',
                '5': 'Enviar factura a SRI',
                '6': 'Generar reporte de ventas',
                '7': 'Cerrar sesión',
                '8': 'Salir'
            }
            self.print_menu(options)
            
            choice = input("Seleccione una opción: ").strip()
            
            if choice == '1':
                self.create_invoice()
            elif choice == '2':
                self.add_product()
            elif choice == '3':
                self.add_invoice_item()
            elif choice == '4':
                self.view_invoice_summary()
            elif choice == '5':
                self.submit_to_sri()
            elif choice == '6':
                self.generate_report()
            elif choice == '7':
                self.service.logout()
            elif choice == '8':
                self.running = False
            else:
                print("Opción inválida")
                input("Presione Enter para continuar...")

    def register_user(self):
        """Registra un nuevo usuario"""
        self.clear_screen()
        self.print_header("REGISTRO DE USUARIO")
        
        username = input("Nombre de usuario: ").strip()
        password = input("Contraseña: ").strip()
        email = input("Email (opcional): ").strip() or None
        ruc = input("RUC Ecuador (opcional): ").strip() or None
        
        success, message = self.service.register(username, password, email, ruc)
        
        print(f"\n{'✓' if success else '✗'} {message}")
        input("Presione Enter para continuar...")

    def login_user(self):
        """Inicia sesión de usuario"""
        self.clear_screen()
        self.print_header("INICIAR SESIÓN")
        
        username = input("Nombre de usuario: ").strip()
        password = input("Contraseña: ").strip()
        
        success, message = self.service.login(username, password)
        
        print(f"\n{'✓' if success else '✗'} {message}")
        input("Presione Enter para continuar...")

    def create_invoice(self):
        """Crea una nueva factura"""
        self.clear_screen()
        self.print_header("CREAR FACTURA")
        
        print("Formato requerido: XXX-XXX-XXXXXXXXXX")
        invoice_number = input("Número de factura: ").strip()
        
        invoice_id, message = self.service.create_invoice(invoice_number)
        
        print(f"\n{'✓' if invoice_id else '✗'} {message}")
        
        if invoice_id:
            print(f"ID de factura: {invoice_id}")
        
        input("Presione Enter para continuar...")

    def add_product(self):
        """Añade un producto"""
        self.clear_screen()
        self.print_header("AÑADIR PRODUCTO")
        
        name = input("Nombre del producto: ").strip()
        
        try:
            price = float(input("Precio: $").strip())
            tax_rate_input = input("Tasa de IVA (0.12 por defecto): ").strip()
            tax_rate = float(tax_rate_input) if tax_rate_input else 0.12
            
            product_id, message = self.service.add_product(name, price, tax_rate)
            
            print(f"\n{'✓' if product_id else '✗'} {message}")
            
            if product_id:
                print(f"ID de producto: {product_id}")
        except ValueError:
            print("\n✗ Valores numéricos inválidos")
        
        input("Presione Enter para continuar...")

    def add_invoice_item(self):
        """Añade un item a una factura"""
        self.clear_screen()
        self.print_header("AÑADIR ITEM A FACTURA")
        
        try:
            invoice_id = int(input("ID de factura: ").strip())
            product_id = int(input("ID de producto: ").strip())
            description = input("Descripción: ").strip()
            quantity = int(input("Cantidad: ").strip())
            unit_price = float(input("Precio unitario: $").strip())
            tax_rate_input = input("Tasa de IVA (0.12 por defecto): ").strip()
            tax_rate = float(tax_rate_input) if tax_rate_input else 0.12
            
            success, message = self.service.add_item_to_invoice(
                invoice_id, product_id, description, quantity, unit_price, tax_rate
            )
            
            print(f"\n{'✓' if success else '✗'} {message}")
        except ValueError:
            print("\n✗ Valores inválidos")
        
        input("Presione Enter para continuar...")

    def view_invoice_summary(self):
        """Ve el resumen de una factura"""
        self.clear_screen()
        self.print_header("RESUMEN DE FACTURA")
        
        try:
            invoice_id = int(input("ID de factura: ").strip())
            
            summary, message = self.service.get_invoice_summary(invoice_id)
            
            if summary:
                invoice = summary['invoice']
                items = summary['items']
                
                print(f"\nFactura #{invoice['invoice_number']}")
                print(f"Fecha: {invoice['date']}")
                print(f"Estado: {invoice['status']}")
                print("-" * 60)
                
                print(f"\n{'Descripción':<40} {'Qty':>6} {'Precio':>10}")
                print("-" * 60)
                
                for item in items:
                    print(f"{item['description']:<40} {item['quantity']:>6} ${item['unit_price']:>9.2f}")
                
                print("-" * 60)
                print(f"Subtotal: ${invoice['subtotal']:.2f}")
                print(f"IVA (12%): ${invoice['tax']:.2f}")
                print(f"TOTAL: ${invoice['total']:.2f}")
                
                if invoice['sri_validation_status']:
                    print(f"\nEstado SRI: {invoice['sri_validation_status']}")
                    if invoice['sri_authorization_code']:
                        print(f"Código de autorización: {invoice['sri_authorization_code']}")
            else:
                print(f"\n✗ {message}")
        except ValueError:
            print("\n✗ ID de factura inválido")
        
        input("\nPresione Enter para continuar...")

    def submit_to_sri(self):
        """Envía una factura al SRI"""
        self.clear_screen()
        self.print_header("ENVIAR FACTURA A SRI")
        
        try:
            invoice_id = int(input("ID de factura: ").strip())
            
            success, message = self.service.submit_to_sri(invoice_id)
            
            print(f"\n{'✓' if success else '✗'} {message}")
        except ValueError:
            print("\n✗ ID de factura inválido")
        
        input("Presione Enter para continuar...")

    def generate_report(self):
        """Genera un reporte de ventas"""
        self.clear_screen()
        self.print_header("REPORTE DE VENTAS")
        
        print("Formato: YYYY-MM-DD")
        start_date = input("Fecha inicio: ").strip() or (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = input("Fecha fin: ").strip() or datetime.now().strftime('%Y-%m-%d')
        
        report, message = self.service.generate_sales_report(start_date, end_date)
        
        if report:
            print(f"\nReporte de {start_date} a {end_date}")
            print("-" * 70)
            
            total_ventas = 0
            
            print(f"{'Fecha':<15} {'Factura':<20} {'Total':>15} {'Estado':<15}")
            print("-" * 70)
            
            for entry in report:
                print(f"{entry['date']:<15} {entry['invoice_number']:<20} ${entry['total']:>14.2f} {entry['status']:<15}")
                total_ventas += entry['total']
            
            print("-" * 70)
            print(f"{'TOTAL VENTAS':<35} ${total_ventas:>14.2f}")
        else:
            print(f"\n✗ {message}")
        
        input("\nPresione Enter para continuar...")

    def run(self):
        """Ejecuta la interfaz"""
        while self.running:
            self.main_menu()
        
        self.service.close()
        print("\n¡Hasta luego!")


def main():
    """Función principal"""
    ui = BillingUI()
    ui.run()


if __name__ == "__main__":
    main()
