@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Crie o ambiente virtual e instale requirements.txt conforme o README.
  pause
  exit /b 1
)
echo Clinica Viva: http://127.0.0.1:5000
start "" "http://127.0.0.1:5000"
".venv\Scripts\python.exe" app.py
pause
