@echo off
echo ================================================
echo   Bolkiri AI Agent - GitHub Deployment Script
echo ================================================
echo.

REM Check if git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

echo Step 1: Navigate to backend directory
cd backend

echo.
echo Step 2: Initialize Git repository
git init

echo.
echo Step 3: Add all files
git add .

echo.
echo Step 4: Create initial commit
git commit -m "Initial commit - Bolkiri AI Agent"

echo.
echo ================================================
echo   IMPORTANT: Create GitHub Repository
echo ================================================
echo.
echo 1. Go to https://github.com/new
echo 2. Repository name: bolkiri-chatbot
echo 3. Choose Public or Private
echo 4. DO NOT initialize with README
echo 5. Click "Create repository"
echo.
echo When ready, you will see a URL like:
echo https://github.com/YOUR_USERNAME/bolkiri-chatbot.git
echo.
pause

echo.
set /p REPO_URL="Enter your GitHub repository URL: "

echo.
echo Step 5: Add remote origin
git remote add origin %REPO_URL%

echo.
echo Step 6: Push to GitHub
git branch -M main
git push -u origin main

echo.
echo ================================================
echo   SUCCESS: Code pushed to GitHub
echo ================================================
echo.
echo Next steps:
echo 1. Go to https://render.com
echo 2. Click "New +" then "Web Service"
echo 3. Connect your GitHub repository
echo 4. Use these settings:
echo    - Name: bolkiri-chatbot
echo    - Region: Frankfurt (EU Central)
echo    - Branch: main
echo    - Root Directory: (leave empty)
echo    - Runtime: Python 3
echo    - Build Command: pip install -r requirements.txt
echo    - Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
echo    - Instance Type: Free
echo.
echo 5. Add Environment Variable:
echo    - OPENAI_API_KEY = (your OpenAI key)
echo.
echo 6. Click "Create Web Service"
echo.
pause
