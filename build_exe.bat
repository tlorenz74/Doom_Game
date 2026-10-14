@echo off
setlocal
cd /d "%~dp0"

set "PYTHON=py"
set "PYTHON_ARGS=-3.13"
py -3.13 --version >nul 2>&1
if errorlevel 1 (
    set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    set "PYTHON_ARGS="
    if not exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" goto :python_error
)

"%PYTHON%" %PYTHON_ARGS% -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 13) else 1)" >nul 2>&1
if errorlevel 1 goto :python_error

"%PYTHON%" %PYTHON_ARGS% -m venv .venv
if errorlevel 1 goto :error
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto :error
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto :error
python hellbound.py --self-test
if errorlevel 1 goto :error
pyinstaller --noconfirm --clean --onefile --windowed --name Hellbound hellbound.py
if errorlevel 1 goto :error

echo.
echo Done! Your game is at: %~dp0dist\Hellbound.exe
exit /b 0

:python_error
echo Python 3.13 was not found. Install Python 3.13 or update this script with its location.
exit /b 1

:error
echo Build failed. Review the error above.
exit /b 1
