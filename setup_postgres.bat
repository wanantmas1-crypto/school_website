@echo off
REM PostgreSQL Setup Script for Windows
REM Run this BEFORE running migrate_to_postgres.py

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     PostgreSQL Setup for Busiada Boarding                  ║
echo ║     Windows Edition                                        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if PostgreSQL is installed
echo Checking for PostgreSQL...
psql --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ PostgreSQL not found. Please install PostgreSQL first:
    echo    https://www.postgresql.org/download/windows/
    echo.
    echo After installation, add PostgreSQL bin folder to PATH
    pause
    exit /b 1
)

echo ✅ PostgreSQL found

REM Check if database exists
echo.
echo Creating PostgreSQL database...
psql -U postgres -c "CREATE DATABASE busiada_boarding;" 2>nul

if errorlevel 1 (
    echo ⚠️  Database may already exist (this is OK)
) else (
    echo ✅ Database created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install psycopg2
echo.
echo Installing PostgreSQL driver for Python...
pip install psycopg2-binary

echo.
echo ✅ PostgreSQL setup complete!
echo.
echo NEXT STEPS:
echo   1. Edit config/settings.py - update DATABASES with your PostgreSQL password
echo   2. Run: python migrate_to_postgres.py
echo.
pause
