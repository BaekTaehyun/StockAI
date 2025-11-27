@echo off
echo === Starting Stock Monitoring App (v2) ===
echo.

set PYTHON_PATH="C:\Users\bak12\AppData\Local\Programs\Python\Python38-32\python.exe"

if exist %PYTHON_PATH% (
    echo Found Python at %PYTHON_PATH%
    %PYTHON_PATH% app.py
) else (
    echo [ERROR] Python not found at %PYTHON_PATH%
    echo Please check your installation.
)

pause
