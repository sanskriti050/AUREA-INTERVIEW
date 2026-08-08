@echo off
echo Setting up Aurea V2 Backend...

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ✅ Backend setup complete!
echo.
echo Next steps:
echo 1. Open .env file and add your GROQ_API_KEY
echo 2. Make sure PostgreSQL is running
echo 3. Run: venv\Scripts\activate
echo 4. Run: uvicorn app.main:app --reload
echo 5. Open: http://localhost:8000/docs
