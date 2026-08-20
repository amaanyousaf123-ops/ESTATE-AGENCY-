@echo off
echo ===================================================
echo Commander City Estate Management System (Zero-Install)
echo ===================================================
echo.
echo Starting Server and Opening Browser...
echo The app will open in your default browser. Keep this window open while using the app!
echo.

:: Wait for a second to allow the server to start before opening the browser
start "" http://localhost:8080

:: Start the Python standard library HTTP server
py backend/server.py

pause
