@echo off
chcp 65001 >nul

:: Detect system language
set "LANG_CODE=en"
for /f "tokens=3" %%a in ('reg query "HKU\Control Panel\Desktop" /v PreferredUILanguages 2^>nul') do (
    set "UI_LANG=%%a"
)
if defined UI_LANG (
    set "UI_LANG=%UI_LANG:~0,2%"
) else (
    for /f "tokens=3" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Nls\Language" /v InstallLanguage 2^>nul') do (
        set "INSTALL_LANG=%%a"
    )
    if "%INSTALL_LANG%"=="0407" set "LANG_CODE=de"
    if "%INSTALL_LANG%"=="0c0a" set "LANG_CODE=es"
    if "%INSTALL_LANG%"=="040c" set "LANG_CODE=fr"
)
if "%UI_LANG%"=="de" set "LANG_CODE=de"
if "%UI_LANG%"=="es" set "LANG_CODE=es"
if "%UI_LANG%"=="fr" set "LANG_CODE=fr"

if "%LANG_CODE%"=="de" (
    set "TXT_TITLE=Screen Color Monitor Launcher"
    set "TXT_CHECK_DEP=Prüfe Abhängigkeiten für Screen Color Monitor..."
    set "TXT_ERR_PATH=Fehler: Python ist nicht in deiner PATH-Umgebungsvariable gefunden!"
    set "TXT_ERR_PATH_INSTALL=Bitte installiere Python und füge es zu PATH hinzu."
    set "TXT_MISSING_LIBS=Es fehlen benötigte Python-Bibliotheken (Pillow, numpy)."
    set "TXT_PROMPT_INSTALL=Möchtest du sie jetzt automatisch über pip installieren? (j/n): "
    set "TXT_START_INSTALL=Starte Installation über pip..."
    set "TXT_INSTALL_DONE=Installation abgeschlossen!"
    set "TXT_CANCELLED=Abgebrochen."
    set "TXT_STARTING=Starte Screen Color Monitor..."
) else if "%LANG_CODE%"=="es" (
    set "TXT_TITLE=Screen Color Monitor Launcher"
    set "TXT_CHECK_DEP=Comprobando dependencias para Screen Color Monitor..."
    set "TXT_ERR_PATH=Error: ¡No se encontró Python en su variable de entorno PATH!"
    set "TXT_ERR_PATH_INSTALL=Por favor, instale Python y agréguelo a PATH."
    set "TXT_MISSING_LIBS=Faltan las bibliotecas de Python necesarias (Pillow, numpy)."
    set "TXT_PROMPT_INSTALL=¿Desea instalarlas automáticamente a través de pip ahora? (s/n): "
    set "TXT_START_INSTALL=Iniciando instalación a través de pip..."
    set "TXT_INSTALL_DONE=¡Instalación completada!"
    set "TXT_CANCELLED=Cancelado."
    set "TXT_STARTING=Iniciando Screen Color Monitor..."
) else if "%LANG_CODE%"=="fr" (
    set "TXT_TITLE=Screen Color Monitor Launcher"
    set "TXT_CHECK_DEP=Vérification des dépendances pour Screen Color Monitor..."
    set "TXT_ERR_PATH=Erreur: Python n'a pas été trouvé dans votre variable d'environnement PATH !"
    set "TXT_ERR_PATH_INSTALL=Veuillez installer Python et l'ajouter à PATH."
    set "TXT_MISSING_LIBS=Des bibliothèques Python requises sont manquantes (Pillow, numpy)."
    set "TXT_PROMPT_INSTALL=Voulez-vous les installer automatiquement via pip maintenant ? (o/n) : "
    set "TXT_START_INSTALL=Démarrage de l'installation via pip..."
    set "TXT_INSTALL_DONE=Installation terminée !"
    set "TXT_CANCELLED=Annulé."
    set "TXT_STARTING=Démarrage de Screen Color Monitor..."
) else (
    set "TXT_TITLE=Screen Color Monitor Launcher"
    set "TXT_CHECK_DEP=Checking dependencies for Screen Color Monitor..."
    set "TXT_ERR_PATH=Error: Python is not found in your PATH environment variable!"
    set "TXT_ERR_PATH_INSTALL=Please install Python and add it to PATH."
    set "TXT_MISSING_LIBS=Required Python libraries are missing (Pillow, numpy)."
    set "TXT_PROMPT_INSTALL=Do you want to install them automatically via pip now? (y/n): "
    set "TXT_START_INSTALL=Starting installation via pip..."
    set "TXT_INSTALL_DONE=Installation completed!"
    set "TXT_CANCELLED=Cancelled."
    set "TXT_STARTING=Starting Screen Color Monitor..."
)

title %TXT_TITLE%

echo %TXT_CHECK_DEP%
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo %TXT_ERR_PATH%
    echo %TXT_ERR_PATH_INSTALL%
    pause
    exit /b
)

python -c "import tkinter, PIL, numpy" >nul 2>&1
if errorlevel 1 (
    echo %TXT_MISSING_LIBS%
    set /p install_choice="%TXT_PROMPT_INSTALL%"
    if /I "%install_choice%"=="j" goto do_install
    if /I "%install_choice%"=="y" goto do_install
    if /I "%install_choice%"=="o" goto do_install
    if /I "%install_choice%"=="s" goto do_install
    echo %TXT_CANCELLED%
    pause
    exit /b
)
goto start_app

:do_install
echo %TXT_START_INSTALL%
pip install pillow numpy
echo.
echo %TXT_INSTALL_DONE%

:start_app
echo.
echo %TXT_STARTING%
python "%~dp0python\color_monitor\color_monitor.py"
exit /b
