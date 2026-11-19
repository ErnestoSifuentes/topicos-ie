@echo off
cd /d "%~dp0"
python -m pip install -r requirements.txt
python monitor_adxl335_python.py
pause
