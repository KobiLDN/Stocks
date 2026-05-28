@echo off
cd /d "%~dp0"
echo Updating Defence ^& Aerospace prices...
echo.
python update_prices.py
echo.
pause
