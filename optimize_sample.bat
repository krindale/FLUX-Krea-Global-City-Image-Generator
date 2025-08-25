@echo off
chcp 65001 >nul
title Sample PNG to WebP Converter

echo.
echo ========================================
echo Sample PNG to WebP Converter
echo ========================================
echo.
echo This script will:
echo 1. Optimize all PNG files in Sample folder
echo 2. Convert PNG files to WebP format
echo 3. Move original PNG files to backup folder
echo.

cd /d "%~dp0"

REM Check Sample folder exists
if not exist "Sample" (
    echo [ERROR] Sample folder does not exist.
    echo.
    pause
    exit /b 1
)

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo.
    pause
    exit /b 1
)

REM Check PIL/Pillow installation
python -c "from PIL import Image" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PIL Pillow library is not installed.
    echo Please install with: pip install Pillow
    echo.
    pause
    exit /b 1
)

echo Checking PNG files in Sample folder...
echo.

REM Run optimization and WebP conversion
python optimize_images.py "Sample" --quality 85

echo.
echo ========================================
echo Complete!
echo ========================================
echo.
echo Results:
echo - WebP files: Sample/timezones/ folder
echo - Original PNG: Sample/backup/ folder
echo.
pause