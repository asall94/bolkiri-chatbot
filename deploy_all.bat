@echo off
echo Deploiement complet : Backend + Demo
echo.

REM 1. Commit et push du repo principal
echo [1/3] Push du repo principal...
git add -A
git commit -m "%~1"
git push origin main

REM 2. Copier vers bolkiri-demo
echo [2/3] Copie vers bolkiri-demo...
copy "docs\index.html" "..\bolkiri-demo\index.html" /Y

REM 3. Deploy demo
echo [3/3] Deploy demo sur GitHub Pages...
cd "..\bolkiri-demo"
git add index.html
git commit -m "Auto-sync depuis bolkiri-chatbot"
git push origin main

cd "..\Bolkiri"
echo.
echo ========================================
echo Deploiement complet termine !
echo - Backend: https://bolkiri-chatbot.onrender.com/
echo - Demo: https://asall94.github.io/bolkiri-demo/
echo ========================================
echo.
pause
