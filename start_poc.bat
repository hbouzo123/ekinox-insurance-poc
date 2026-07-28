@echo off
title Ekinox Insurance Platform & ORASS Sandbox Launcher
echo =====================================================================
echo   LANCEMENT CONJOINT : SANDBOX ORASS (PORT 8000) & EKINOX IA (PORT 8090)
echo   SanlamAllianz Multi-Country Digital Sales & Fraud Accelerator
echo =====================================================================
echo.

cd /d "%~dp0poc"

echo [1/2] Démarrage du Serveur Sandbox ORASS (Port 8000)...
start "Sandbox ORASS Core Insurance (Port 8000)" cmd /k "set PORT=8000 && python main.py"

timeout /t 2 /nobreak >nul

echo [2/2] Démarrage de la Plateforme Ekinox IA (Port 8090)...
start "Ekinox IA Platform (Port 8090)" cmd /k "set PORT=8090 && set ORASS_LOCAL_SANDBOX_URL=http://localhost:8000/api/v1/sandbox && python main.py"

timeout /t 2 /nobreak >nul

echo.
echo =====================================================================
echo [OK] Les 2 serveurs sont démarrés avec succès !
echo - Sandbox ORASS Core API : http://localhost:8000/api/v1/sandbox/catalog
echo - Application Ekinox IA  : http://localhost:8090/sales/chat
echo =====================================================================
echo.

start http://localhost:8090/sales/chat

pause
