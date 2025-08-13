@echo off
chcp 65001 >nul
cd /d "C:\Users\wow32\ComfyUI_Batch\cloud_generator"

echo Cloud Generator - CFG 3.5 (TRANSPARENT BACKGROUND)
echo.
echo All clouds will have TRANSPARENT background for easy compositing!
echo.
echo 1. Generate all 5 cloud types (ALL TRANSPARENT)
echo 2. Blue sky cloud (white cloud + transparent)
echo 3. Sunset cloud (orange/pink cloud + transparent)
echo 4. Gray cloud (gray cloud + transparent)
echo 5. Fantasy castle cloud (blue/gray/white + transparent)
echo 6. Mystical blue cloud (blue/silver/white + transparent)
echo.

set /p choice="Choice (1-6): "

if "%choice%"=="1" python single_cloud_generator.py --style all
if "%choice%"=="2" python single_cloud_generator.py --style blue_sky_mountain
if "%choice%"=="3" python single_cloud_generator.py --style sunset_cityscape
if "%choice%"=="4" python single_cloud_generator.py --style overcast_gray
if "%choice%"=="5" python single_cloud_generator.py --style fantasy_castle
if "%choice%"=="6" python single_cloud_generator.py --style mystical_blue

echo.
echo Done! All clouds have TRANSPARENT background.
echo Check single_clouds folder for compositing ready images!
pause
