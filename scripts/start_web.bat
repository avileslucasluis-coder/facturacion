@echo off
REM Script de inicio para el Sistema de Facturación con IA
REM Este script inicia el servidor FastAPI

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  SISTEMA DE FACTURACIÓN CON INTELIGENCIA ARTIFICIAL        ║
echo ║  Iniciando servidor...                                     ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Verificar si pip está instalado
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python/pip no está instalado
    pause
    exit /b 1
)

REM Instalar dependencias si es necesario
echo ⏳ Verificando dependencias...
pip install -r requirements.txt -q

REM Iniciar el servidor
echo.
echo ✓ Iniciando API en http://localhost:8000
echo.
echo 📚 Documentación: http://localhost:8000/docs
echo 🌐 Interfaz Web: http://localhost:8000 (abre index.html)
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
