@echo off
echo ====================================
echo Pushing to GitHub
echo ====================================
echo.

cd /d "%~dp0"

echo Adding files...
git add .

echo.
echo Committing...
git commit -m "Initial commit: API AI Tester with Petstore support and multiple LLM models"

echo.
echo Setting branch to main...
git branch -M main

echo.
echo Pushing to GitHub...
git push -u origin main

echo.
echo ====================================
echo Done! Check https://github.com/pranaybhaskar9851/APIAITester
echo ====================================
pause
