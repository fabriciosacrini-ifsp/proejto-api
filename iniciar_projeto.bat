@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

title Inicializador do CriptoMonitor (Flask + React)
cd /d "%~dp0"

echo ============================================================
echo          CRIPTOMONITOR - INICIALIZADOR AUTOMATICO
echo ============================================================
echo.

:: ------------------------------------------------------------
:: 1. VERIFICAR E PREPARAR O BACKEND (PYTHON + VENV + PIP)
:: ------------------------------------------------------------
echo [1/3] Verificando ambiente do Backend (Python / Flask)...
cd /d "%~dp0backend"

:: Testa se a venv existe E se funciona neste computador
:: (Se a pasta venv veio de outro PC, o caminho do Python muda e recriamos automaticamente)
set "VENV_VALIDA=0"
if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" -c "import sys" >nul 2>&1
    if !errorlevel! equ 0 set "VENV_VALIDA=1"
)

if "!VENV_VALIDA!"=="0" (
    echo       - Criando ambiente virtual Python ^(venv^) para este computador...
    if exist "venv" rmdir /s /q "venv"
    python -m venv venv
    if !errorlevel! neq 0 (
        echo.
        echo [ERRO] Nao foi possivel encontrar o Python instalado neste computador.
        echo Certifique-se de que o Python esta instalado e marcado no PATH.
        pause
        exit /b 1
    )
)

:: Testa se as bibliotecas do requirements.txt ja estao instaladas
"venv\Scripts\python.exe" -c "import flask, flask_sqlalchemy, requests" >nul 2>&1
if !errorlevel! neq 0 (
    echo       - Baixando dependencias do Python ^(requirements.txt^)...
    "venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>&1
    "venv\Scripts\python.exe" -m pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo.
        echo [ERRO] Falha ao instalar as dependencias do Backend ^(requirements.txt^).
        pause
        exit /b 1
    )
)
echo       [OK] Backend pronto!
echo.

:: ------------------------------------------------------------
:: 2. VERIFICAR E PREPARAR O FRONTEND (NODE + NODE_MODULES)
:: ------------------------------------------------------------
echo [2/3] Verificando ambiente do Frontend (Node.js / React)...
cd /d "%~dp0frontend"

if not exist "node_modules\vite" (
    echo       - Pasta node_modules nao encontrada.
    echo       - Baixando dependencias do Frontend ^(package.json^)... Aguarde...
    call npm install
    if !errorlevel! neq 0 (
        echo.
        echo [ERRO] Falha ao instalar as dependencias do Frontend.
        echo Verifique se o Node.js esta instalado neste computador.
        pause
        exit /b 1
    )
)
echo       [OK] Frontend pronto!
echo.

:: ------------------------------------------------------------
:: 3. INICIAR OS DOIS SERVIDORES E ABRIR O NAVEGADOR
:: ------------------------------------------------------------
echo [3/3] Iniciando servidores...

:: Verifica se a porta 5000 (Flask) ja esta em uso
netstat -ano | findstr ":5000 " | findstr "LISTENING" >nul 2>&1
if !errorlevel! equ 0 (
    echo       - Servidor Backend ^(porta 5000^) ja esta em execucao.
) else (
    echo       - Iniciando Backend Flask em http://127.0.0.1:5000 ...
    start "Backend - API Flask (Porta 5000)" cmd /k "cd /d "%~dp0backend" && venv\Scripts\python.exe run.py"
)

:: Verifica se a porta 5173 (Vite/React) ja esta em uso
netstat -ano | findstr ":5173 " | findstr "LISTENING" >nul 2>&1
if !errorlevel! equ 0 (
    echo       - Servidor Frontend ^(porta 5173^) ja esta em execucao.
) else (
    echo       - Iniciando Frontend React em http://localhost:5173 ...
    start "Frontend - React Vite (Porta 5173)" cmd /k "cd /d "%~dp0frontend" && npm run dev -- --port 5173 --strictPort"
)

:: Aguarda 2 segundos e abre o navegador no site
timeout /t 2 /nobreak >nul
start "" "http://localhost:5173"

echo.
echo ============================================================
echo   Tudo pronto! O CriptoMonitor foi aberto no navegador:
echo   - Frontend (Site): http://localhost:5173
echo   - Backend  (API) : http://127.0.0.1:5000
echo ============================================================
echo.
pause
