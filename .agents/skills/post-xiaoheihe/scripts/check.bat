@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0\.."

if not exist ".venv\Scripts\python.exe" (
    echo [错误] 没装依赖，先双击根目录的 install.bat
    pause
    exit /b 1
)

echo === 登录态 / 编辑器检查 ===
".venv\Scripts\python.exe" "scripts\xhh_check.py" %*
echo.
pause
