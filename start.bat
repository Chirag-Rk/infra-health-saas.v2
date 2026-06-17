@echo off
echo Starting Urban Infrastructure Intelligence Portal...

if not exist venv (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b
)

echo Starting FastAPI Backend...
start cmd /k "call venv\Scripts\activate && uvicorn app.main:app --reload"

echo Starting Streamlit Frontend...
start cmd /k "call venv\Scripts\activate && streamlit run frontend/streamlit_app.py"

echo Application launched in separate windows!
