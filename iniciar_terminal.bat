@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

title CriptoMonitor - Menu de Terminal (SQLite3 + POO)
cd /d "%~dp0backend"

:: Verifica se a venv existe e funciona neste computador
set "VENV_VALIDA=0"
if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" -c "import sys" >nul 2>&1
    if !errorlevel! equ 0 set "VENV_VALIDA=1"
)

if "!VENV_VALIDA!"=="0" (
    echo Preparando ambiente virtual Python ^(venv^)...
    if exist "venv" rmdir /s /q "venv"
    python -m venv venv
)

"venv\Scripts\python.exe" -c "import flask, flask_sqlalchemy, requests" >nul 2>&1
if !errorlevel! neq 0 (
    echo Instalando bibliotecas do requirements.txt...
    "venv\Scripts\python.exe" -m pip install -r requirements.txt
)

cls
"venv\Scripts\python.exe" terminal.py
pause
