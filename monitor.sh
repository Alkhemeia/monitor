#!/bin/bash
set -euo pipefail

# Language detection
LANG_CODE="en"
if [[ "${LANG:-}" =~ ^de ]]; then
    LANG_CODE="de"
elif [[ "${LANG:-}" =~ ^es ]]; then
    LANG_CODE="es"
elif [[ "${LANG:-}" =~ ^fr ]]; then
    LANG_CODE="fr"
elif command -v locale >/dev/null 2>&1; then
    LOC=$(locale | grep LANG= | cut -d= -f2 | cut -d_ -f1 | tr '[:upper:]' '[:lower:]')
    if [[ "$LOC" == "de" || "$LOC" == "es" || "$LOC" == "fr" ]]; then
        LANG_CODE="$LOC"
    fi
fi

if [ "$LANG_CODE" = "de" ]; then
    TXT_HELP_USAGE="Verwendung: $0 [Optionen]"
    TXT_HELP_DESC="Startet den Screen Color Monitor."
    TXT_HELP_OPTS="Optionen:"
    TXT_HELP_SHOW="  -h, --help    Zeigt diese Hilfe an"
    TXT_CHECK_DEP="Prüfe Abhängigkeiten für Screen Color Monitor..."
    TXT_ERR_PY="Fehler: Python 3 ist nicht installiert!"
    TXT_MISSING_TK="- tkinter fehlt"
    TXT_MISSING_PIL="- PIL.ImageTk (Pillow-Tkinter) fehlt"
    TXT_MISSING_NP="- numpy fehlt"
    TXT_MISSING_XTST="- libXtst (XTest-Erweiterung) fehlt"
    TXT_DEP_MISSING="Es fehlen benötigte Abhängigkeiten."
    TXT_PROMPT_INSTALL="Möchtest du die Abhängigkeiten jetzt automatisch über apt installieren? (j/n): "
    TXT_START_INSTALL="Starte Installation (sudo benötigt)..."
    TXT_INSTALL_DONE="Installation abgeschlossen!"
    TXT_CANCELLED="Abgebrochen. Das Tool kann ohne Abhängigkeiten nicht gestartet werden."
    TXT_PRESS_ANY="Drücke eine beliebige Taste zum Beenden..."
    TXT_DEP_OK="Alle Abhängigkeiten sind erfüllt!"
    TXT_STARTING="Starte Screen Color Monitor..."
    TXT_BYE="Auf Wiedersehen!"
elif [ "$LANG_CODE" = "es" ]; then
    TXT_HELP_USAGE="Uso: $0 [Opciones]"
    TXT_HELP_DESC="Inicia el Screen Color Monitor."
    TXT_HELP_OPTS="Opciones:"
    TXT_HELP_SHOW="  -h, --help    Muestra esta ayuda"
    TXT_CHECK_DEP="Comprobando dependencias para Screen Color Monitor..."
    TXT_ERR_PY="Error: ¡Python 3 no está instalado!"
    TXT_MISSING_TK="- falta tkinter"
    TXT_MISSING_PIL="- falta PIL.ImageTk (Pillow-Tkinter)"
    TXT_MISSING_NP="- falta numpy"
    TXT_MISSING_XTST="- falta libXtst (extensión XTest)"
    TXT_DEP_MISSING="Faltan las dependencias necesarias."
    TXT_PROMPT_INSTALL="¿Desea instalar las dependencias automáticamente a través de apt ahora? (s/n): "
    TXT_START_INSTALL="Iniciando instalación (se requiere sudo)..."
    TXT_INSTALL_DONE="¡Instalación completada!"
    TXT_CANCELLED="Cancelado. La herramienta no se puede iniciar sin dependencias."
    TXT_PRESS_ANY="Presione cualquier tecla para salir..."
    TXT_DEP_OK="¡Todas las dependencias están cumplidas!"
    TXT_STARTING="Iniciando Screen Color Monitor..."
    TXT_BYE="¡Adiós!"
elif [ "$LANG_CODE" = "fr" ]; then
    TXT_HELP_USAGE="Utilisation: $0 [Options]"
    TXT_HELP_DESC="Démarre le Screen Color Monitor."
    TXT_HELP_OPTS="Opciones:"
    TXT_HELP_SHOW="  -h, --help    Affiche cette aide"
    TXT_CHECK_DEP="Vérification des dépendances pour Screen Color Monitor..."
    TXT_ERR_PY="Erreur: Python 3 n'est pas installé !"
    TXT_MISSING_TK="- tkinter manquant"
    TXT_MISSING_PIL="- PIL.ImageTk (Pillow-Tkinter) manquant"
    TXT_MISSING_NP="- numpy manquant"
    TXT_MISSING_XTST="- libXtst (extension XTest) manquant"
    TXT_DEP_MISSING="Des dépendances requises sont manquantes."
    TXT_PROMPT_INSTALL="Voulez-vous installer les dépendances automatiquement via apt maintenant ? (o/n) : "
    TXT_START_INSTALL="Démarrage de l'installation (sudo requis)..."
    TXT_INSTALL_DONE="Installation terminée !"
    TXT_CANCELLED="Annulé. L'outil ne peut pas démarrer sans les dépendances."
    TXT_PRESS_ANY="Appuyez sur n'importe quelle touche pour quitter..."
    TXT_DEP_OK="Toutes les dépendances sont respectées !"
    TXT_STARTING="Démarrage de Screen Color Monitor..."
    TXT_BYE="Au revoir !"
else
    TXT_HELP_USAGE="Usage: $0 [options]"
    TXT_HELP_DESC="Starts the Screen Color Monitor."
    TXT_HELP_OPTS="Options:"
    TXT_HELP_SHOW="  -h, --help    Shows this help"
    TXT_CHECK_DEP="Checking dependencies for Screen Color Monitor..."
    TXT_ERR_PY="Error: Python 3 is not installed!"
    TXT_MISSING_TK="- tkinter is missing"
    TXT_MISSING_PIL="- PIL.ImageTk (Pillow-Tkinter) is missing"
    TXT_MISSING_NP="- numpy is missing"
    TXT_MISSING_XTST="- libXtst (XTest extension) is missing"
    TXT_DEP_MISSING="Required dependencies are missing."
    TXT_PROMPT_INSTALL="Do you want to install dependencies automatically via apt now? (y/n): "
    TXT_START_INSTALL="Starting installation (sudo required)..."
    TXT_INSTALL_DONE="Installation completed!"
    TXT_CANCELLED="Cancelled. The tool cannot run without dependencies."
    TXT_PRESS_ANY="Press any key to exit..."
    TXT_DEP_OK="All dependencies are fulfilled!"
    TXT_STARTING="Starting Screen Color Monitor..."
    TXT_BYE="Goodbye!"
fi

show_help() {
    echo "$TXT_HELP_USAGE"
    echo ""
    echo "$TXT_HELP_DESC"
    echo ""
    echo "$TXT_HELP_OPTS"
    echo "$TXT_HELP_SHOW"
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    show_help
    exit 0
fi

# Terminal-Emulator-Autostart bei Doppelklick
if [ ! -t 0 ]; then
    for term in xfce4-terminal gnome-terminal xterm kitty alacritty konsole; do
        if command -v "$term" >/dev/null 2>&1; then
            if [[ "$term" == "gnome-terminal" ]]; then
                exec gnome-terminal -- "$0"
            else
                exec "$term" -e "$0"
            fi
            exit 0
        fi
    done
fi

# Farbdefinitionen für ein schönes UI
BG_BLUE="\033[1;34m"
FG_GREEN="\033[0;32m"
FG_YELLOW="\033[0;33m"
FG_RED="\033[0;31m"
FG_CYAN="\033[0;36m"
NC="\033[0m" # No Color

check_and_install_dependencies() {
    local missing=0
    
    echo -e "${FG_YELLOW}$TXT_CHECK_DEP${NC}"
    
    # Prüfe Python 3
    if ! command -v python3 >/dev/null 2>&1; then
        echo -e "${FG_RED}$TXT_ERR_PY${NC}"
        missing=1
    fi
    
    # Prüfe Module im System-Python
    if ! python3 -c "import tkinter" >/dev/null 2>&1; then
        echo -e "${FG_RED}$TXT_MISSING_TK${NC}"
        missing=1
    fi
    if ! python3 -c "from PIL import ImageTk" >/dev/null 2>&1; then
        echo -e "${FG_RED}$TXT_MISSING_PIL${NC}"
        missing=1
    fi
    if ! python3 -c "import numpy" >/dev/null 2>&1; then
        echo -e "${FG_RED}$TXT_MISSING_NP${NC}"
        missing=1
    fi
    
    # Prüfe X11 Test-Bibliotheken via Python ctypes find_library
    if ! python3 -c "from ctypes.util import find_library; import sys; sys.exit(0 if find_library('Xtst') else 1)" >/dev/null 2>&1; then
        echo -e "${FG_RED}$TXT_MISSING_XTST${NC}"
        missing=1
    fi

    if [ "$missing" -eq 1 ]; then
        echo -e "\n${FG_YELLOW}$TXT_DEP_MISSING${NC}"
        read -p "$TXT_PROMPT_INSTALL" choice
        case "$choice" in 
            j|J|ja|Ja|y|Y|yes|Yes|o|O|oui|Oui|s|S|si|Si)
                echo -e "${FG_CYAN}$TXT_START_INSTALL${NC}"
                sudo apt update
                sudo apt install -y python3-tk python3-pil.imagetk python3-numpy python3-pil libxtst6 libx11-6
                echo -e "${FG_GREEN}$TXT_INSTALL_DONE${NC}"
                ;;
            *)
                echo -e "${FG_RED}$TXT_CANCELLED${NC}"
                read -n 1 -s -r -p "$TXT_PRESS_ANY"
                return 1
                ;;
        esac
    else
        echo -e "${FG_GREEN}$TXT_DEP_OK${NC}"
    fi
    return 0
}

if check_and_install_dependencies; then
    echo -e "${FG_CYAN}$TXT_STARTING${NC}"
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    python3 "$SCRIPT_DIR/python/color_monitor/color_monitor.py"
fi
