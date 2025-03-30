@echo off
echo Setting up AI Travel Planner...

REM Check if Python is installed
python --version > NUL 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists, create if it doesn't
if not exist ".env" (
    echo Creating .env file with API keys...
    echo GEMINI_API_KEY=AIzaSyD4x3ofUx_LnHbuPfiZ-2GN2v0Dy_UGiIM> .env
    echo OPENWEATHER_API_KEY=d092975910383ea8a4ab10da6aebf6be>> .env
)

REM Run the application
echo Starting the application...
streamlit run app/main.py

REM If there's an error, keep the window open
if errorlevel 1 (
    echo An error occurred while running the application.
    pause
)