@echo off
setlocal

:: CD into pipeline is no longer needed since everything runs from root
:: cd /d "%~dp0\pipeline"

echo =========================================
echo  Starting PaddleOCR Custom Pipeline...
echo =========================================

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python 3.10+ and try again.
    pause
    exit /b 1
)

:: Check if virtual environment exists, create if it doesn't
if exist "venv\Scripts\activate.bat" goto venv_exists
echo [INFO] Creating virtual environment (venv)...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)
echo [INFO] Virtual environment created successfully.
:venv_exists

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Upgrade pip and install dependencies
echo [INFO] Installing/Verifying dependencies from requirements.txt...
"%~dp0venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>&1
"%~dp0venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies. Please check your requirements.txt.
    pause
    exit /b 1
)

:: Run the main application
echo.
echo [INFO] Starting FastAPI backend server...
echo [INFO] Click the link below to open the website:
echo        http://localhost:8081
echo =========================================
"%~dp0venv\Scripts\python.exe" -m uvicorn app:app --host 0.0.0.0 --port 8081 --reload
if errorlevel 1 (
    echo =========================================
    echo [ERROR] The server exited with an error.
    pause
    exit /b 1
)

echo =========================================
echo [SUCCESS] Execution finished.
pause
