@echo off
cd /d "%~dp0"
set LOG=%~dp0update_all_prices_log.txt

:: Overwrite log with header
(
  echo ============================================================
  echo  STOCKS -- Update All Sector Prices
  echo  %DATE% %TIME%
  echo ============================================================
  echo.
) > "%LOG%"

echo ============================================================
echo  STOCKS -- Update All Sector Prices
echo ============================================================
echo.

echo [1/3] AI Infrastructure...
echo [1/3] AI Infrastructure... >> "%LOG%"
cd AI
powershell -Command "python -u AI_update_prices.py 2>&1 | Tee-Object -FilePath '..\update_all_prices_log.txt' -Append"
cd ..
echo. >> "%LOG%"
echo.

echo [2/3] Biotech...
echo [2/3] Biotech... >> "%LOG%"
cd Biotech
powershell -Command "python -u Biotech_update_prices.py 2>&1 | Tee-Object -FilePath '..\update_all_prices_log.txt' -Append"
cd ..
echo. >> "%LOG%"
echo.

echo [3/3] Defence ^& Aerospace...
echo [3/3] Defence ^& Aerospace... >> "%LOG%"
cd Defence
powershell -Command "python -u Defence_update_prices.py 2>&1 | Tee-Object -FilePath '..\update_all_prices_log.txt' -Append"
cd ..
echo. >> "%LOG%"
echo.

echo [4/4] Technology...
echo [4/4] Technology... >> "%LOG%"
cd Tech
powershell -Command "python -u Tech_update_prices.py 2>&1 | Tee-Object -FilePath '..\update_all_prices_log.txt' -Append"
cd ..
echo. >> "%LOG%"

(
  echo ============================================================
  echo  Done. All 4 sectors updated.
  echo  Log: %LOG%
  echo ============================================================
) >> "%LOG%"

echo ============================================================
echo  Done. All 4 sectors updated.
echo  Log saved to: %LOG%
echo ============================================================
pause
