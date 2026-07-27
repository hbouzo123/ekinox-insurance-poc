@echo off
title Arrêt Ekinox Insurance Platform POC
echo ========================================================
echo   ARRÊT DU SERVEUR EKINOX INSURANCE PLATFORM (PORT 8000)
echo ========================================================
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /f /pid %%a >nul 2>&1
echo [OK] Le serveur Ekinox POC sur le port 8000 a été arrêté avec succès.
pause
