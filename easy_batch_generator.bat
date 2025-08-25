@echo off
chcp 65001 > nul 2>&1
setlocal enabledelayedexpansion
title Global City Image Generator

echo.
echo ===============================================================
echo  FLUX Krea + Low Poly Joy LoRA Global City Image Generator
echo ===============================================================
echo.
echo  Timezone-based folder management
echo  51 major cities landmark image generation  
echo  6 weather conditions
echo  VRAM 12GB+ recommended
echo.

:MAIN_MENU
cls
echo.
echo ===============================================================
echo Generation Options
echo ===============================================================
echo.
echo [1] Asia-Pacific (16 cities, 96 images, 3-4 hours)
echo [2] Europe (12 cities, 72 images, 2-3 hours)
echo [3] North America (10 cities, 60 images, 2-3 hours)
echo [4] Middle East and Africa (9 cities, 54 images, 2-3 hours)
echo [5] South America (5 cities, 30 images, 1-2 hours)
echo [6] Resort Destinations (15 cities, 90 images, 3-4 hours)
echo [7] Regional Fallbacks (9 regions, 54 images, 3-4 hours)
echo [8] All Regions (51 cities, 306 images, 9-15 hours)
echo [9] Individual City Selection
echo [10] Test Run (First 2 cities)
echo [11] Weather Selection
echo [12] Show Info
echo [13] Clear Existing Images
echo [0] Exit
echo.
echo ** Existing images will be automatically overwritten **
echo.
set /p "choice=Please select (0-13): "

if "!choice!"=="1" goto :ASIA_PACIFIC
if "!choice!"=="2" goto :EUROPE
if "!choice!"=="3" goto :NORTH_AMERICA
if "!choice!"=="4" goto :MIDDLE_EAST_AFRICA
if "!choice!"=="5" goto :SOUTH_AMERICA
if "!choice!"=="6" goto :RESORT_DESTINATIONS
if "!choice!"=="7" goto :REGIONAL_FALLBACK
if "!choice!"=="8" goto :ALL_REGIONS
if "!choice!"=="9" goto :INDIVIDUAL_MENU
if "!choice!"=="10" goto :TEST_RUN
if "!choice!"=="11" goto :WEATHER_SELECT
if "!choice!"=="12" goto :SHOW_INFO
if "!choice!"=="13" goto :CLEAR_IMAGES
if "!choice!"=="0" goto :EXIT

echo Invalid selection. Please try again.
pause
goto :MAIN_MENU

:CLEAR_IMAGES
echo.
echo ===============================================================
echo Clear Existing Images
echo ===============================================================
echo.
echo This will delete all images in ComfyUI/output/timezones/ folder.
echo.
set /p "confirm=Are you sure you want to delete all existing images? (y/n): "
if /i "!confirm!"=="y" goto :DO_CLEAR
goto :MAIN_MENU

:DO_CLEAR
echo.
echo Deleting existing images...
if exist "..\ComfyUI\output\timezones" (
    rmdir /s /q "..\ComfyUI\output\timezones" > nul 2>&1
    echo Successfully deleted all existing images.
) else (
    echo No images to delete.
)
echo.
pause
goto :MAIN_MENU

:ASIA_PACIFIC
echo.
echo Starting Asia-Pacific region generation...
echo ===============================================================
echo Existing images will be automatically overwritten.
echo.
python regional_batch_generator.py --region asia_pacific --config global_cities_config.json
goto :RESULT_MENU

:EUROPE
echo.
echo Starting Europe region generation...
echo ===============================================================
echo Existing images will be automatically overwritten.
echo.
python regional_batch_generator.py --region europe --config global_cities_config.json
goto :RESULT_MENU

:NORTH_AMERICA
echo.
echo Starting North America region generation...
echo ===============================================================
echo Existing images will be automatically overwritten.
echo.
python regional_batch_generator.py --region north_america --config global_cities_config.json
goto :RESULT_MENU

:MIDDLE_EAST_AFRICA
echo.
echo Starting Middle East and Africa region generation...
echo ===============================================================
echo Existing images will be automatically overwritten.
echo.
python regional_batch_generator.py --region middle_east_africa --config global_cities_config.json
goto :RESULT_MENU

:SOUTH_AMERICA
echo.
echo Starting South America region generation...
echo ===============================================================
echo Existing images will be automatically overwritten.
echo.
python regional_batch_generator.py --region south_america --config global_cities_config.json
goto :RESULT_MENU

:RESORT_DESTINATIONS
echo.
echo Starting Resort Destinations generation...
echo ===============================================================
echo Cities: 15 premium resort and tourist destinations
echo Images: 90 (15 cities x 6 weather conditions)
echo Time: 3-4 hours
echo Existing images will be automatically overwritten.
echo.
python regional_batch_generator.py --resort --config resort_cities_config.json
goto :RESULT_MENU

:REGIONAL_FALLBACK
echo.
echo Starting Regional Fallbacks generation...
echo ===============================================================
echo Regions: Northern India, China Inland, Southeast Asia Extended, West Africa, Middle East Extended, Eastern Europe, Northern Andes, Central Asia, Oceania Extended
echo Images: 54 (9 regions x 6 weather conditions)
echo Time: 3-4 hours
echo Existing images will be automatically overwritten.
echo.
python regional_fallback_generator.py --config regional_fallback_config.json
goto :RESULT_MENU

:ALL_REGIONS
echo.
echo Starting ALL regions generation...
echo ===============================================================
echo WARNING: This will take 9-14 hours!
echo Existing images will be automatically overwritten.
echo.
set /p "confirm=Are you sure? (y/n): "
if /i "!confirm!"=="y" goto :RUN_ALL
goto :MAIN_MENU

:RUN_ALL
python regional_batch_generator.py --region asia_pacific --config global_cities_config.json
python regional_batch_generator.py --region europe --config global_cities_config.json
python regional_batch_generator.py --region north_america --config global_cities_config.json
python regional_batch_generator.py --region middle_east_africa --config global_cities_config.json
python regional_batch_generator.py --region south_america --config global_cities_config.json
echo ALL REGIONS COMPLETED!
goto :RESULT_MENU

:INDIVIDUAL_MENU
cls
echo.
echo Individual City & Region Selection
echo ===============================================================
echo.
echo MAIN CITIES:
echo [1] Asia-Pacific cities (16 cities)
echo [2] Europe cities (12 cities)
echo [3] North America cities (10 cities)
echo [4] Middle East and Africa cities (9 cities)
echo [5] South America cities (5 cities)
echo.
echo RESORT DESTINATIONS:
echo [6] Resort Cities (15 cities)
echo.
echo REGIONAL FALLBACKS:
echo [7] Regional Fallback Areas (11 regions)
echo.
echo [0] Back to main menu
echo.
echo ** Selected city/region images will be overwritten **
echo.
set /p "region=Select option (0-7): "

if "!region!"=="1" goto :ASIA_PACIFIC_CITIES
if "!region!"=="2" goto :EUROPE_CITIES
if "!region!"=="3" goto :NORTH_AMERICA_CITIES
if "!region!"=="4" goto :MIDDLE_EAST_AFRICA_CITIES
if "!region!"=="5" goto :SOUTH_AMERICA_CITIES
if "!region!"=="6" goto :RESORT_CITIES
if "!region!"=="7" goto :FALLBACK_REGIONS
if "!region!"=="0" goto :MAIN_MENU

echo Invalid selection.
pause
goto :INDIVIDUAL_MENU

:ASIA_PACIFIC_CITIES
cls
echo.
echo Asia-Pacific Cities:
echo ===============================================================
echo [1] Seoul [2] Tokyo [3] Beijing [4] Singapore [5] Bangkok
echo [6] Mumbai [7] Bangalore [8] Jakarta [9] Kuala Lumpur [10] Manila
echo [11] Ho Chi Minh [12] Shanghai [13] Taipei [14] Melbourne [15] Sydney
echo [0] Back
echo.
echo ** Selected city images will be overwritten **
echo.
set /p "city=Select city (0-15): "

if "!city!"=="1" call :SINGLE_CITY "seoul"
if "!city!"=="2" call :SINGLE_CITY "tokyo"
if "!city!"=="3" call :SINGLE_CITY "beijing"
if "!city!"=="4" call :SINGLE_CITY "singapore"
if "!city!"=="5" call :SINGLE_CITY "bangkok"
if "!city!"=="6" call :SINGLE_CITY "mumbai"
if "!city!"=="7" call :SINGLE_CITY "bangalore"
if "!city!"=="8" call :SINGLE_CITY "jakarta"
if "!city!"=="9" call :SINGLE_CITY "kuala_lumpur"
if "!city!"=="10" call :SINGLE_CITY "manila"
if "!city!"=="11" call :SINGLE_CITY "ho_chi_minh"
if "!city!"=="12" call :SINGLE_CITY "shanghai"
if "!city!"=="13" call :SINGLE_CITY "taipei"
if "!city!"=="14" call :SINGLE_CITY "melbourne"
if "!city!"=="15" call :SINGLE_CITY "sydney"
if "!city!"=="0" goto :INDIVIDUAL_MENU

echo Invalid selection.
pause
goto :ASIA_PACIFIC_CITIES

:EUROPE_CITIES
cls
echo.
echo Europe Cities:
echo ===============================================================
echo [1] London [2] Paris [3] Berlin [4] Amsterdam [5] Zurich
echo [6] Stockholm [7] Barcelona [8] Rome [9] Istanbul [10] Moscow
echo [11] Prague [12] Vienna
echo [0] Back
echo.
echo ** Selected city images will be overwritten **
echo.
set /p "city=Select city (0-12): "

if "!city!"=="1" call :SINGLE_CITY "london"
if "!city!"=="2" call :SINGLE_CITY "paris"
if "!city!"=="3" call :SINGLE_CITY "berlin"
if "!city!"=="4" call :SINGLE_CITY "amsterdam"
if "!city!"=="5" call :SINGLE_CITY "zurich"
if "!city!"=="6" call :SINGLE_CITY "stockholm"
if "!city!"=="7" call :SINGLE_CITY "barcelona"
if "!city!"=="8" call :SINGLE_CITY "rome"
if "!city!"=="9" call :SINGLE_CITY "istanbul"
if "!city!"=="10" call :SINGLE_CITY "moscow"
if "!city!"=="11" call :SINGLE_CITY "prague"
if "!city!"=="12" call :SINGLE_CITY "vienna"
if "!city!"=="0" goto :INDIVIDUAL_MENU

echo Invalid selection.
pause
goto :EUROPE_CITIES

:NORTH_AMERICA_CITIES
cls
echo.
echo North America Cities:
echo ===============================================================
echo [1] New York [2] Los Angeles [3] Chicago [4] Toronto [5] Boston
echo [6] Miami [7] San Francisco [8] Washington DC [9] Seattle [10] Vancouver
echo [0] Back
echo.
echo ** Selected city images will be overwritten **
echo.
set /p "city=Select city (0-10): "

if "!city!"=="1" call :SINGLE_CITY "new_york"
if "!city!"=="2" call :SINGLE_CITY "los_angeles"
if "!city!"=="3" call :SINGLE_CITY "chicago"
if "!city!"=="4" call :SINGLE_CITY "toronto"
if "!city!"=="5" call :SINGLE_CITY "boston"
if "!city!"=="6" call :SINGLE_CITY "miami"
if "!city!"=="7" call :SINGLE_CITY "san_francisco"
if "!city!"=="8" call :SINGLE_CITY "washington_dc"
if "!city!"=="9" call :SINGLE_CITY "seattle"
if "!city!"=="10" call :SINGLE_CITY "vancouver"
if "!city!"=="0" goto :INDIVIDUAL_MENU

echo Invalid selection.
pause
goto :NORTH_AMERICA_CITIES

:MIDDLE_EAST_AFRICA_CITIES
cls
echo.
echo Middle East and Africa Cities:
echo ===============================================================
echo [1] Dubai [2] Riyadh [3] Tehran [4] Cairo
echo [5] Johannesburg [6] Nairobi [7] Casablanca [8] Tel Aviv [9] Lagos
echo [0] Back
echo.
echo ** Selected city images will be overwritten **
echo.
set /p "city=Select city (0-9): "

if "!city!"=="1" call :SINGLE_CITY "dubai"
if "!city!"=="2" call :SINGLE_CITY "riyadh"
if "!city!"=="3" call :SINGLE_CITY "tehran"
if "!city!"=="4" call :SINGLE_CITY "cairo"
if "!city!"=="5" call :SINGLE_CITY "johannesburg"
if "!city!"=="6" call :SINGLE_CITY "nairobi"
if "!city!"=="7" call :SINGLE_CITY "casablanca"
if "!city!"=="8" call :SINGLE_CITY "tel_aviv"
if "!city!"=="9" call :SINGLE_CITY "lagos"
if "!city!"=="0" goto :INDIVIDUAL_MENU

echo Invalid selection.
pause
goto :MIDDLE_EAST_AFRICA_CITIES

:SOUTH_AMERICA_CITIES
cls
echo.
echo South America Cities:
echo ===============================================================
echo [1] Sao Paulo [2] Rio de Janeiro [3] Buenos Aires [4] Santiago [5] Mexico City
echo [0] Back
echo.
echo ** Selected city images will be overwritten **
echo.
set /p "city=Select city (0-5): "

if "!city!"=="1" call :SINGLE_CITY "sao_paulo"
if "!city!"=="2" call :SINGLE_CITY "rio_de_janeiro"
if "!city!"=="3" call :SINGLE_CITY "buenos_aires"
if "!city!"=="4" call :SINGLE_CITY "santiago"
if "!city!"=="5" call :SINGLE_CITY "mexico_city"
if "!city!"=="0" goto :INDIVIDUAL_MENU

echo Invalid selection.
pause
goto :SOUTH_AMERICA_CITIES

:RESORT_CITIES
cls
echo.
echo Resort Destination Cities:
echo ===============================================================
echo TROPICAL RESORTS:
echo [1] Maldives [2] Phuket [3] Bali [4] Cancun [5] Hawaii
echo.
echo MOUNTAIN RESORTS:
echo [6] Aspen [7] Zermatt [8] Tahiti [9] Queenstown
echo.
echo CULTURAL DESTINATIONS:
echo [10] Sapporo [11] Dubrovnik [12] Petra [13] Santorini [14] Machu Picchu [15] Angkor Wat
echo [0] Back
echo.
echo ** Selected city images will be overwritten **
echo.
set /p "city=Select city (0-15): "

if "!city!"=="1" call :SINGLE_RESORT_CITY "maldives"
if "!city!"=="2" call :SINGLE_RESORT_CITY "phuket"
if "!city!"=="3" call :SINGLE_RESORT_CITY "bali"
if "!city!"=="4" call :SINGLE_RESORT_CITY "cancun"
if "!city!"=="5" call :SINGLE_RESORT_CITY "hawaii"
if "!city!"=="6" call :SINGLE_RESORT_CITY "aspen"
if "!city!"=="7" call :SINGLE_RESORT_CITY "zermatt"
if "!city!"=="8" call :SINGLE_RESORT_CITY "tahiti"
if "!city!"=="9" call :SINGLE_RESORT_CITY "queenstown"
if "!city!"=="10" call :SINGLE_RESORT_CITY "sapporo"
if "!city!"=="11" call :SINGLE_RESORT_CITY "dubrovnik"
if "!city!"=="12" call :SINGLE_RESORT_CITY "petra"
if "!city!"=="13" call :SINGLE_RESORT_CITY "santorini"
if "!city!"=="14" call :SINGLE_RESORT_CITY "machu_picchu"
if "!city!"=="15" call :SINGLE_RESORT_CITY "angkor_wat"
if "!city!"=="0" goto :INDIVIDUAL_MENU

echo Invalid selection.
pause
goto :RESORT_CITIES

:FALLBACK_REGIONS
cls
echo.
echo Regional Fallback Areas:
echo ===============================================================
echo HIGH PRIORITY:
echo [1] Northern India [2] China Inland [3] China South [4] Southeast Asia Extended [5] West Africa [6] Middle East Extended
echo.
echo MEDIUM PRIORITY:
echo [7] East Africa [8] Eastern Europe [9] Northern Andes
echo.
echo LOW PRIORITY:
echo [10] Central Asia [11] Oceania Extended
echo.
echo [0] Back
echo.
echo ** Selected region images will be overwritten **
echo.
set /p "fallback=Select region (0-11): "

if "!fallback!"=="1" call :SINGLE_FALLBACK "northern_india"
if "!fallback!"=="2" call :SINGLE_FALLBACK "china_inland"
if "!fallback!"=="3" call :SINGLE_FALLBACK "china_south"
if "!fallback!"=="4" call :SINGLE_FALLBACK "southeast_asia_extended"
if "!fallback!"=="5" call :SINGLE_FALLBACK "west_africa"
if "!fallback!"=="6" call :SINGLE_FALLBACK "middle_east_extended"
if "!fallback!"=="7" call :SINGLE_FALLBACK "east_africa"
if "!fallback!"=="8" call :SINGLE_FALLBACK "eastern_europe"
if "!fallback!"=="9" call :SINGLE_FALLBACK "northern_andes"
if "!fallback!"=="10" call :SINGLE_FALLBACK "central_asia"
if "!fallback!"=="11" call :SINGLE_FALLBACK "oceania_extended"
if "!fallback!"=="0" goto :INDIVIDUAL_MENU

echo Invalid selection.
pause
goto :FALLBACK_REGIONS

:SINGLE_FALLBACK
echo.
echo Generating regional fallback: %~1
echo ===============================================================
echo Images: 6 (1 region x 6 weather conditions)
echo Estimated time: 12-24 minutes
echo Existing images will be overwritten.
echo.

python create_single_config.py %~1

if exist temp_single_fallback_config.json (
    python regional_fallback_generator.py --regions %~1 --config temp_single_fallback_config.json
    del temp_single_fallback_config.json > nul 2>&1
    echo Single region generation completed!
) else (
    echo Error creating config for region: %~1
    pause
)

goto :RESULT_MENU

:SINGLE_CITY
echo.
echo Generating single city: %~1
echo ===============================================================
echo Images: 6 (1 city x 6 weather conditions)
echo Estimated time: 12-24 minutes
echo Existing images will be overwritten.
echo.

python create_single_config.py %~1

if exist temp_single_city_config.json (
    python regional_batch_generator.py --region single_city --config temp_single_city_config.json
    del temp_single_city_config.json > nul 2>&1
    echo Single city generation completed!
) else (
    echo Error creating config for city: %~1
    pause
)

goto :RESULT_MENU

:SINGLE_RESORT_CITY
echo.
echo Generating resort city: %~1
echo ===============================================================
echo Images: 6 (1 city x 6 weather conditions)
echo Estimated time: 12-24 minutes
echo Existing images will be overwritten.
echo.

python create_single_config.py %~1 --resort

if exist temp_single_resort_config.json (
    python regional_batch_generator.py --resort single_city --config temp_single_resort_config.json
    del temp_single_resort_config.json > nul 2>&1
    echo Single resort city generation completed!
) else (
    echo Error creating config for resort city: %~1
    pause
)

goto :RESULT_MENU

:TEST_RUN
echo.
echo Test Run - First 2 cities from Asia-Pacific
echo ===============================================================
echo Cities: Seoul, Tokyo
echo Images: 12 (2 cities x 6 weather conditions)
echo Time: 30 minutes
echo Existing images will be overwritten.
echo.
python regional_batch_generator.py --region asia_pacific --config global_cities_config.json
echo Test completed!
goto :RESULT_MENU

:WEATHER_SELECT
cls
echo.
echo Weather Selection Generation
echo ===============================================================
echo Available weather types: sunny, cloudy, rainy, snowy, sunset, foggy
echo Example: sunny cloudy
echo.
echo ** Region images will be overwritten **
echo.
set /p "weather=Enter weather types (space separated): "
echo.
echo Select region:
echo [1] Asia-Pacific [2] Europe [3] North America [4] Middle East/Africa [5] South America
set /p "region_choice=Region: "

set "region_name="
if "!region_choice!"=="1" set "region_name=asia_pacific"
if "!region_choice!"=="2" set "region_name=europe"
if "!region_choice!"=="3" set "region_name=north_america"
if "!region_choice!"=="4" set "region_name=middle_east_africa"
if "!region_choice!"=="5" set "region_name=south_america"

if not "!region_name!"=="" (
    echo.
    echo Generating !region_name! region with weather: !weather!
    echo Existing images will be overwritten.
    echo.
    python regional_batch_generator.py --region !region_name! --config global_cities_config.json --weather !weather!
    goto :RESULT_MENU
) else (
    echo Invalid region selection.
    pause
    goto :WEATHER_SELECT
)

:SHOW_INFO
echo.
echo Region and Timezone Information
echo ===============================================================
python regional_batch_generator.py --list --config global_cities_config.json
echo.
pause
goto :MAIN_MENU

:RESULT_MENU
echo.
echo ===============================================================
echo Generation completed!
echo ===============================================================
echo.
echo Results saved to: ComfyUI/output/timezones/
echo Existing images have been replaced with new ones.
echo.
echo [1] Generate another region/city
echo [2] Open result folder
echo [3] Clear all generated images
echo [0] Exit
echo.
set /p "result=Select: "

if "!result!"=="1" goto :MAIN_MENU
if "!result!"=="2" (
    echo Opening result folder...
    if exist "..\ComfyUI\output\timezones" (
        start "" explorer "..\ComfyUI\output\timezones"
    ) else (
        echo Result folder does not exist.
        pause
    )
    goto :RESULT_MENU
)
if "!result!"=="3" goto :CLEAR_RESULTS
if "!result!"=="0" goto :EXIT

goto :RESULT_MENU

:CLEAR_RESULTS
echo.
echo ===============================================================
echo Clear Generated Images
echo ===============================================================
echo.
echo Do you want to delete all generated images?
echo.
set /p "clear_confirm=Are you sure? (y/n): "
if /i "!clear_confirm!"=="y" (
    if exist "..\ComfyUI\output\timezones" (
        rmdir /s /q "..\ComfyUI\output\timezones" > nul 2>&1
        echo All generated images have been deleted.
    ) else (
        echo No images to delete.
    )
) else (
    echo Deletion cancelled.
)
echo.
pause
goto :RESULT_MENU

:EXIT
echo.
echo Exiting FLUX Krea Global City Image Generator.
echo.
echo Generated images can be used in your Flutter app!
echo Check the ComfyUI/output/timezones/ folder for results.
echo.
echo ** Note: ComfyUI automatically overwrites files with same name **
echo.
pause
exit /b 0
