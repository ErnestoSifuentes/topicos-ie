@echo off
cd /d "%~dp0"
python -m pip install -r requirements.txt
python proyecto1_termostato_tmp36.py
pause
