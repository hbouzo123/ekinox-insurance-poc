@echo off
title Ekinox Insurance Platform POC
echo ========================================================
echo   LANCEMENT DE LA PLATEFORME EKINOX INSURANCE (PORT 8000)
echo   SanlamAllianz Multi-Country Accelerator (CI, MA, SN)
echo ========================================================
cd /d "%~dp0poc"
python main.py
pause
