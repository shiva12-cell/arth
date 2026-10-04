@echo off
title Arth - Personal Finance Platform
cd /d "c:\Users\abcom\Desktop\Arth"
echo ===================================================
echo Starting Arth Personal Finance Platform...
echo Freeing port 8501 if previously occupied...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8501 ^| findstr LISTENING') do taskkill /f /pid %%a >nul 2>&1
echo The browser will open automatically once ready.
echo Close this window when you want to stop the app.
echo ===================================================
echo.
"C:\Users\abcom\AppData\Local\Programs\Python\Python312\python.exe" -m streamlit run app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred while starting Streamlit.
    pause
)
