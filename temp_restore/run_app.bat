@echo off
echo === Starting Stock Monitoring App ===
echo.

:: Try python command
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Found 'python' command. Starting app...
    python app.py
    goto :end
)

:: Try py command
py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Found 'py' launcher. Starting app...
    py app.py
    goto :end
)

echo.
echo [ERROR] Python not found!
echo Please install Python or add it to your PATH.
echo.

:end
pause
