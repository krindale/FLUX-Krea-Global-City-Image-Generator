@echo off
chcp 65001 >nul
echo Simple Background Remover
echo.

cd /d "C:\Users\wow32\ComfyUI_Batch\cloud_generator"

echo Choose action:
echo 1. Remove background from clouds folder
echo 2. Remove background from custom folder  
echo 3. Remove background from single image
echo 4. Install libraries (run install.bat)
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo Processing clouds folder...
    python simple_background_remover.py --input clouds --output simple_transparent --method auto
) else if "%choice%"=="2" (
    echo.
    set /p inputdir="Enter input folder path: "
    set /p outputdir="Enter output folder name: "
    if "%outputdir%"=="" set outputdir=simple_transparent
    echo Processing folder...
    python simple_background_remover.py --input "%inputdir%" --output "%outputdir%" --method auto
) else if "%choice%"=="3" (
    echo.
    set /p filepath="Enter image file path: "
    echo Processing single image...
    python simple_background_remover.py --single "%filepath%" --method auto
) else if "%choice%"=="4" (
    echo Running installation...
    call install.bat
    echo Installation completed!
) else (
    echo Invalid choice
)

echo.
echo Processing completed!
pause
