#!/bin/bash
# Script de inicio para el Sistema de Facturación con IA
# Este script inicia el servidor FastAPI

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  SISTEMA DE FACTURACIÓN CON INTELIGENCIA ARTIFICIAL        ║"
echo "║  Iniciando servidor...                                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python no está instalado"
    exit 1
fi

# Instalar dependencias
echo "⏳ Verificando dependencias..."
pip install -r requirements.txt -q

# Iniciar el servidor
echo ""
echo "✓ Iniciando API en http://localhost:8000"
echo ""
echo "📚 Documentación: http://localhost:8000/docs"
echo "🌐 Interfaz Web: http://localhost:8000 (abre index.html)"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

python3 -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
