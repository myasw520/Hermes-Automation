@echo off
REM post-xiaoheihe deps installer (ASCII-only per windows-batch-powershell rule)
REM Original CN version had GBK mojibake; venv can also be built manually:
REM   python -m venv .venv
REM   .venv\Scripts\python -m pip install -r requirements.txt
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] python not found in PATH. Install Python 3.10+ first.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] creating .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] venv creation failed
        pause
        exit /b 1
    )
) else (
    echo [1/3] .venv exists, skip
)

echo [2/3] upgrading pip ...
".venv\Scripts\python.exe" -m pip install --upgrade pip -q --index-url https://pypi.tuna.tsinghua.edu.cn/simple

echo [3/3] installing requirements ...
".venv\Scripts\python.exe" -m pip install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo [ERROR] install failed. Try official index:
    echo   .venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo DONE. Verify: .venv\Scripts\python.exe scripts\xhh_check.py --help
pause
