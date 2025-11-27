@echo off
chcp 65001 >nul
echo ==========================================
echo 주식 모니터링 시스템 설치 및 실행 도우미
echo ==========================================

set PYTHON_CMD=

:: 1. python 명령어 확인
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :found
)

:: 2. py 명령어 확인
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    goto :found
)

echo [오류] 파이썬을 찾을 수 없습니다.
pause
exit /b

:found
echo.
echo [확인] '%PYTHON_CMD%' 명령어로 파이썬을 실행합니다.
echo.

echo [1/2] 필수 패키지 확인 중...
echo ------------------------------------------
:: Google Generative AI SDK 설치 (Python 3.10 이상 필요)
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install flask flask-cors requests pandas google-generativeai

if %errorlevel% neq 0 (
    echo.
    echo [오류] 패키지 설치 중 문제가 발생했습니다.
    echo 관리자 권한으로 실행하거나 인터넷 연결을 확인해주세요.
    pause
    exit /b
)

echo.
echo [2/2] 서버를 시작합니다...
echo ------------------------------------------
echo 브라우저에서 http://localhost:5000 으로 접속하세요.
echo (서버를 종료하려면 창을 닫거나 Ctrl+C를 누르세요)
echo.

%PYTHON_CMD% app.py

pause
