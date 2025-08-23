#!/usr/bin/env bash
set -e

# --- Detect OS / shell ---
OS="$(uname -s 2>/dev/null || echo unknown)"
IS_POWERSHELL=false
if [[ "$OS" == MINGW* ]] || [[ "$OS" == CYGWIN* ]] || [[ "$OS" == MSYS* ]]; then
    # Detect PowerShell by checking PSModulePath
    if [[ ! -z "$PSModulePath" ]]; then
        IS_POWERSHELL=true
    fi
fi

# --- Function to print colored messages ---
color_echo() {
    local color="$1"
    shift
    local text="$*"

    if [[ "$IS_POWERSHELL" = true ]]; then
        # Prefer pwsh if available
        if command -v pwsh >/dev/null 2>&1; then
            pwsh -Command "Write-Host '$text' -ForegroundColor $color"
        elif command -v powershell.exe >/dev/null 2>&1; then
            powershell.exe -Command "Write-Host '$text' -ForegroundColor $color"
        else
            echo "$text"
        fi
    else
        # Bash / macOS / Linux ANSI colors
        case $color in
            Red) echo -e "\e[31m$text\e[0m" ;;
            Green) echo -e "\e[32m$text\e[0m" ;;
            Yellow) echo -e "\e[33m$text\e[0m" ;;
            Blue) echo -e "\e[34m$text\e[0m" ;;
            Magenta) echo -e "\e[35m$text\e[0m" ;;
            Cyan) echo -e "\e[36m$text\e[0m" ;;
            *) echo "$text" ;;
        esac
    fi
}

# --- Function to check if command exists ---
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

color_echo Yellow "Detecting OS..."
OS="$(uname -s)"

# --- macOS ---
if [[ "$OS" == "Darwin" ]]; then
    color_echo Blue "macOS detected"

    if ! command_exists brew; then
        color_echo Yellow "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.bashrc
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi

    if ! command_exists python3; then
        color_echo Yellow "Installing Python..."
        brew install python
    else
        color_echo Green "Python already installed: $(python3 --version)"
    fi

# --- Windows (Git Bash / MSYS / Cygwin) ---
elif [[ "$OS" == "MINGW"* || "$OS" == "CYGWIN"* || "$OS" == "MSYS"* ]]; then
    color_echo Blue "Windows detected"

    if command_exists py; then
        color_echo Green "Python already installed: $(py -3 --version)"
    else
        color_echo Yellow "Installing Python..."

        if command_exists winget; then
            winget install -e --id Python.Python.3
        elif command_exists choco; then
            choco install -y python
        else
            color_echo Red "Neither winget nor choco found. Install Python manually from https://www.python.org/downloads/"
            exit 1
        fi
    fi

else
    color_echo Red "Unsupported OS: $OS"
    exit 1
fi

# --- Ensure python & pip commands ---
if command_exists python; then
    PYTHON_CMD="python"
elif command_exists py; then
    PYTHON_CMD="py -3"
elif command_exists python3; then
    PYTHON_CMD="python3"
else
    color_echo Red "Python not found even after installation"
    exit 1
fi

if ! command_exists pip3 && ! command_exists pip; then
    color_echo Yellow "Installing pip..."
    curl -sS https://bootstrap.pypa.io/get-pip.py | $PYTHON_CMD
fi

# --- Ensure 'python' alias exists ---
if ! command_exists python; then
    color_echo Yellow "Adding alias 'python' -> $PYTHON_CMD"
    echo "alias python='$PYTHON_CMD'" >> ~/.bashrc
    source ~/.bashrc
fi

# --- Ensure 'pip' alias exists ---
if ! command_exists pip; then
    if command_exists pip3; then
        echo "alias pip='pip3'" >> ~/.bashrc
        source ~/.bashrc
    fi
fi

# --- Install required libraries ---
color_echo Yellow "Installing required Python libraries..."

pip install --upgrade pip

if [[ -f "requirements.txt" ]]; then
    color_echo Yellow "Found requirements.txt — installing..."
    pip install -r requirements.txt
else
    color_echo Yellow "No requirements.txt found. Installing pygame as default."
    pip install pygame
fi

color_echo Green "Setup complete!"
$PYTHON_CMD --version
pip --version