#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    SISTEMA DE FACTURACIÓN - INICIO                        ║
║                                                                           ║
║  Sistema profesional de facturación para Ecuador con:                    ║
║  ✓ Seguridad avanzada (contraseñas hasheadas)                          ║
║  ✓ Gestión de múltiples usuarios                                        ║
║  ✓ Facturas con cálculo automático de impuestos                         ║
║  ✓ Integración preparada con SRI Ecuador                                ║
║  ✓ Reportes de ventas                                                   ║
║  ✓ Auditoría de todas las acciones                                      ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import sys
import os

def show_menu():
    """Muestra el menú principal de opciones"""
    print("\n" + "="*70)
    print("  SISTEMA DE FACTURACIÓN - MENÚ PRINCIPAL")
    print("="*70)
    print("\nElige cómo deseas empezar:\n")
    print("  1. Ejecutar la INTERFAZ INTERACTIVA (recomendado)")
    print("     - Menú amigable para crear facturas, productos, reportes")
    print("     - Interacción paso a paso")
    print()
    print("  2. Ejecutar DEMOSTRACIÓN AUTOMÁTICA")
    print("     - Ve todas las funcionalidades en acción")
    print("     - Crea usuarios, facturas y reportes automáticamente")
    print()
    print("  3. Ver DOCUMENTACIÓN (README.md)")
    print("     - Instrucciones detalladas de uso")
    print("     - Estructura del proyecto")
    print("     - Detalles técnicos")
    print()
    print("  4. Salir")
    print()
    print("-"*70)

def main():
    """Función principal"""
    
    # Banner de bienvenida
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  SISTEMA DE FACTURACIÓN PARA ECUADOR".center(68) + "║")
    print("║" + "  Versión 2.0 - Producción Ready".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    while True:
        show_menu()
        
        choice = input("Selecciona una opción (1-4): ").strip()
        
        if choice == '1':
            print("\n⏳ Iniciando interfaz interactiva...")
            print("   (Si hay errores, asegúrate de que estés en la carpeta correcta)\n")
            try:
                from ui import BillingUI
                ui = BillingUI()
                ui.run()
            except ImportError as e:
                print(f"❌ Error: No se puede cargar el módulo ui.py")
                print(f"   Asegúrate de que todos los archivos están en la misma carpeta")
                print(f"   Detalles: {e}")
            except Exception as e:
                print(f"❌ Error al ejecutar la interfaz: {e}")
            break
        
        elif choice == '2':
            print("\n⏳ Ejecutando demostración automática...")
            print("   Esto creará una base de datos de demostración temporal\n")
            try:
                import example
                print("\n✓ Demostración completada exitosamente")
                print("\nLa base de datos de demostración se creó en: billing_demo.db")
            except ImportError as e:
                print(f"❌ Error: No se puede cargar el módulo example.py")
                print(f"   Detalles: {e}")
            except Exception as e:
                print(f"❌ Error al ejecutar la demostración: {e}")
            
            input("\nPresiona Enter para volver al menú...")
        
        elif choice == '3':
            print("\n" + "="*70)
            print("  DOCUMENTACIÓN - README")
            print("="*70)
            
            readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
            
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(content)
                except Exception as e:
                    print(f"Error al leer README.md: {e}")
            else:
                print("\n❌ Archivo README.md no encontrado")
                print("\nPara ver la documentación, abre README.md en tu editor de texto")
            
            input("\nPresiona Enter para volver al menú...")
        
        elif choice == '4':
            print("\n" + "="*70)
            print("  ¡Hasta luego!")
            print("="*70)
            print("\nDocumentación de referencia:")
            print("  - README.md: Información completa del proyecto")
            print("  - Código fuente:")
            print("    • backend.py: Base de datos")
            print("    • billing_service.py: Lógica de negocio")
            print("    • security.py: Seguridad")
            print("    • sri_validator.py: Integración SRI Ecuador")
            print("    • ui.py: Interfaz interactiva")
            print()
            break
        
        else:
            print("\n❌ Opción inválida. Por favor, selecciona 1, 2, 3 o 4")
            input("Presiona Enter para continuar...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Programa interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

