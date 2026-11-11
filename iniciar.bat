@echo off
chcp 65001 >nul
title Centralizador Diario de Relatorios - Vivo
echo ========================================================
echo   Iniciando Centralizador Diario de Relatorios - VIVO
echo ========================================================

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

start "" http://127.0.0.1:8000
python app.py
pause
