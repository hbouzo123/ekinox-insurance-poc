@echo off
title Arrêt Ekinox Insurance Platform & Sandbox ORASS
echo =====================================================================
echo   ARRÊT DES SERVEURS SANDBOX ORASS (PORT 8000) & EKINOX IA (PORT 8090)
echo =====================================================================

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8090 ^| findstr LISTENING') do taskkill /f /pid %%a >nul 2>&1

echo [OK] Les serveurs sur les ports 8000 et 8090 ont été arrêtés avec succès.
pause
