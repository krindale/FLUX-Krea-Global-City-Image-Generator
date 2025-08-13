@echo off
chcp 65001 >nul
echo ========================================
echo   Image Optimization Tool
echo ========================================
echo.

cd /d "%~dp0"

echo Optimizing images in Sample folder...
echo Original files will be backed up to backup folder.
echo.

python optimize_images.py "Sample" --quality 85

echo.
echo Optimization completed!
echo Original files can be found in the backup folder.
echo.
pause