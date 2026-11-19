@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 servidor_tutor_ia.py
) else (
  python servidor_tutor_ia.py
)
pause
