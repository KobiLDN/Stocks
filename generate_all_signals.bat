@echo off
cd /d "%~dp0"
set LOG=%~dp0generate_all_signals_log.txt

:: Overwrite log with header
(
  echo ============================================================
  echo  STOCKS -- Generate All Sector Signals
  echo  %DATE% %TIME%
  echo ============================================================
  echo.
) > "%LOG%"

echo ============================================================
echo  STOCKS -- Generate All Sector Signals
echo ============================================================
echo.

echo [1/3] AI Infrastructure...
echo [1/3] AI Infrastructure... >> "%LOG%"
cd AI
powershell -Command "python -u generate_signals_local.py 2>&1 | Tee-Object -FilePath '..\generate_all_signals_log.txt' -Append"
cd ..
echo. >> "%LOG%"
echo.

echo [2/3] Biotech...
echo [2/3] Biotech... >> "%LOG%"
cd Biotech
powershell -Command "python -u generate_signals_local.py 2>&1 | Tee-Object -FilePath '..\generate_all_signals_log.txt' -Append"
cd ..
echo. >> "%LOG%"
echo.

echo [3/3] Defence ^& Aerospace...
echo [3/3] Defence ^& Aerospace... >> "%LOG%"
cd Defence
powershell -Command "python -u generate_signals_local.py 2>&1 | Tee-Object -FilePath '..\generate_all_signals_log.txt' -Append"
cd ..
echo. >> "%LOG%"

(
  echo ============================================================
  echo  Done. All 3 sector signals generated.
  echo  Log: %LOG%
  echo ============================================================
) >> "%LOG%"

echo ============================================================
echo  Done. All 3 sector signals generated.
echo  Log saved to: %LOG%
echo ============================================================
pause
