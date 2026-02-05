@echo off
set PROJECT=WinCleanerPro

echo =========================================
echo  Creando estructura %PROJECT%
echo =========================================

:: Carpeta raíz
mkdir %PROJECT%

:: Core
mkdir %PROJECT%\core

:: Addons
mkdir %PROJECT%\addons
mkdir %PROJECT%\addons\windows
mkdir %PROJECT%\addons\browsers

:: Idiomas y logs
mkdir %PROJECT%\languages
mkdir %PROJECT%\logs

:: Archivos principales
echo. > %PROJECT%\main.py
echo. > %PROJECT%\config.ini

:: Core files
echo. > %PROJECT%\core\gui.py
echo. > %PROJECT%\core\addon_manager.py
echo. > %PROJECT%\core\cleaner_engine.py
echo. > %PROJECT%\core\config.py
echo. > %PROJECT%\core\logger.py

:: Addons Windows
echo. > %PROJECT%\addons\windows\temp_files.py
echo. > %PROJECT%\addons\windows\recycle_bin.py

:: Addons Browsers
echo. > %PROJECT%\addons\browsers\chrome_cache.py

:: Idiomas
echo { } > %PROJECT%\languages\es.json

echo.
echo =========================================
echo  Estructura creada correctamente
echo =========================================
echo.
echo Proyecto listo en: %CD%\%PROJECT%
echo.
pause
