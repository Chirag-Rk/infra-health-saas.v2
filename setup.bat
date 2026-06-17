@echo off
echo Setting up Urban Infrastructure Intelligence Portal...

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo Seeding database...
set PYTHONIOENCODING=utf-8
python scripts\seed_database.py

echo Setup complete! You can now run start.bat to launch the application.
