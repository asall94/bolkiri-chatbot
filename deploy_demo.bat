@echo off
echo Deploiement de la demo sur GitHub Pages...
echo.

REM Copier index.html vers le repo demo
copy "docs\index.html" "..\bolkiri-demo\index.html" /Y

REM Aller dans le repo demo
cd "..\bolkiri-demo"

REM Git add, commit et push
git add index.html
git commit -m "Mise a jour demo"
git push origin main

echo.
echo Demo deployee avec succes !
echo URL: https://asall94.github.io/bolkiri-demo/
echo.
pause
