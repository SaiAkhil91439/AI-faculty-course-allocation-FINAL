@echo off
title AI Faculty Course Allocation Agent
echo =====================================================================
echo  Starting AI Faculty Course Allocation Optimization Engine...
echo  URL: http://127.0.0.1:8000
echo  Username: admin  ^|  Password: admin123
echo =====================================================================
cd /d "%~dp0"
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    python run.py
) else (
    python run.py
)
pause
