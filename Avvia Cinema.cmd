@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 cinema.py
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Installa Python 3.10 o successivo da python.org per avviare Cinema.
    pause
    exit /b 1
  )
  python cinema.py
)
if errorlevel 1 pause
