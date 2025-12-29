@echo off
REM ============================================================================
REM Jenkins Freestyle Project - API AI Tester Execution Script
REM This script is called by Jenkins Freestyle project with parameters
REM ============================================================================

echo ============================================================================
echo            API AI Tester - Freestyle Project Execution
echo ============================================================================

REM Display parameters
echo.
echo Configuration:
echo   Base URL: %BASE_URL%
echo   Swagger URL: %SWAGGER_URL%
echo   API Key: ***
echo   Use AI: %USE_AI%
echo   LLM Model: %LLM_MODEL%
echo   Reuse Tests: %REUSE_TESTS%
echo   Python Command: %PYTHON_CMD%
echo.
echo ============================================================================

REM Clean Python cache to ensure fresh code execution
echo.
echo [0/5] Cleaning Python cache files...
if exist __pycache__ rmdir /s /q __pycache__
if exist engine\__pycache__ rmdir /s /q engine\__pycache__
echo Python cache cleaned
echo.

REM Step 1: Setup Python Virtual Environment
echo.
echo [1/5] Setting up Python virtual environment...
%PYTHON_CMD% -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create virtual environment
    exit /b 1
)

call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to activate virtual environment
    exit /b 1
)

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)

echo SUCCESS: Virtual environment ready
echo.

REM Step 2: Verify Ollama if AI is enabled
if /I "%USE_AI%"=="true" (
    echo [2/5] Verifying Ollama setup...
    ollama --version
    if %ERRORLEVEL% NEQ 0 (
        echo WARNING: Ollama not found - AI features may not work
    ) else (
        echo Checking for model: %LLM_MODEL%
        ollama list | findstr /I "%LLM_MODEL%"
        if %ERRORLEVEL% NEQ 0 (
            echo WARNING: Model %LLM_MODEL% not found
        ) else (
            echo SUCCESS: Ollama and model verified
        )
    )
    echo.
) else (
    echo [2/5] Skipping Ollama verification (AI not enabled)
    echo.
)

REM Step 3: Build command line arguments
echo [3/5] Preparing test execution...

set RUN_CMD=%PYTHON_CMD% -u run_pipeline.py --base-url "%BASE_URL%" --swagger-url "%SWAGGER_URL%" --api-key "%API_KEY%" --llm-model "%LLM_MODEL%"

if /I "%USE_AI%"=="true" (
    set RUN_CMD=%RUN_CMD% --use-ai
)

if /I "%REUSE_TESTS%"=="true" (
    set RUN_CMD=%RUN_CMD% --reuse-tests
)

echo Command: %RUN_CMD%
echo.

REM Step 4: Execute tests
echo [4/5] Executing API tests...
echo ============================================================================
%RUN_CMD%
set TEST_RESULT=%ERRORLEVEL%
echo ============================================================================
echo.

REM Step 5: Summary
echo [5/5] Execution Summary
if %TEST_RESULT% EQU 0 (
    echo STATUS: SUCCESS - All tests passed
    echo Reports generated in 'reports' folder
    echo Artifacts saved in 'artifacts' folder
) else (
    echo STATUS: FAILED - Some tests failed
    echo Check reports for details
)
echo.
echo ============================================================================

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat 2>nul

REM Exit with test result code
exit /b %TEST_RESULT%
