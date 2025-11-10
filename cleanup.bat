@echo off
echo Nettoyage des fichiers non necessaires...

echo Suppression integration...
rmdir /s /q integration 2>nul

echo Suppression docs...
rmdir /s /q docs 2>nul

echo Suppression start_frontend.bat...
del /q start_frontend.bat 2>nul

echo Suppression backend\data...
rmdir /s /q backend\data 2>nul

echo Suppression backend\knowledge_base.py (ancien)...
del /q backend\knowledge_base.py 2>nul

echo Suppression backend\scraper.py (ancien)...
del /q backend\scraper.py 2>nul

echo Suppression backend\scraped_data.json...
del /q backend\scraped_data.json 2>nul

echo Suppression backend\test_agent.py...
del /q backend\test_agent.py 2>nul

echo Suppression backend\test_openai.py...
del /q backend\test_openai.py 2>nul

echo Suppression backend\test_enriched_kb.py...
del /q backend\test_enriched_kb.py 2>nul

echo.
echo Nettoyage termine!
echo.
echo NOTE: Le dossier frontend/ contient node_modules (lourd).
echo Si tu veux le supprimer, ferme VS Code et supprime-le manuellement.
pause
