@echo off
echo Building Distance Checker...

:: Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

:: Install requirements
pip install -r requirements.txt

:: Run PyInstaller
python build_exe.py

:: Create logs directory in dist
mkdir dist\logs 2>nul

:: Create a README for the distribution
echo Distance Checker Installation Instructions > dist\README.txt
echo ================================== >> dist\README.txt
echo. >> dist\README.txt
echo 1. Before first run: >> dist\README.txt
echo    - Rename .env.template to .env >> dist\README.txt
echo    - Edit .env and add your Google Maps API key >> dist\README.txt
echo. >> dist\README.txt
echo 2. Run DistanceChecker.exe >> dist\README.txt
echo. >> dist\README.txt
echo Note: You can get a Google Maps API key from: >> dist\README.txt
echo https://console.cloud.google.com/ >> dist\README.txt

echo Build complete! Check the dist folder for the executable.
pause