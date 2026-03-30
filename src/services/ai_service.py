"""
Servicio de Inteligencia Artificial para el Sistema de Facturación
Integración con OpenAI y funciones de IA
"""

import logging
import os
from typing import Dict, List, Optional
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    """Servicio de IA integrado con OpenAI"""
    
    def __init__(self):
        """Inicializa el servicio de IA"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = "gpt-3.5-turbo"
        self.available = False
        self.system_prompt = (
            "Eres un asistente experto en facturación y análisis financiero para empresas ecuatorianas. "
            "Responde con información auténtica y veraz; si no tuvieras datos para afirmar algo, dilo claramente."
        )

        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                self.available = True
                logger.info("Servicio de IA OpenAI inicializado correctamente")
            except ImportError:
                logger.warning("Librería OpenAI no instalada")
                self.available = False
        else:
            logger.warning("OPENAI_API_KEY no configurada en variables de entorno")
            self.available = False

    def is_available(self) -> bool:
        """Verifica si el servicio de IA está disponible"""
        return self.available

    def _call_openai(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        """Llama a OpenAI API con fallback"""
        if not self.available:
            return None
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.3,
                n=1
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error llamando a OpenAI: {e}")
            return None

    def analyze_invoice(self, invoice_data: Dict) -> Dict:
        """
        Analiza una factura usando IA
        
        Args:
            invoice_data: Datos de la factura (invoice + items)
            
        Returns:
            Dict con análisis, sugerencias y nivel de riesgo
        """
        try:
            invoice = invoice_data.get('invoice', {})
            items = invoice_data.get('items', [])
            
            # Preparar resumen para IA
            summary_text = f"""
            Factura: {invoice.get('invoice_number', 'N/A')}
            Fecha: {invoice.get('date', 'N/A')}
            Subtotal: ${invoice.get('subtotal', 0):.2f}
            IVA: ${invoice.get('tax', 0):.2f}
            Total: ${invoice.get('total', 0):.2f}
            Items: {len(items)}
            """
            
            # Llamar a IA si está disponible
            if self.available:
                prompt = f"""
                Analiza la siguiente factura y proporciona:
                1. Un análisis breve (2-3 líneas)
                2. 3 sugerencias de mejora
                3. Nivel de riesgo (bajo, medio, alto)
                
                Datos de la factura:
                {summary_text}
                
                Items:
                {json.dumps([{'description': item.get('description'), 'qty': item.get('quantity'), 'price': item.get('unit_price')} for item in items[:5]], ensure_ascii=False)}
                
                Responde en formato JSON: {{"analysis": "...", "suggestions": ["...", "...", "..."], "risk_level": "..."}}
                """
                
                response = self._call_openai(prompt)
                if response:
                    # Intentar parsear JSON
                    try:
                        result = json.loads(response)
                        return {
                            'analysis': result.get('analysis', 'Análisis disponible'),
                            'suggestions': result.get('suggestions', []),
                            'risk_level': result.get('risk_level', 'unknown')
                        }
                    except:
                        pass
            
            # Fallback: análisis básico
            return {
                'analysis': f'Factura de ${invoice.get("total", 0):.2f} con {len(items)} items. Está lista para ser validada.',
                'suggestions': [
                    'Verificar que todos los items tengan impuestos correctos',
                    'Validar con SRI para autorización',
                    'Mantener registro de auditoría de cambios'
                ],
                'risk_level': 'low' if invoice.get('total', 0) < 10000 else 'medium'
            }
        
        except Exception as e:
            logger.error(f"Error analizando factura: {e}")
            return {
                'analysis': 'Error al analizar la factura',
                'suggestions': [],
                'risk_level': 'unknown'
            }

    def suggest_product_price(self, product_name: str) -> Dict:
        """
        Sugiere un precio para un producto usando IA
        
        Args:
            product_name: Nombre del producto
            
        Returns:
            Dict con precio sugerido y razonamiento
        """
        try:
            if self.available:
                prompt = f"""
                Eres un asesor de precios para productos en Ecuador.
                
                Para el producto: "{product_name}"
                
                Sugiere un precio competitivo en USD considerando:
                - El mercado ecuatoriano
                - Márgenes de ganancia razonables (30-50%)
                - Tendencias actuales
                
                Responde en JSON: {{"price": número, "reasoning": "explicación breve"}}
                """
                
                response = self._call_openai(prompt, max_tokens=200)
                if response:
                    try:
                        result = json.loads(response)
                        return {
                            'price': float(result.get('price', 100)),
                            'reasoning': result.get('reasoning', 'Precio estimado')
                        }
                    except:
                        pass
            
            # Fallback: precios base por tipo de producto
            price_map = {
                'laptop': 800, 'computadora': 800,
                'mouse': 25, 'ratón': 25,
                'teclado': 120,
                'monitor': 350,
                'pantalla': 350,
                'impresora': 300,
                'cable': 10,
                'adaptador': 15,
                'cargador': 25,
                'funda': 20,
            }
            
            product_lower = product_name.lower()
            base_price = 50
            
            for key, price in price_map.items():
                if key in product_lower:
                    base_price = price
                    break
            
            return {
                'price': base_price,
                'reasoning': f'Precio base estimado para {product_name} en el mercado ecuatoriano'
            }
        
        except Exception as e:
            logger.error(f"Error sugiriendo precio: {e}")
            return {
                'price': 100,
                'reasoning': 'Precio default'
            }

    def analyze_sales(self, sales_report: List[Dict]) -> Dict:
        """
        Analiza tendencias de ventas usando IA
        
        Args:
            sales_report: Lista de facturas/ventas
            
        Returns:
            Dict con insights, tendencias y recomendaciones
        """
        try:
            # Calcular estadísticas básicas
            total_sales = sum(item.get('total', 0) for item in sales_report)
            avg_sale = total_sales / len(sales_report) if sales_report else 0
            num_invoices = len(sales_report)
            authorized = sum(1 for item in sales_report if item.get('status') == 'authorized')
            
            stats_text = f"""
            Período de análisis: {len(sales_report)} facturas
            Total de ventas: ${total_sales:.2f}
            Venta promedio: ${avg_sale:.2f}
            Facturas autorizadas: {authorized}/{num_invoices}
            """
            
            if self.available:
                prompt = f"""
                Eres un analista financiero especializado en pequeñas empresas en Ecuador.
                
                Analiza estos datos de ventas:
                {stats_text}
                
                Proporciona:
                1. Insights principales (2-3 puntos clave)
                2. Tendencias observadas
                3. 3 recomendaciones de acción
                
                Responde en JSON: {{"insights": "...", "trends": ["...", "..."], "recommendations": ["...", "...", "..."]}}
                """
                
                response = self._call_openai(prompt)
                if response:
                    try:
                        result = json.loads(response)
                        return {
                            'insights': result.get('insights', 'Datos analizados'),
                            'trends': result.get('trends', []),
                            'recommendations': result.get('recommendations', [])
                        }
                    except:
                        pass
            
            # Fallback: análisis básico
            insights = f'Se generaron {num_invoices} facturas por ${total_sales:.2f}. Venta promedio: ${avg_sale:.2f}'
            
            return {
                'insights': insights,
                'trends': [
                    f'Volumen de ventas: {num_invoices} transacciones',
                    f'Autorización SRI: {authorized}/{num_invoices} facturas',
                    f'Monto promedio por factura: ${avg_sale:.2f}'
                ],
                'recommendations': [
                    'Continuar validación de facturas con SRI',
                    'Monitorear patrones de ventas regularmente',
                    'Optimizar products con mayor rotación'
                ]
            }
        
        except Exception as e:
            logger.error(f"Error analizando ventas: {e}")
            return {
                'insights': 'Error al analizar ventas',
                'trends': [],
                'recommendations': []
            }

    def realtime_assistant(self, prompt: str) -> str:
        """Provee respuesta en tiempo real para el asistente IA"""
        try:
            if self.available:
                # Pedir confirmación de veracidad y claridad
                response = self._call_openai(
                    f"{prompt}\n\nResponde con datos verificados y cita cuando sean hechos; si no se conoce, indica que no hay información suficiente.",
                    max_tokens=280
                )
                if response:
                    return response.strip()

            # Fallback local (offline)
            return (
                "[Modo offline] No disponible OpenAI. "
                "Proporciona información básica y verifica siempre con registros reales de su compañía."
            )
        except Exception as e:
            logger.error(f"Error en realtime_assistant: {e}")
            return "Error interno en el asistente. Intente más tarde."

    def extract_invoice_data(self, document_text: str) -> Dict:
        """
        Extrae datos de un documento usando IA (OCR simulado)
        
        Args:
            document_text: Texto del documento o descripción
            
        Returns:
            Dict con datos extraídos
        """
        try:
            if self.available:
                prompt = f"""
                Extrae información de factura del siguiente texto y devolverla en JSON.
                
                Texto:
                {document_text}
                
                Extrae: cliente, items (descripción, cantidad, precio), total
                
                Responde en JSON: {{"client": "...", "items": [{{"description": "...", "quantity": 1, "price": 0}}], "total": 0}}
                """
                
                response = self._call_openai(prompt)
                if response:
                    try:
                        return json.loads(response)
                    except:
                        pass
            
            # Fallback: extracción simple
            return {
                'client': 'Cliente',
                'items': [
                    {'description': 'Item 1', 'quantity': 1, 'price': 100}
                ],
                'total': 100,
                'note': 'Datos extraídos de forma básica'
            }
        
        except Exception as e:
            logger.error(f"Error extrayendo datos: {e}")
            return {
                'client': 'Desconocido',
                'items': [],
                'total': 0,
                'error': str(e)
            }

    def generate_invoice_description(self, product_name: str, quantity: int) -> str:
        """
        Genera una descripción detallada de un producto para la factura
        
        Args:
            product_name: Nombre del producto
            quantity: Cantidad
            
        Returns:
            Descripción detallada
        """
        try:
            if self.available:
                prompt = f"""
                Genera una descripción profesional y breve para factura de:
                Producto: {product_name}
                Cantidad: {quantity}
                
                La descripción debe ser clara, concisa y profesional.
                """
                
                response = self._call_openai(prompt, max_tokens=100)
                if response:
                    return response.strip()
            
            # Fallback
            return f"{quantity}x {product_name} (suministro/equipo)"
        
        except Exception as e:
            logger.error(f"Error generando descripción: {e}")
            return f"{quantity}x {product_name}"
