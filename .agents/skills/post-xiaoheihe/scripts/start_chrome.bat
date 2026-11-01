@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0\.."

if not exist ".venv\Scripts\python.exe" (
    echo [错误] 没装依赖，先双击根目录的 install.bat
    pause
    exit /b 1
)

".venv\Scripts\python.exe" "scripts\start_chrome.py" %*
pause
