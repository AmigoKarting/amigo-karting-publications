@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
echo ============================================
echo   AMIGO KARTING - Recherche de nouvelles
echo ============================================
echo.
echo Je cherche les actualites du moment sur internet...
echo (karting, F1, evenements Gatineau/Outaouais, sorties famille)
echo.
python chercher_nouvelles.py
if errorlevel 1 py chercher_nouvelles.py
echo.
echo --------------------------------------------
echo  Termine !
echo  Ouvre (ou rafraichis avec la touche F5) le fichier :
echo     Idees-Publications-Amigo.html
echo --------------------------------------------
echo.
pause
