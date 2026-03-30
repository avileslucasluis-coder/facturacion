import logging
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from src.db.database import Database
from src.core.security import SecurityManager
from src.core.sri_validator import SRIValidator
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import lxml.etree as ET
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BillingService:
    """Servicio principal del sistema de facturación"""
    
    def __init__(self, db_name: str = 'billing_system.db'):
        self.db = Database(db_name)
        self.security = SecurityManager()
        self.current_user = None
        self.current_user_id = None
        self.sri_validator = None

    def register(self, username: str, password: str, email: str = None, ruc: str = None, role: str = 'user', company_name: str = None, phone: str = None) -> Tuple[bool, str]:
        """
        Registra un nuevo usuario
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            email: Email del usuario
            ruc: RUC del contribuyente (Ecuador)
            role: Rol del usuario (user/admin)
            company_name: Nombre de la empresa
            phone: Teléfono
            
        Returns:
            (éxito, mensaje)
        """
        try:
            # Validaciones
            if not username or len(username) < 3:
                return False, "Nombre de usuario debe tener al menos 3 caracteres"
            
            if not password or len(password) < 6:
                return False, "Contraseña debe tener al menos 6 caracteres"
            
            if email and not self.security.validate_email(email):
                return False, "Email inválido"
            
            if ruc and not self.security.validate_ruc(ruc):
                return False, "RUC inválido (debe tener 13 dígitos)"
            
            # Hash de contraseña
            password_hash = self.security.hash_password(password)
            
            # Crear usuario
            if self.db.get_user(username):
                return False, "El nombre de usuario ya existe"
            if email and self.db.get_user_by_email(email):
                return False, "El email ya está registrado"

            if self.db.add_user(username, password_hash, email, ruc, role, company_name, phone):
                logger.info(f"Usuario {username} registrado exitosamente")
                return True, "Usuario registrado exitosamente"
            else:
                return False, "Ocurrió un error en registro (posible duplicado)"
        
        except Exception as e:
            logger.error(f"Error en registro: {e}")
            return False, f"Error en registro: {str(e)}"

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Autentica un usuario
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            (éxito, mensaje)
        """
        try:
            user = self.db.get_user(username)
            
            if not user:
                logger.warning(f"Intento de login fallido: usuario {username} no encontrado")
                return False, "Usuario o contraseña inválidos"
            
            if not self.security.verify_password(password, user['password_hash']):
                logger.warning(f"Intento de login fallido: contraseña incorrecta para {username}")
                return False, "Usuario o contraseña inválidos"
            
            self.current_user = user
            self.current_user_id = user['id']
            
            # Inicializar SRI validator si tiene RUC
            if user['ruc']:
                self.sri_validator = SRIValidator(user['ruc'])
            
            self.db.log_audit(user['id'], 'LOGIN', f"Login exitoso")
            logger.info(f"Usuario {username} autenticado")
            return True, "Login exitoso"
        
        except Exception as e:
            logger.error(f"Error en login: {e}")
            return False, f"Error en login: {str(e)}"

    def logout(self):
        """Cierra la sesión del usuario actual"""
        if self.current_user:
            self.db.log_audit(self.current_user_id, 'LOGOUT', 'Logout exitoso')
            self.current_user = None
            self.current_user_id = None
            self.sri_validator = None
            logger.info("Usuario desconectado")

    def is_logged_in(self) -> bool:
        """Verifica si hay un usuario autenticado"""
        return self.current_user is not None

    def create_invoice(self, invoice_number: str) -> Tuple[Optional[int], str]:
        """
        Crea una nueva factura
        
        Args:
            invoice_number: Número de factura (formato: XXX-XXX-XXXXXXXXXX)
            
        Returns:
            (invoice_id, mensaje)
        """
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            
            if not self.security.validate_invoice_number(invoice_number):
                return None, "Formato de factura inválido (debe ser XXX-XXX-XXXXXXXXXX)"
            
            invoice_id = self.db.create_invoice(self.current_user_id, invoice_number)
            
            if invoice_id:
                self.db.log_audit(self.current_user_id, 'CREATE_INVOICE', f"Factura {invoice_number} creada")
                logger.info(f"Factura {invoice_number} creada por usuario {self.current_user['username']}")
                return invoice_id, f"Factura {invoice_number} creada exitosamente"
            else:
                return None, "Error al crear factura (número duplicado)"
        
        except Exception as e:
            logger.error(f"Error creando factura: {e}")
            return None, f"Error al crear factura: {str(e)}"

    def add_product(self, name: str, price: float, tax_rate: float = 0.12) -> Tuple[Optional[int], str]:
        """
        Añade un producto al catálogo del usuario
        
        Args:
            name: Nombre del producto
            price: Precio del producto
            tax_rate: Tasa de IVA (default 12%)
            
        Returns:
            (product_id, mensaje)
        """
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            
            if price <= 0:
                return None, "Precio debe ser mayor a 0"
            
            if tax_rate < 0 or tax_rate > 1:
                return None, "Tasa de impuesto debe estar entre 0 y 1"
            
            product_id = self.db.add_product(self.current_user_id, name, price, tax_rate)
            
            if product_id:
                self.db.log_audit(self.current_user_id, 'ADD_PRODUCT', f"Producto {name} añadido")
                logger.info(f"Producto {name} añadido por usuario {self.current_user['username']}")
                return product_id, f"Producto {name} añadido exitosamente"
            else:
                return None, "Error al añadir producto"
        
        except Exception as e:
            logger.error(f"Error añadiendo producto: {e}")
            return None, f"Error al añadir producto: {str(e)}"

    def list_products(self) -> Tuple[Optional[List[Dict]], str]:
        """Obtiene todos los productos del usuario"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            products = self.db.get_products(self.current_user_id)
            return products, "OK"
        except Exception as e:
            logger.error(f"Error listando productos: {e}")
            return None, f"Error al listar productos: {str(e)}"

    def add_provider(self, name: str, ruc: str, email: str = None, phone: str = None, address: str = None) -> Tuple[Optional[int], str]:
        """Añade un proveedor"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            if not name or len(name) < 2:
                return None, "Nombre de proveedor inválido"
            provider_id = self.db.add_provider(self.current_user_id, name, ruc, email, phone, address)
            if provider_id:
                self.db.log_audit(self.current_user_id, 'ADD_PROVIDER', f"Proveedor {name} añadido")
                return provider_id, "Proveedor añadido exitosamente"
            return None, "Error al añadir proveedor"
        except Exception as e:
            logger.error(f"Error añadiendo proveedor: {e}")
            return None, f"Error al añadir proveedor: {str(e)}"

    def list_providers(self) -> Tuple[Optional[List[Dict]], str]:
        """Obtiene los proveedores"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            providers = self.db.get_providers(self.current_user_id)
            return providers, "OK"
        except Exception as e:
            logger.error(f"Error listando proveedores: {e}")
            return None, f"Error al listar proveedores: {str(e)}"

    def get_users(self) -> Tuple[Optional[List[Dict]], str]:
        """Obtiene todos los usuarios (solo admin)"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            if self.current_user.get('role') != 'admin':
                return None, "Acceso no autorizado, se necesita rol admin"
            users = self.db.get_users()
            return users, "OK"
        except Exception as e:
            logger.error(f"Error listando usuarios: {e}")
            return None, f"Error al listar usuarios: {str(e)}"

    def set_user_role(self, user_id: int, role: str) -> Tuple[bool, str]:
        """Actualiza rol de usuario (solo admin)"""
        try:
            if not self.is_logged_in():
                return False, "Debe hacer login primero"
            if self.current_user.get('role') != 'admin':
                return False, "Acceso no autorizado, se necesita rol admin"
            role = role.lower().strip()
            if role not in ['user', 'admin']:
                return False, "Rol inválido (user/admin)"
            if self.db.set_user_role(user_id, role):
                self.db.log_audit(self.current_user_id, 'SET_USER_ROLE', f"Set role {role} para usuario {user_id}")
                return True, "Rol actualizado"
            return False, "No se pudo actualizar el rol"
        except Exception as e:
            logger.error(f"Error actualizando rol de usuario: {e}")
            return False, f"Error al actualizar rol de usuario: {str(e)}"

    def add_invoice_file(self, provider_id: int, invoice_id: int, filename: str, file_type: str, file_path: str, sri_document_type: str = 'invoice', signature_required: bool = True) -> Tuple[Optional[int], str]:
        """Registra un archivo de factura en la base"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            file_id = self.db.add_invoice_file(self.current_user_id, provider_id, invoice_id, filename, file_type, file_path, sri_document_type, signature_required)
            if file_id:
                self.db.log_audit(self.current_user_id, 'UPLOAD_INVOICE_FILE', f"Archivo {filename} subido")
                return file_id, "Archivo subido exitosamente"
            return None, "Error al subir archivo"
        except Exception as e:
            logger.error(f"Error subiendo archivo: {e}")
            return None, f"Error al subir archivo: {str(e)}"

    def get_uploaded_files(self) -> Tuple[Optional[List[Dict]], str]:
        """Obtiene archivos subidos"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            files = self.db.get_uploaded_files(self.current_user_id)
            return files, "OK"
        except Exception as e:
            logger.error(f"Error obteniendo archivos: {e}")
            return None, f"Error al obtener archivos: {str(e)}"

    def add_inventory_item(self, product_id: int, quantity: int, cost_price: float = None) -> Tuple[Optional[int], str]:
        """Agrega/actualiza inventario"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            if quantity <= 0:
                return None, "Cantidad debe ser mayor a cero"
            # insertar o actualizar inventario
            inventory_id = self.db.add_inventory_item(self.current_user_id, product_id, quantity, cost_price)
            if inventory_id:
                self.db.update_stock(product_id, quantity)
                self.db.log_audit(self.current_user_id, 'ADD_INVENTORY', f"Inventario actualizado para producto {product_id}")
                return inventory_id, "Inventario actualizado"
            return None, "Error al actualizar inventario"
        except Exception as e:
            logger.error(f"Error en inventario: {e}")
            return None, f"Error al actualizar inventario: {str(e)}"

    def get_inventory(self) -> Tuple[Optional[List[Dict]], str]:
        """Obtiene inventario"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            inventory = self.db.get_inventory(self.current_user_id)
            return inventory, "OK"
        except Exception as e:
            logger.error(f"Error obteniendo inventario: {e}")
            return None, f"Error al obtener inventario: {str(e)}"

    def create_subscription(self, plan_name: str, monthly_fee: float, next_billing_date: str, payment_account: str) -> Tuple[Optional[int], str]:
        """Crea suscripción"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            sub_id = self.db.create_subscription(self.current_user_id, plan_name, monthly_fee, next_billing_date, payment_account)
            if sub_id:
                self.db.log_audit(self.current_user_id, 'CREATE_SUBSCRIPTION', f"Suscripción {plan_name} creada")
                return sub_id, "Suscripción creada"
            return None, "Error al crear suscripción"
        except Exception as e:
            logger.error(f"Error creando suscripción: {e}")
            return None, f"Error al crear suscripción: {str(e)}"

    def get_subscriptions(self) -> Tuple[Optional[List[Dict]], str]:
        """Obtiene suscripciones"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            subs = self.db.get_subscriptions(self.current_user_id)
            return subs, "OK"
        except Exception as e:
            logger.error(f"Error obteniendo suscripciones: {e}")
            return None, f"Error al obtener suscripciones: {str(e)}"

    def create_transaction(self, provider_id: Optional[int], invoice_id: Optional[int], type_: str, amount: float, details: str = None) -> Tuple[Optional[int], str]:
        """Crea transacción"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            if amount <= 0:
                return None, "El monto debe ser mayor a 0"
            date = datetime.now().isoformat()
            tx_id = self.db.create_transaction(self.current_user_id, provider_id, invoice_id, type_, amount, date, details)
            if tx_id:
                self.db.log_audit(self.current_user_id, 'CREATE_TRANSACTION', f"Transacción {type_} registrada")
                return tx_id, "Transacción creada"
            return None, "Error al crear transacción"
        except Exception as e:
            logger.error(f"Error creando transacción: {e}")
            return None, f"Error al crear transacción: {str(e)}"

    def get_transactions(self, start_date: str, end_date: str) -> Tuple[Optional[List[Dict]], str]:
        """Obtiene transacciones"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            txs = self.db.get_transactions(self.current_user_id, start_date, end_date)
            return txs, "OK"
        except Exception as e:
            logger.error(f"Error obteniendo transacciones: {e}")
            return None, f"Error al obtener transacciones: {str(e)}"

    def list_invoices(self) -> Tuple[Optional[List[Dict]], str]:
        """Lista facturas del usuario"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            invoices = self.db.get_all_invoices(self.current_user_id)
            return invoices, "OK"
        except Exception as e:
            logger.error(f"Error listando facturas: {e}")
            return None, f"Error al listar facturas: {str(e)}"

    def add_invoice_item(self, invoice_id: int, product_id: Optional[int], description: str, quantity: int, unit_price: float, tax_rate: float = 0.12) -> Tuple[bool, str]:
        """Añade un item a una factura"""
        try:
            if not self.is_logged_in():
                return False, "Debe hacer login primero"

            if quantity <= 0:
                return False, "Cantidad debe ser mayor a 0"

            if unit_price <= 0:
                return False, "Precio unitario debe ser mayor a 0"

            added = self.db.add_invoice_item(invoice_id, product_id, description, quantity, unit_price, tax_rate)
            if not added:
                return False, "Error al añadir item"

            self.db.log_audit(self.current_user_id, 'ADD_INVOICE_ITEM', f"Item añadido a factura {invoice_id}")
            logger.info(f"Item añadido a factura {invoice_id}")
            return True, "Item añadido exitosamente"
        except Exception as e:
            logger.error(f"Error añadiendo item: {e}")
            return False, f"Error al añadir item: {str(e)}"

    def get_invoice_summary(self, invoice_id: int) -> Tuple[Optional[Dict], str]:
        """
        Obtiene el resumen de una factura
        
        Args:
            invoice_id: ID de la factura
            
        Returns:
            (datos de factura, mensaje)
        """
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            
            invoice = self.db.get_invoice(invoice_id)
            
            if not invoice:
                return None, "Factura no encontrada"
            
            items = self.db.get_invoice_items(invoice_id)
            
            summary = {
                'invoice': dict(invoice),
                'items': items
            }
            
            logger.info(f"Resumen de factura {invoice_id} obtenido")
            return summary, "OK"
        
        except Exception as e:
            logger.error(f"Error obteniendo resumen: {e}")
            return None, f"Error al obtener resumen: {str(e)}"

    def finalize_invoice(self, invoice_id: int) -> Tuple[bool, str]:
        """
        Finaliza una factura (cambiar estado a finalizado)
        
        Args:
            invoice_id: ID de la factura
            
        Returns:
            (éxito, mensaje)
        """
        try:
            if not self.is_logged_in():
                return False, "Debe hacer login primero"
            
            if self.db.update_invoice_status(invoice_id, 'finalized'):
                self.db.log_audit(self.current_user_id, 'FINALIZE_INVOICE', f"Factura {invoice_id} finalizada")
                logger.info(f"Factura {invoice_id} finalizada")
                return True, "Factura finalizada exitosamente"
            else:
                return False, "Error al finalizar factura"
        
        except Exception as e:
            logger.error(f"Error finalizando factura: {e}")
            return False, f"Error al finalizar factura: {str(e)}"

    def submit_to_sri(self, invoice_id: int) -> Tuple[bool, str]:
        """
        Envía una factura al SRI para validación
        
        Args:
            invoice_id: ID de la factura
            
        Returns:
            (éxito, mensaje)
        """
        try:
            if not self.is_logged_in():
                return False, "Debe hacer login primero"
            
            if not self.sri_validator:
                return False, "No hay RUC configurado. Configure un RUC en su perfil."
            
            summary, _ = self.get_invoice_summary(invoice_id)
            
            if not summary:
                return False, "Factura no encontrada"
            
            # Generar XML
            invoice_data = {
                'ruc': self.current_user['ruc'],
                'razon_social': self.current_user['username'],
                'subtotal': summary['invoice']['subtotal'],
                'tax': summary['invoice']['tax'],
                'total': summary['invoice']['total'],
                'date': summary['invoice']['date']
            }
            
            invoice_xml = self.sri_validator.generate_invoice_xml(invoice_data)
            
            # Firmar XML (en producción)
            signed_xml = self.sri_validator.sign_invoice(invoice_xml)
            
            # Validar con SRI
            result = self.sri_validator.validate_with_sri(signed_xml)
            
            if result['success']:
                self.db.update_sri_validation(
                    invoice_id,
                    'AUTHORIZED',
                    result.get('authorization_code')
                )
                self.db.update_invoice_status(invoice_id, 'authorized')
                self.db.log_audit(
                    self.current_user_id, 'SUBMIT_SRI',
                    f"Factura {invoice_id} enviada a SRI - Código: {result.get('authorization_code')}"
                )
                logger.info(f"Factura {invoice_id} autorizada por SRI")
                return True, f"Factura autorizada. Código: {result.get('authorization_code')}"
            else:
                self.db.update_sri_validation(invoice_id, 'REJECTED')
                logger.warning(f"Factura {invoice_id} rechazada por SRI")
                return False, f"Error SRI: {result.get('error', 'Error desconocido')}"
        
        except Exception as e:
            logger.error(f"Error enviando a SRI: {e}")
            return False, f"Error al enviar a SRI: {str(e)}"

    def generate_sales_report(self, start_date: str, end_date: str) -> Tuple[Optional[List], str]:
        """
        Genera reporte de ventas
        
        Args:
            start_date: Fecha inicio (YYYY-MM-DD)
            end_date: Fecha fin (YYYY-MM-DD)
            
        Returns:
            (reporte, mensaje)
        """
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            
            report = self.db.get_sales_report(self.current_user_id, start_date, end_date)
            
            self.db.log_audit(
                self.current_user_id, 'GENERATE_REPORT',
                f"Reporte generado de {start_date} a {end_date}"
            )
            logger.info(f"Reporte generado por usuario {self.current_user['username']}")
            return report, "Reporte generado exitosamente"
        
        except Exception as e:
            logger.error(f"Error generando reporte: {e}")
            return None, f"Error al generar reporte: {str(e)}"

    # Nuevos métodos para edición de facturas y documentos adicionales

    def update_invoice(self, invoice_id: int, invoice_number: str = None, date: str = None,
                      document_type: str = None, reference_invoice_id: int = None) -> Tuple[bool, str]:
        """
        Actualiza una factura existente
        
        Args:
            invoice_id: ID de la factura
            invoice_number: Nuevo número (opcional)
            date: Nueva fecha (opcional)
            document_type: Tipo de documento (opcional)
            reference_invoice_id: ID de factura de referencia (opcional)
            
        Returns:
            (éxito, mensaje)
        """
        try:
            if not self.is_logged_in():
                return False, "Debe hacer login primero"
            
            if self.db.update_invoice(invoice_id, invoice_number, date, document_type, reference_invoice_id):
                self.db.log_audit(self.current_user_id, 'UPDATE_INVOICE', f"Factura {invoice_id} actualizada")
                logger.info(f"Factura {invoice_id} actualizada")
                return True, "Factura actualizada exitosamente"
            else:
                return False, "Error al actualizar factura"
        
        except Exception as e:
            logger.error(f"Error actualizando factura: {e}")
            return False, f"Error al actualizar factura: {str(e)}"

    def create_credit_note(self, invoice_number: str, reference_invoice_id: int) -> Tuple[Optional[int], str]:
        """
        Crea una nota de crédito
        
        Args:
            invoice_number: Número de la nota de crédito
            reference_invoice_id: ID de la factura de referencia
            
        Returns:
            (note_id, mensaje)
        """
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            
            if not self.security.validate_invoice_number(invoice_number):
                return None, "Formato de número inválido"
            
            invoice_id = self.db.create_invoice(self.current_user_id, invoice_number)
            
            if invoice_id:
                # Actualizar tipo de documento
                self.db.update_invoice(invoice_id, document_type='credit_note', reference_invoice_id=reference_invoice_id)
                self.db.log_audit(self.current_user_id, 'CREATE_CREDIT_NOTE', f"Nota de crédito {invoice_number} creada")
                logger.info(f"Nota de crédito {invoice_number} creada")
                return invoice_id, f"Nota de crédito {invoice_number} creada exitosamente"
            else:
                return None, "Error al crear nota de crédito"
        
        except Exception as e:
            logger.error(f"Error creando nota de crédito: {e}")
            return None, f"Error al crear nota de crédito: {str(e)}"

    def create_debit_note(self, invoice_number: str, reference_invoice_id: int) -> Tuple[Optional[int], str]:
        """
        Crea una nota de débito
        
        Args:
            invoice_number: Número de la nota de débito
            reference_invoice_id: ID de la factura de referencia
            
        Returns:
            (note_id, mensaje)
        """
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            
            if not self.security.validate_invoice_number(invoice_number):
                return None, "Formato de número inválido"
            
            invoice_id = self.db.create_invoice(self.current_user_id, invoice_number)
            
            if invoice_id:
                # Actualizar tipo de documento
                self.db.update_invoice(invoice_id, document_type='debit_note', reference_invoice_id=reference_invoice_id)
                self.db.log_audit(self.current_user_id, 'CREATE_DEBIT_NOTE', f"Nota de débito {invoice_number} creada")
                logger.info(f"Nota de débito {invoice_number} creada")
                return invoice_id, f"Nota de débito {invoice_number} creada exitosamente"
            else:
                return None, "Error al crear nota de débito"
        
        except Exception as e:
            logger.error(f"Error creando nota de débito: {e}")
            return None, f"Error al crear nota de débito: {str(e)}"

    def create_retention(self, retention_number: str, retention_type: str, provider_ruc: str, 
                        provider_name: str, date: str, invoice_id: int = None) -> Tuple[Optional[int], str]:
        """
        Crea una retención (Form 104 o 103)
        
        Args:
            retention_number: Número de retención
            retention_type: 'income' (104) o 'purchase' (103)
            provider_ruc: RUC del proveedor
            provider_name: Nombre del proveedor
            date: Fecha de retención
            invoice_id: ID de factura relacionada (opcional)
            
        Returns:
            (retention_id, mensaje)
        """
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            
            if retention_type not in ['income', 'purchase']:
                return None, "Tipo de retención inválido (debe ser 'income' o 'purchase')"

            if not provider_ruc or not self.security.validate_ruc(provider_ruc):
                return None, "RUC de proveedor inválido (debe ser 13 dígitos numéricos)"
            
            retention_id = self.db.create_retention(
                self.current_user_id, retention_number, retention_type, 
                provider_ruc, provider_name, date, invoice_id
            )
            
            if retention_id:
                self.db.log_audit(self.current_user_id, 'CREATE_RETENTION', f"Retención {retention_number} creada")
                logger.info(f"Retención {retention_number} creada")
                return retention_id, f"Retención {retention_number} creada exitosamente"
            else:
                return None, "Error al crear retención"
        
        except Exception as e:
            logger.error(f"Error creando retención: {e}")
            return None, f"Error al crear retención: {str(e)}"

    def add_retention_item(self, retention_id: int, tax_type: str, tax_rate: float, 
                          base_amount: float, retained_amount: float) -> Tuple[bool, str]:
        """
        Añade un item a una retención
        
        Args:
            retention_id: ID de la retención
            tax_type: Tipo de impuesto (IVA, RENTA, etc.)
            tax_rate: Tasa de retención
            base_amount: Monto base
            retained_amount: Monto retenido
            
        Returns:
            (éxito, mensaje)
        """
        try:
            if not self.is_logged_in():
                return False, "Debe hacer login primero"
            
            if self.db.add_retention_item(retention_id, tax_type, tax_rate, base_amount, retained_amount):
                self.db.log_audit(self.current_user_id, 'ADD_RETENTION_ITEM', f"Item añadido a retención {retention_id}")
                logger.info(f"Item añadido a retención {retention_id}")
                return True, "Item añadido exitosamente"
            else:
                return False, "Error al añadir item"
        
        except Exception as e:
            logger.error(f"Error añadiendo item de retención: {e}")
            return False, f"Error al añadir item: {str(e)}"

    def list_retentions(self) -> Tuple[Optional[List[Dict]], str]:
        """Lista retenciones del usuario"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            retentions = self.db.get_retentions(self.current_user_id)
            return retentions, "OK"
        except Exception as e:
            logger.error(f"Error listando retenciones: {e}")
            return None, f"Error al listar retenciones: {str(e)}"

    def get_retention_summary(self, retention_id: int) -> Tuple[Optional[Dict], str]:
        """Obtiene el resumen de una retención"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            
            # Obtener retención
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT * FROM retentions WHERE id = ?', (retention_id,))
            retention = cursor.fetchone()
            
            if not retention:
                return None, "Retención no encontrada"
            
            items = self.db.get_retention_items(retention_id)
            
            summary = {
                'retention': dict(retention),
                'items': items
            }
            
            return summary, "OK"
        
        except Exception as e:
            logger.error(f"Error obteniendo resumen de retención: {e}")
            return None, f"Error al obtener resumen: {str(e)}"

    def get_inventory_aggregation(self) -> Tuple[Optional[List[Dict]], str]:
        """Agrega el inventario por producto"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"

            inventory = self.db.aggregate_inventory(self.current_user_id)
            return inventory, "OK"
        except Exception as e:
            logger.error(f"Error agrupando inventario: {e}")
            return None, f"Error al agrupar inventario: {str(e)}"

    def get_purchase_sales_report(self, start_date: str, end_date: str) -> Tuple[Optional[Dict], str]:
        """Reporte Form 103/104 (compras y ventas)"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"

            report = self.db.get_purchase_sales_report(self.current_user_id, start_date, end_date)
            return report, "OK"
        except Exception as e:
            logger.error(f"Error obteniendo reporte de compras/ventas: {e}")
            return None, f"Error al generar reporte: {str(e)}"

    def get_retention_report(self, start_date: str, end_date: str, report_type: str = None, provider_ruc: str = None) -> Tuple[Optional[Dict], str]:
        """Reporte unificado 103/104"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"

            if report_type not in ['103', '104', None]:
                return None, "Tipo de reporte inválido (103 o 104)"

            retention_type = None
            if report_type == '103':
                retention_type = 'purchase'
            elif report_type == '104':
                retention_type = 'income'

            if provider_ruc and not self.security.validate_ruc(provider_ruc):
                return None, "RUC inválido (13 dígitos numéricos)"

            report = self.db.get_retention_report(self.current_user_id, start_date, end_date, retention_type, provider_ruc)

            # Aplicar reglas fiscales de Ecuador (ejemplo: top check)
            for r in report.get('retentions', []):
                r['ruc_valid'] = self.security.validate_ruc(r.get('provider_ruc', ''))
                # Regla arbitraria: si compra es tipo juridico debe empezar con 99
                if r['ruc_valid'] and r['provider_ruc'].startswith('99'):
                    r['fiscal_type'] = 'Jurídico'
                elif r['ruc_valid'] and r['provider_ruc'].startswith('10'):
                    r['fiscal_type'] = 'Natural'
                else:
                    r['fiscal_type'] = 'Otros'

            report['rules'] = {
                'ruc_rule': 'RUC 13 dígitos numericos',
                'note': 'Retenciones 103 = compras / 104 = ingresos'
            }

            return report, "OK"
        except Exception as e:
            logger.error(f"Error obteniendo reporte de retenciones: {e}")
            return None, f"Error al generar reporte: {str(e)}"

    def bulk_upload_invoices(self, file_content: str) -> Tuple[Optional[List[Dict]], str]:
        """Carga masiva de facturas desde archivo de texto"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"

            results = self.db.bulk_upload_invoices_txt(self.current_user_id, file_content)
            return results, "OK"
        except Exception as e:
            logger.error(f"Error en carga masiva: {e}")
            return None, f"Error al cargar las facturas: {str(e)}"

    def sign_and_validate_invoice(self, invoice_id: int) -> Tuple[Optional[Dict], str]:
        """Firma y valida factura contra SRI"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"

            invoice = self.db.get_invoice(invoice_id)
            if not invoice:
                return None, "Factura no encontrada"

            items = self.db.get_invoice_items(invoice_id)
            invoice_data = {
                'invoice_number': invoice['invoice_number'],
                'date': invoice['date'],
                'subtotal': invoice['subtotal'],
                'tax': invoice['tax'],
                'total': invoice['total'],
                'items': items,
                'ruc': self.current_user.get('ruc', ''),
                'razon_social': self.current_user.get('company_name', ''),
                'buyer_name': invoice.get('buyer_name', 'Cliente')
            }

            if not self.sri_validator:
                self.sri_validator = SRIValidator(self.current_user.get('ruc', ''))

            xml = self.sri_validator.generate_invoice_xml(invoice_data)
            signed_xml = self.sri_validator.sign_invoice(xml)
            sri_response = self.sri_validator.validate_with_sri(signed_xml)

            if sri_response.get('success'):
                self.db.update_sri_validation(invoice_id, 'AUTHORIZED', sri_response.get('authorization_code'))
                self.db.log_audit(self.current_user_id, 'SRI_VALIDATE', f"Factura {invoice_id} autorizada {sri_response.get('authorization_code')}")
                return sri_response, "Factura validada con SRI"

            return sri_response, "Error en validación SRI"
        except Exception as e:
            logger.error(f"Error en firma/validación SRI: {e}")
            return None, f"Error en SRI: {str(e)}"

    def create_emission_sheet(self, establishment_code: str, emission_point: str, document_type: str,
                            start_number: int, end_number: int, sri_authorization_code: str,
                            valid_from: str, valid_until: str) -> Tuple[Optional[int], str]:
        """
        Crea una hoja de emisión para secuencia de documentos
        
        Args:
            establishment_code: Código de establecimiento (3 dígitos)
            emission_point: Punto de emisión (3 dígitos)
            document_type: Tipo de documento
            start_number: Número inicial
            end_number: Número final
            sri_authorization_code: Código de autorización SRI
            valid_from: Fecha de inicio de validez
            valid_until: Fecha de fin de validez
            
        Returns:
            (sheet_id, mensaje)
        """
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            
            sheet_id = self.db.create_emission_sheet(
                self.current_user_id, establishment_code, emission_point, document_type,
                start_number, end_number, sri_authorization_code, valid_from, valid_until
            )
            
            if sheet_id:
                self.db.log_audit(self.current_user_id, 'CREATE_EMISSION_SHEET', f"Hoja de emisión {document_type} creada")
                logger.info(f"Hoja de emisión {document_type} creada")
                return sheet_id, "Hoja de emisión creada exitosamente"
            else:
                return None, "Error al crear hoja de emisión"
        
        except Exception as e:
            logger.error(f"Error creando hoja de emisión: {e}")
            return None, f"Error al crear hoja de emisión: {str(e)}"

    def get_emission_sheets(self, document_type: str = None) -> Tuple[Optional[List[Dict]], str]:
        """Obtiene hojas de emisión"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            sheets = self.db.get_emission_sheets(self.current_user_id, document_type)
            return sheets, "OK"
        except Exception as e:
            logger.error(f"Error obteniendo hojas de emisión: {e}")
            return None, f"Error al obtener hojas de emisión: {str(e)}"

    def get_next_document_number(self, document_type: str) -> Tuple[Optional[str], str]:
        """Obtiene el siguiente número de documento disponible"""
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            
            number = self.db.get_next_document_number(self.current_user_id, document_type)
            
            if number:
                return number, "Número obtenido exitosamente"
            else:
                return None, "No hay números disponibles en las hojas de emisión activas"
        
        except Exception as e:
            logger.error(f"Error obteniendo número de documento: {e}")
            return None, f"Error al obtener número: {str(e)}"

    def generate_pdf(self, document_id: int, document_type: str = 'invoice') -> Tuple[Optional[str], str]:
        """
        Genera PDF para factura o retención
        
        Args:
            document_id: ID del documento
            document_type: 'invoice', 'retention', 'credit_note', 'debit_note'
            
        Returns:
            (file_path, mensaje)
        """
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            
            if document_type == 'invoice':
                summary, msg = self.get_invoice_summary(document_id)
                if not summary:
                    return None, msg
                document = summary['invoice']
                items = summary['items']
                title = f"Factura {document['invoice_number']}"
            elif document_type == 'retention':
                summary, msg = self.get_retention_summary(document_id)
                if not summary:
                    return None, msg
                document = summary['retention']
                items = summary['items']
                title = f"Retención {document['retention_number']}"
            else:
                return None, "Tipo de documento no soportado"
            
            # Crear directorio si no existe
            output_dir = f"pdfs/{self.current_user['username']}"
            os.makedirs(output_dir, exist_ok=True)
            
            filename = f"{document_type}_{document_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(output_dir, filename)
            
            # Generar PDF
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Título
            story.append(Paragraph(title, styles['Title']))
            story.append(Spacer(1, 12))
            
            # Información del documento
            info_data = [
                ['Fecha:', document.get('date', '')],
                ['Usuario:', self.current_user['username']],
                ['RUC:', self.current_user.get('ruc', '')],
            ]
            
            if document_type == 'invoice':
                info_data.extend([
                    ['Subtotal:', f"${document.get('subtotal', 0):.2f}"],
                    ['IVA:', f"${document.get('tax', 0):.2f}"],
                    ['Total:', f"${document.get('total', 0):.2f}"],
                ])
            elif document_type == 'retention':
                info_data.extend([
                    ['Tipo:', 'Ingreso' if document.get('retention_type') == 'income' else 'Compra'],
                    ['Proveedor:', document.get('provider_name', '')],
                    ['RUC Proveedor:', document.get('provider_ruc', '')],
                    ['Total Retenido:', f"${document.get('total_retained', 0):.2f}"],
                ])
            
            info_table = Table(info_data, colWidths=[100, 200])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(info_table)
            story.append(Spacer(1, 12))
            
            # Tabla de items
            if items:
                if document_type == 'invoice':
                    item_headers = ['Descripción', 'Cantidad', 'Precio Unit.', 'Subtotal', 'IVA', 'Total']
                else:
                    item_headers = ['Tipo Impuesto', 'Tasa', 'Base', 'Retenido']
                
                item_data = [item_headers]
                
                for item in items:
                    if document_type == 'invoice':
                        item_data.append([
                            item.get('description', ''),
                            str(item.get('quantity', 0)),
                            f"${item.get('unit_price', 0):.2f}",
                            f"${item.get('subtotal', 0):.2f}",
                            f"${item.get('tax', 0):.2f}",
                            f"${item.get('total', 0):.2f}"
                        ])
                    else:
                        item_data.append([
                            item.get('tax_type', ''),
                            f"{item.get('tax_rate', 0)*100:.1f}%",
                            f"${item.get('base_amount', 0):.2f}",
                            f"${item.get('retained_amount', 0):.2f}"
                        ])
                
                item_table = Table(item_data, colWidths=[100, 60, 80, 80, 60, 80] if document_type == 'invoice' else [120, 60, 80, 80])
                item_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(item_table)
            
            doc.build(story)
            
            self.db.log_audit(self.current_user_id, 'GENERATE_PDF', f"PDF generado para {document_type} {document_id}")
            logger.info(f"PDF generado: {filepath}")
            return filepath, "PDF generado exitosamente"
            
        except Exception as e:
            logger.error(f"Error generando PDF: {e}")
            return None, f"Error al generar PDF: {str(e)}"

    def generate_xml(self, document_id: int, document_type: str = 'invoice') -> Tuple[Optional[str], str]:
        """
        Genera XML para SRI
        
        Args:
            document_id: ID del documento
            document_type: 'invoice', 'retention', 'credit_note', 'debit_note'
            
        Returns:
            (file_path, mensaje)
        """
        try:
            if not self.is_logged_in():
                return None, "Debe hacer login primero"
            
            if document_type == 'invoice':
                summary, msg = self.get_invoice_summary(document_id)
                if not summary:
                    return None, msg
                document = summary['invoice']
                items = summary['items']
            elif document_type == 'retention':
                summary, msg = self.get_retention_summary(document_id)
                if not summary:
                    return None, msg
                document = summary['retention']
                items = summary['items']
            else:
                return None, "Tipo de documento no soportado para XML"
            
            # Crear directorio si no existe
            output_dir = f"xmls/{self.current_user['username']}"
            os.makedirs(output_dir, exist_ok=True)
            
            filename = f"{document_type}_{document_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
            filepath = os.path.join(output_dir, filename)
            
            # Crear XML
            if document_type == 'invoice':
                root = ET.Element("factura")
                ET.SubElement(root, "numero").text = document.get('invoice_number', '')
                ET.SubElement(root, "fecha").text = document.get('date', '')
                ET.SubElement(root, "ruc").text = self.current_user.get('ruc', '')
                ET.SubElement(root, "subtotal").text = str(document.get('subtotal', 0))
                ET.SubElement(root, "iva").text = str(document.get('tax', 0))
                ET.SubElement(root, "total").text = str(document.get('total', 0))
                
                items_elem = ET.SubElement(root, "items")
                for item in items:
                    item_elem = ET.SubElement(items_elem, "item")
                    ET.SubElement(item_elem, "descripcion").text = item.get('description', '')
                    ET.SubElement(item_elem, "cantidad").text = str(item.get('quantity', 0))
                    ET.SubElement(item_elem, "precio_unitario").text = str(item.get('unit_price', 0))
                    ET.SubElement(item_elem, "subtotal").text = str(item.get('subtotal', 0))
                    ET.SubElement(item_elem, "iva").text = str(item.get('tax', 0))
                    ET.SubElement(item_elem, "total").text = str(item.get('total', 0))
                    
            elif document_type == 'retention':
                root = ET.Element("retencion")
                ET.SubElement(root, "numero").text = document.get('retention_number', '')
                ET.SubElement(root, "tipo").text = document.get('retention_type', '')
                ET.SubElement(root, "fecha").text = document.get('date', '')
                ET.SubElement(root, "ruc_contribuyente").text = self.current_user.get('ruc', '')
                ET.SubElement(root, "ruc_proveedor").text = document.get('provider_ruc', '')
                ET.SubElement(root, "nombre_proveedor").text = document.get('provider_name', '')
                ET.SubElement(root, "total_retenido").text = str(document.get('total_retained', 0))
                
                items_elem = ET.SubElement(root, "impuestos")
                for item in items:
                    item_elem = ET.SubElement(items_elem, "impuesto")
                    ET.SubElement(item_elem, "tipo").text = item.get('tax_type', '')
                    ET.SubElement(item_elem, "tasa").text = str(item.get('tax_rate', 0))
                    ET.SubElement(item_elem, "base").text = str(item.get('base_amount', 0))
                    ET.SubElement(item_elem, "retenido").text = str(item.get('retained_amount', 0))
            
            # Escribir archivo
            tree = ET.ElementTree(root)
            tree.write(filepath, encoding='utf-8', xml_declaration=True, pretty_print=True)
            
            self.db.log_audit(self.current_user_id, 'GENERATE_XML', f"XML generado para {document_type} {document_id}")
            logger.info(f"XML generado: {filepath}")
            return filepath, "XML generado exitosamente"
            
        except Exception as e:
            logger.error(f"Error generando XML: {e}")
            return None, f"Error al generar XML: {str(e)}"

    def close(self):
        """Cierra la conexión con la base de datos"""
        self.db.close()
