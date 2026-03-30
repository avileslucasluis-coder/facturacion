import sqlite3
from datetime import datetime
from typing import Optional, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    """Maneja todas las operaciones de base de datos"""
    
    def __init__(self, db_name='data/billing_system.db'):
        self.db_name = db_name
        self.conn = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Conecta a la base de datos"""
        try:
            self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Conectado a {self.db_name}")
        except sqlite3.Error as e:
            logger.error(f"Error al conectar: {e}")
            raise

    def create_tables(self):
        """Crea las tablas necesarias"""
        try:
            with self.conn:
                # Tabla de usuarios
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        email TEXT UNIQUE,
                        ruc TEXT UNIQUE,
                        role TEXT DEFAULT 'user',
                        company_name TEXT,
                        phone TEXT,
                        is_active INTEGER DEFAULT 1,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Tabla de proveedores (suppliers)
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS providers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        name TEXT NOT NULL,
                        ruc TEXT,
                        email TEXT,
                        phone TEXT,
                        address TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )
                ''')
                
                # Tabla de facturas (actualizada para tipos de documento)
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS invoices (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        document_type TEXT DEFAULT 'invoice',  -- invoice, credit_note, debit_note
                        invoice_number TEXT UNIQUE NOT NULL,
                        date TEXT NOT NULL,
                        subtotal REAL DEFAULT 0,
                        tax REAL DEFAULT 0,
                        total REAL DEFAULT 0,
                        status TEXT DEFAULT 'draft',
                        sri_validation_status TEXT,
                        sri_authorization_code TEXT,
                        sri_document_type TEXT DEFAULT 'invoice',
                        reference_invoice_id INTEGER,  -- Para notas de crédito/débito
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id),
                        FOREIGN KEY(reference_invoice_id) REFERENCES invoices(id)
                    )
                ''')
                
                # Tabla de productos
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        price REAL NOT NULL,
                        tax_rate REAL DEFAULT 0.12,
                        stock INTEGER DEFAULT 0,
                        min_stock INTEGER DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )
                ''')

                # Tabla de items de factura
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS invoice_items (
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
                ''')

                # Tabla de archivos de facturas (pdf, txt)
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS invoice_files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        provider_id INTEGER,
                        invoice_id INTEGER,
                        filename TEXT NOT NULL,
                        file_type TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        sri_document_type TEXT DEFAULT 'invoice',
                        signature_required INTEGER DEFAULT 1,
                        signed INTEGER DEFAULT 0,
                        FOREIGN KEY(user_id) REFERENCES users(id),
                        FOREIGN KEY(provider_id) REFERENCES providers(id),
                        FOREIGN KEY(invoice_id) REFERENCES invoices(id)
                    )
                ''')

                # Tabla de inventario
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS inventory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        product_id INTEGER NOT NULL,
                        quantity INTEGER NOT NULL,
                        cost_price REAL,
                        last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id),
                        FOREIGN KEY(product_id) REFERENCES products(id)
                    )
                ''')

                # Tabla de suscripciones
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS subscriptions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        plan_name TEXT NOT NULL,
                        status TEXT DEFAULT 'active',
                        monthly_fee REAL NOT NULL,
                        start_date TEXT NOT NULL,
                        next_billing_date TEXT NOT NULL,
                        payment_account TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )
                ''')

                # Tabla de transacciones (compras/ventas)
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        provider_id INTEGER,
                        invoice_id INTEGER,
                        type TEXT NOT NULL,
                        amount REAL NOT NULL,
                        date TEXT NOT NULL,
                        details TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id),
                        FOREIGN KEY(provider_id) REFERENCES providers(id),
                        FOREIGN KEY(invoice_id) REFERENCES invoices(id)
                    )
                ''')

                # Tabla de auditoría
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS audit_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        action TEXT NOT NULL,
                        details TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )
                ''')
                
                # Tabla de retenciones (Form 104 y 103)
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS retentions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        retention_number TEXT UNIQUE NOT NULL,
                        retention_type TEXT NOT NULL,  -- 'income' (104) o 'purchase' (103)
                        invoice_id INTEGER,  -- Factura relacionada
                        provider_ruc TEXT NOT NULL,
                        provider_name TEXT NOT NULL,
                        date TEXT NOT NULL,
                        total_retained REAL DEFAULT 0,
                        status TEXT DEFAULT 'draft',
                        sri_validation_status TEXT,
                        sri_authorization_code TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id),
                        FOREIGN KEY(invoice_id) REFERENCES invoices(id)
                    )
                ''')

                # Tabla de items de retención
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS retention_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        retention_id INTEGER NOT NULL,
                        tax_type TEXT NOT NULL,  -- IVA, RENTA, etc.
                        tax_rate REAL NOT NULL,
                        base_amount REAL NOT NULL,
                        retained_amount REAL NOT NULL,
                        FOREIGN KEY(retention_id) REFERENCES retentions(id)
                    )
                ''')

                # Tabla de hojas de emisión
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS emission_sheets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        establishment_code TEXT NOT NULL,  -- Código de establecimiento (3 dígitos)
                        emission_point TEXT NOT NULL,      -- Punto de emisión (3 dígitos)
                        document_type TEXT NOT NULL,       -- invoice, retention, credit_note, etc.
                        start_number INTEGER NOT NULL,
                        end_number INTEGER NOT NULL,
                        current_number INTEGER DEFAULT 0,
                        sri_authorization_code TEXT,
                        valid_from TEXT,
                        valid_until TEXT,
                        is_active INTEGER DEFAULT 1,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )
                ''')
                
            logger.info("Tablas creadas exitosamente")
        except sqlite3.Error as e:
            logger.error(f"Error creando tablas: {e}")
            raise

    def add_user(self, username: str, password_hash: str, email: str = None, ruc: str = None, role: str = 'user', company_name: str = None, phone: str = None) -> bool:
        """Añade un nuevo usuario"""
        try:
            with self.conn:
                self.conn.execute(
                    'INSERT INTO users (username, password_hash, email, ruc, role, company_name, phone) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (username, password_hash, email, ruc, role, company_name, phone)
                )
            logger.info(f"Usuario {username} registrado con rol {role}")
            return True
        except sqlite3.IntegrityError as e:
            logger.error(f"Error al registrar usuario: {e}")
            return False

    def get_user(self, username: str) -> Optional[dict]:
        """Obtiene un usuario por nombre de usuario"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except sqlite3.Error as e:
            logger.error(f"Error al obtener usuario: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Obtiene un usuario por email"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except sqlite3.Error as e:
            logger.error(f"Error al obtener usuario por email: {e}")
            return None

    def get_users(self) -> List[dict]:
        """Obtiene todos los usuarios"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id, username, email, ruc, role, company_name, phone, is_active, created_at FROM users ORDER BY username')
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error al listar usuarios: {e}")
            return []

    def set_user_role(self, user_id: int, role: str) -> bool:
        """Actualiza el rol de un usuario"""
        try:
            with self.conn:
                self.conn.execute('UPDATE users SET role = ? WHERE id = ?', (role, user_id))
            return True
        except sqlite3.Error as e:
            logger.error(f"Error al actualizar rol de usuario: {e}")
            return False

    def create_invoice(self, user_id: int, invoice_number: str) -> Optional[int]:
        """Crea una nueva factura"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(
                    'INSERT INTO invoices (user_id, invoice_number, date, status) VALUES (?, ?, ?, ?)',
                    (user_id, invoice_number, datetime.now().isoformat(), 'draft')
                )
                invoice_id = cursor.lastrowid
            logger.info(f"Factura {invoice_number} creada")
            return invoice_id
        except sqlite3.IntegrityError as e:
            logger.error(f"Error al crear factura: {e}")
            return None

    def add_product(self, user_id: int, name: str, price: float, tax_rate: float = 0.12) -> Optional[int]:
        """Añade un producto"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(
                    'INSERT INTO products (user_id, name, price, tax_rate) VALUES (?, ?, ?, ?)',
                    (user_id, name, price, tax_rate)
                )
                product_id = cursor.lastrowid
            logger.info(f"Producto {name} añadido")
            return product_id
        except sqlite3.Error as e:
            logger.error(f"Error al añadir producto: {e}")
            return None

    def get_products(self, user_id: int) -> List[dict]:
        """Obtiene todos los productos"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM products WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error al obtener productos: {e}")
            return []

    def add_invoice_item(self, invoice_id: int, product_id: int, description: str, 
                        quantity: int, unit_price: float, tax_rate: float = 0.12) -> bool:
        """Añade un item a una factura"""
        try:
            subtotal = quantity * unit_price
            tax = subtotal * tax_rate
            total = subtotal + tax
            
            with self.conn:
                self.conn.execute(
                    '''INSERT INTO invoice_items 
                       (invoice_id, product_id, description, quantity, unit_price, subtotal, tax, total)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (invoice_id, product_id, description, quantity, unit_price, subtotal, tax, total)
                )
                
                # Actualizar totales de la factura
                self._update_invoice_totals(invoice_id)
            
            logger.info(f"Item añadido a factura {invoice_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error al añadir item: {e}")
            return False

    def _update_invoice_totals(self, invoice_id: int):
        """Actualiza los totales de una factura"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT COALESCE(SUM(subtotal), 0) as subtotal, COALESCE(SUM(tax), 0) as tax FROM invoice_items WHERE invoice_id = ?',
            (invoice_id,)
        )
        result = cursor.fetchone()
        subtotal = result[0]
        tax = result[1]
        total = subtotal + tax
        
        self.conn.execute(
            'UPDATE invoices SET subtotal = ?, tax = ?, total = ? WHERE id = ?',
            (subtotal, tax, total, invoice_id)
        )

    def get_invoice(self, invoice_id: int) -> Optional[dict]:
        """Obtiene una factura"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM invoices WHERE id = ?', (invoice_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except sqlite3.Error as e:
            logger.error(f"Error al obtener factura: {e}")
            return None

    def get_invoice_items(self, invoice_id: int) -> List[dict]:
        """Obtiene los items de una factura"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM invoice_items WHERE invoice_id = ?', (invoice_id,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error al obtener items: {e}")
            return []

    def get_sales_report(self, user_id: int, start_date: str, end_date: str) -> List[dict]:
        """Genera reporte de ventas"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT date, invoice_number, total, status
                FROM invoices
                WHERE user_id = ? AND date BETWEEN ? AND ?
                ORDER BY date DESC
            ''', (user_id, start_date, end_date))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error al generar reporte: {e}")
            return []

    def get_all_invoices(self, user_id: int) -> List[dict]:
        """Obtiene todas las facturas de un usuario"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM invoices WHERE user_id = ? ORDER BY date DESC', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error al obtener todas las facturas: {e}")
            return []

    def add_provider(self, user_id: int, name: str, ruc: str, email: str = None, phone: str = None, address: str = None) -> Optional[int]:
        """Añade un proveedor"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(
                    'INSERT INTO providers (user_id, name, ruc, email, phone, address) VALUES (?, ?, ?, ?, ?, ?)',
                    (user_id, name, ruc, email, phone, address)
                )
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error al añadir proveedor: {e}")
            return None

    def get_providers(self, user_id: int) -> List[dict]:
        """Obtiene proveedores"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM providers WHERE user_id = ?', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error al obtener proveedores: {e}")
            return []

    def add_invoice_file(self, user_id: int, provider_id: Optional[int], invoice_id: Optional[int], filename: str, file_type: str, file_path: str, sri_document_type: str, signature_required: bool = True) -> Optional[int]:
        """Guarda registro de archivo de factura"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(
                    'INSERT INTO invoice_files (user_id, provider_id, invoice_id, filename, file_type, file_path, sri_document_type, signature_required) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    (user_id, provider_id, invoice_id, filename, file_type, file_path, sri_document_type, 1 if signature_required else 0)
                )
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error al guardar archivo de factura: {e}")
            return None

    def get_uploaded_files(self, user_id: int) -> List[dict]:
        """Obtiene todos los archivos subidos"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM invoice_files WHERE user_id = ? ORDER BY uploaded_at DESC', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error al obtener archivos subidos: {e}")
            return []

    def update_stock(self, product_id: int, change_quantity: int) -> bool:
        """Actualiza el stock de un producto"""
        try:
            with self.conn:
                self.conn.execute(
                    'UPDATE products SET stock = stock + ?, updated_at = ? WHERE id = ?',
                    (change_quantity, datetime.now().isoformat(), product_id)
                )
            return True
        except sqlite3.Error as e:
            logger.error(f"Error al actualizar stock: {e}")
            return False

    def get_inventory(self, user_id: int) -> List[dict]:
        """Obtiene el inventario"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT i.*, p.name, p.price FROM inventory i JOIN products p ON i.product_id = p.id WHERE i.user_id = ?', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error al obtener inventario: {e}")
            return []

    def add_inventory_item(self, user_id: int, product_id: int, quantity: int, cost_price: float = None) -> Optional[int]:
        """Añade o actualiza un elemento de inventario"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute('SELECT id, quantity FROM inventory WHERE user_id = ? AND product_id = ?', (user_id, product_id))
                existing = cursor.fetchone()
                if existing:
                    new_quantity = existing['quantity'] + quantity
                    self.conn.execute(
                        'UPDATE inventory SET quantity = ?, cost_price = ?, last_updated = ? WHERE id = ?',
                        (new_quantity, cost_price if cost_price is not None else existing['cost_price'], datetime.now().isoformat(), existing['id'])
                    )
                    return existing['id']

                cursor.execute(
                    'INSERT INTO inventory (user_id, product_id, quantity, cost_price, last_updated) VALUES (?, ?, ?, ?, ?)',
                    (user_id, product_id, quantity, cost_price, datetime.now().isoformat())
                )
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error al añadir inventario: {e}")
            return None

    def create_subscription(self, user_id: int, plan_name: str, monthly_fee: float, next_billing_date: str, payment_account: str) -> Optional[int]:
        """Crea suscripción mensual"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(
                    'INSERT INTO subscriptions (user_id, plan_name, monthly_fee, start_date, next_billing_date, payment_account) VALUES (?, ?, ?, ?, ?, ?)',
                    (user_id, plan_name, monthly_fee, datetime.now().date().isoformat(), next_billing_date, payment_account)
                )
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error al crear suscripción: {e}")
            return None

    def get_subscriptions(self, user_id: int) -> List[dict]:
        """Obtiene suscripciones"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM subscriptions WHERE user_id = ?', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error al obtener suscripciones: {e}")
            return []

    def create_transaction(self, user_id: int, provider_id: Optional[int], invoice_id: Optional[int], type_: str, amount: float, date: str, details: str = None) -> Optional[int]:
        """Registra una transacción de compra/venta"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(
                    'INSERT INTO transactions (user_id, provider_id, invoice_id, type, amount, date, details) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (user_id, provider_id, invoice_id, type_, amount, date, details)
                )
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error al crear transacción: {e}")
            return None

    def get_transactions(self, user_id: int, start_date: str, end_date: str) -> List[dict]:
        """Obtiene las transacciones entre fechas"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM transactions WHERE user_id = ? AND date BETWEEN ? AND ? ORDER BY date DESC', (user_id, start_date, end_date))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error al obtener transacciones: {e}")
            return []

    def update_invoice_status(self, invoice_id: int, status: str) -> bool:
        """Actualiza el estado de una factura"""
        try:
            with self.conn:
                self.conn.execute('UPDATE invoices SET status = ? WHERE id = ?', (status, invoice_id))
            return True
        except sqlite3.Error as e:
            logger.error(f"Error al actualizar estado: {e}")
            return False

    def update_sri_validation(self, invoice_id: int, status: str, auth_code: str = None) -> bool:
        """Actualiza la validación SRI de una factura"""
        try:
            with self.conn:
                self.conn.execute(
                    'UPDATE invoices SET sri_validation_status = ?, sri_authorization_code = ? WHERE id = ?',
                    (status, auth_code, invoice_id)
                )
            return True
        except sqlite3.Error as e:
            logger.error(f"Error al actualizar validación SRI: {e}")
            return False

    def log_audit(self, user_id: int, action: str, details: str = None):
        """Registra una acción en el log de auditoría"""
        try:
            with self.conn:
                self.conn.execute(
                    'INSERT INTO audit_log (user_id, action, details) VALUES (?, ?, ?)',
                    (user_id, action, details)
                )
        except sqlite3.Error as e:
            logger.error(f"Error al registrar auditoría: {e}")

    # Nuevos métodos para edición de facturas y documentos adicionales

    def update_invoice(self, invoice_id: int, invoice_number: str = None, date: str = None, 
                      document_type: str = None, reference_invoice_id: int = None) -> bool:
        """Actualiza una factura existente"""
        try:
            updates = []
            params = []
            if invoice_number:
                updates.append("invoice_number = ?")
                params.append(invoice_number)
            if date:
                updates.append("date = ?")
                params.append(date)
            if document_type:
                updates.append("document_type = ?")
                params.append(document_type)
            if reference_invoice_id is not None:
                updates.append("reference_invoice_id = ?")
                params.append(reference_invoice_id)
            
            if not updates:
                return True  # No hay cambios
            
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(invoice_id)
            
            query = f"UPDATE invoices SET {', '.join(updates)} WHERE id = ?"
            
            with self.conn:
                self.conn.execute(query, params)
            return True
        except sqlite3.Error as e:
            logger.error(f"Error al actualizar factura: {e}")
            return False

    def create_retention(self, user_id: int, retention_number: str, retention_type: str, 
                        provider_ruc: str, provider_name: str, date: str, invoice_id: int = None) -> Optional[int]:
        """Crea una nueva retención"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(
                    '''INSERT INTO retentions 
                       (user_id, retention_number, retention_type, invoice_id, provider_ruc, provider_name, date)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (user_id, retention_number, retention_type, invoice_id, provider_ruc, provider_name, date)
                )
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error al crear retención: {e}")
            return None

    def add_retention_item(self, retention_id: int, tax_type: str, tax_rate: float, 
                          base_amount: float, retained_amount: float) -> bool:
        """Añade un item a una retención"""
        try:
            with self.conn:
                self.conn.execute(
                    '''INSERT INTO retention_items 
                       (retention_id, tax_type, tax_rate, base_amount, retained_amount)
                       VALUES (?, ?, ?, ?, ?)''',
                    (retention_id, tax_type, tax_rate, base_amount, retained_amount)
                )
                
                # Actualizar total retenido
                self._update_retention_totals(retention_id)
            return True
        except sqlite3.Error as e:
            logger.error(f"Error al añadir item de retención: {e}")
            return False

    def _update_retention_totals(self, retention_id: int):
        """Actualiza los totales de una retención"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT COALESCE(SUM(retained_amount), 0) FROM retention_items WHERE retention_id = ?',
            (retention_id,)
        )
        total_retained = cursor.fetchone()[0]
        
        self.conn.execute(
            'UPDATE retentions SET total_retained = ? WHERE id = ?',
            (total_retained, retention_id)
        )

    def get_retentions(self, user_id: int) -> List[dict]:
        """Obtiene todas las retenciones de un usuario"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM retentions WHERE user_id = ? ORDER BY date DESC', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error al obtener retenciones: {e}")
            return []

    def get_retention_items(self, retention_id: int) -> List[dict]:
        """Obtiene los items de una retención"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM retention_items WHERE retention_id = ?', (retention_id,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error al obtener items de retención: {e}")
            return []

    def create_emission_sheet(self, user_id: int, establishment_code: str, emission_point: str,
                            document_type: str, start_number: int, end_number: int,
                            sri_authorization_code: str, valid_from: str, valid_until: str) -> Optional[int]:
        """Crea una hoja de emisión"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(
                    '''INSERT INTO emission_sheets 
                       (user_id, establishment_code, emission_point, document_type, 
                        start_number, end_number, current_number, sri_authorization_code, 
                        valid_from, valid_until)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (user_id, establishment_code, emission_point, document_type,
                     start_number, end_number, start_number - 1, sri_authorization_code,
                     valid_from, valid_until)
                )
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error al crear hoja de emisión: {e}")
            return None

    def get_emission_sheets(self, user_id: int, document_type: str = None) -> List[dict]:
        """Obtiene hojas de emisión"""
        try:
            cursor = self.conn.cursor()
            if document_type:
                cursor.execute(
                    'SELECT * FROM emission_sheets WHERE user_id = ? AND document_type = ? AND is_active = 1',
                    (user_id, document_type)
                )
            else:
                cursor.execute('SELECT * FROM emission_sheets WHERE user_id = ? AND is_active = 1', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error al obtener hojas de emisión: {e}")
            return []

    def get_next_document_number(self, user_id: int, document_type: str) -> Optional[str]:
        """Obtiene el siguiente número de documento disponible"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                '''SELECT id, establishment_code, emission_point, current_number, end_number
                   FROM emission_sheets 
                   WHERE user_id = ? AND document_type = ? AND is_active = 1
                   ORDER BY created_at DESC LIMIT 1''',
                (user_id, document_type)
            )
            sheet = cursor.fetchone()
            if not sheet:
                return None
            
            next_num = sheet['current_number'] + 1
            if next_num > sheet['end_number']:
                return None  # No hay números disponibles
            
            # Actualizar el número actual
            self.conn.execute(
                'UPDATE emission_sheets SET current_number = ? WHERE id = ?',
                (next_num, sheet['id'])
            )
            
            # Formatear número: establishment-emission-next_num (padded to 9 digits)
            return f"{sheet['establishment_code']}-{sheet['emission_point']}-{next_num:09d}"
            
        except sqlite3.Error as e:
            logger.error(f"Error al obtener siguiente número: {e}")
            return None

    def aggregate_inventory(self, user_id: int) -> List[dict]:
        """Devuelve stock agregado por producto"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT p.id as product_id, p.name as product_name,
                       SUM(i.quantity) as total_quantity,
                       AVG(COALESCE(i.cost_price, p.price)) as avg_cost,
                       p.price as sale_price,
                       p.tax_rate
                FROM inventory i
                JOIN products p ON p.id = i.product_id
                WHERE i.user_id = ?
                GROUP BY p.id, p.name, p.price, p.tax_rate
            ''', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error agregando inventario: {e}")
            return []

    def get_purchase_sales_report(self, user_id: int, start_date: str, end_date: str) -> dict:
        """Reporte de compras y ventas"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT invoice_number, date, subtotal, tax, total, status
                FROM invoices
                WHERE user_id = ? AND document_type = 'invoice' AND date BETWEEN ? AND ?
                ORDER BY date DESC
            ''', (user_id, start_date, end_date))
            sales = [dict(row) for row in cursor.fetchall()]

            cursor.execute('''
                SELECT date, amount, details
                FROM transactions
                WHERE user_id = ? AND type = 'purchase' AND date BETWEEN ? AND ?
                ORDER BY date DESC
            ''', (user_id, start_date, end_date))
            purchases = [dict(row) for row in cursor.fetchall()]

            return {
                'sales': sales,
                'purchases': purchases,
                'totals': {
                    'total_sales': sum(item['total'] for item in sales),
                    'total_purchases': sum(item['amount'] for item in purchases),
                    'balance': sum(item['total'] for item in sales) - sum(item['amount'] for item in purchases)
                }
            }
        except sqlite3.Error as e:
            logger.error(f"Error generando reporte compras/ventas: {e}")
            return {'sales': [], 'purchases': [], 'totals': {'total_sales': 0, 'total_purchases': 0, 'balance': 0}}

    def get_retention_report(self, user_id: int, start_date: str, end_date: str, retention_type: str = None, provider_ruc: str = None) -> dict:
        """Reporte de retenciones 103 y 104"""
        try:
            cursor = self.conn.cursor()
            query = '''
                SELECT id, retention_number, retention_type, provider_ruc, provider_name, date
                FROM retentions
                WHERE user_id = ? AND date BETWEEN ? AND ?
            '''
            params = [user_id, start_date, end_date]

            if retention_type in ['income', 'purchase']:
                query += ' AND retention_type = ?'
                params.append(retention_type)

            if provider_ruc:
                query += ' AND provider_ruc = ?'
                params.append(provider_ruc)

            query += ' ORDER BY date DESC'
            cursor.execute(query, tuple(params))
            retentions = [dict(row) for row in cursor.fetchall()]

            for retention in retentions:
                cursor.execute('''
                    SELECT tax_type, tax_rate, base_amount, retained_amount
                    FROM retention_items
                    WHERE retention_id = ?
                ''', (retention['id'],))
                items = [dict(r) for r in cursor.fetchall()]
                retention['items'] = items
                retention['total_base'] = sum(item['base_amount'] for item in items)
                retention['total_retained'] = sum(item['retained_amount'] for item in items)

            total_base = sum(r['total_base'] for r in retentions)
            total_retained = sum(r['total_retained'] for r in retentions)

            return {
                'retentions': retentions,
                'totals': {
                    'total_base': total_base,
                    'total_retained': total_retained,
                    'count': len(retentions)
                }
            }
        except sqlite3.Error as e:
            logger.error(f"Error generando reporte de retenciones: {e}")
            return {'retentions': [], 'totals': {'total_base': 0, 'total_retained': 0, 'count': 0}}

    def get_invoice_by_number(self, invoice_number: str) -> Optional[dict]:
        """Obtiene factura por número"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM invoices WHERE invoice_number = ?', (invoice_number,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error buscando factura por número: {e}")
            return None

    def bulk_upload_invoices_txt(self, user_id: int, content: str) -> List[dict]:
        """Carga masiva de facturas vía texto."""
        results = []
        lines = [line.strip() for line in content.splitlines() if line.strip()]

        for idx, line in enumerate(lines, 1):
            try:
                fields = line.split('|')
                if len(fields) < 6:
                    raise ValueError('Formato de línea incorrecto, se requiere invoice_number|date|item_desc|qty|unit_price|tax_rate')

                invoice_num, date_val, item_desc, qty, unit_price, tax_rate = fields[:6]
                qty = int(qty)
                unit_price = float(unit_price)
                tax_rate = float(tax_rate)

                invoice = self.get_invoice_by_number(invoice_num)
                if not invoice:
                    invoice_id = self.create_invoice(user_id, invoice_num)
                    if not invoice_id:
                        raise ValueError('No se pudo crear factura')
                else:
                    invoice_id = invoice['id']

                self.add_invoice_item(invoice_id, None, item_desc, qty, unit_price, tax_rate)
                results.append({'line': idx, 'invoice_number': invoice_num, 'status': 'ok'})
            except Exception as ex:
                logger.error(f"Error línea {idx} en carga masiva de facturas: {ex}")
                results.append({'line': idx, 'line_text': line, 'status': 'error', 'message': str(ex)})

        return results

    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()
            logger.info("Conexión cerrada")
