#!/usr/bin/env bash

# Antigravity 2.0 Fedora Uninstaller
# Safe, robust, and clean removal utility with interactive menu.

set -euo pipefail

# Text formatters
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BLUE}${BOLD}=== Antigravity Uninstaller ===${NC}"

# Default values
REMOVE_IDE=false
REMOVE_APP=false
INSTALL_SCOPE="all"

show_help() {
    cat << EOF
Usage: $(basename "$0") [options]

Options:
  --ide       Uninstall Antigravity IDE only.
  --app       Uninstall Antigravity 2.0 only.
  --both      Uninstall both variants (complete cleanup).
  --user      Limit scope to user space (~/.local) without requiring root privileges.
  -h, --help  Show this help message.
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --ide)
            REMOVE_IDE=true
            shift
            ;;
        --app|--agent)
            REMOVE_APP=true
            shift
            ;;
        --both)
            REMOVE_IDE=true
            REMOVE_APP=true
            shift
            ;;
        --user)
            INSTALL_SCOPE="user"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option '$1'${NC}" >&2
            show_help
            exit 1
            ;;
    esac
done

# --- INTERACTIVE MENU ---
if [[ "$REMOVE_IDE" == "false" && "$REMOVE_APP" == "false" ]]; then
    if [[ ! -t 0 ]]; then
        echo -e "${RED}Error: Standard input is not a terminal. Please specify what to remove using --ide, --app, or --both.${NC}" >&2
        exit 1
    fi

    echo -e "\n${BOLD}Select what you want to uninstall:${NC}"
    echo -e "  ${GREEN}1)${NC} Uninstall ${BOLD}Antigravity IDE${NC} only"
    echo -e "  ${GREEN}2)${NC} Uninstall ${BOLD}Antigravity 2.0${NC} only"
    echo -e "  ${GREEN}3)${NC} Uninstall ${BOLD}Both${NC} (Complete Cleanup)"
    echo -ne "\nEnter an option [1-3]: "

    read -r OPTION

    case "$OPTION" in
        1)
            REMOVE_IDE=true
            ;;
        2)
            REMOVE_APP=true
            ;;
        3)
            REMOVE_IDE=true
            REMOVE_APP=true
            ;;
        *)
            echo -e "${RED}Invalid option. Canceling uninstallation.${NC}" >&2
            exit 1
            ;;
    esac
fi

# Define target paths
SYSTEM_DESKTOP_DIR="/usr/share/applications"
USER_DESKTOP_DIR="$HOME/.local/share/applications"

# Function to safely delete files/folders
safe_remove() {
    local target="$1"
    local use_sudo="${2:-false}"

    if [ -e "$target" ] || [ -L "$target" ]; then
        echo -e "${YELLOW}Removing: $target${NC}"
        if [ "$use_sudo" = "true" ]; then
            sudo rm -rf "$target"
        else
            rm -rf "$target"
        fi
    fi
}

# --- UNINSTALLATION PROCESS ---

# 1. System-wide removal (Requires sudo if components exist, only executed if scope is not "user")
if [ "$INSTALL_SCOPE" != "user" ]; then
    if [ "$REMOVE_APP" = "true" ]; then
        echo -e "\n${BLUE}Checking for system-wide Antigravity 2.0 components...${NC}"
        safe_remove "/opt/antigravity-Linux" "true"
        safe_remove "/opt/Antigravity-Linux" "true"
        safe_remove "/opt/Antigravity-x64" "true"
        safe_remove "/usr/local/bin/antigravity" "true"
        safe_remove "$SYSTEM_DESKTOP_DIR/antigravity.desktop" "true"
        safe_remove "$SYSTEM_DESKTOP_DIR/antigravity-legacy.desktop" "true"
        safe_remove "$SYSTEM_DESKTOP_DIR/antigravity-2.desktop" "true"
        safe_remove "$SYSTEM_DESKTOP_DIR/antigravity-url-handler.desktop" "true"
    fi

    if [ "$REMOVE_IDE" = "true" ]; then
        echo -e "\n${BLUE}Checking for system-wide Antigravity IDE components...${NC}"
        safe_remove "/opt/antigravity-ide-Linux" "true"
        safe_remove "/usr/local/bin/antigravity-ide" "true"
        safe_remove "$SYSTEM_DESKTOP_DIR/antigravity-ide.desktop" "true"
        safe_remove "$SYSTEM_DESKTOP_DIR/antigravity-ide-legacy.desktop" "true"
    fi

    # Refresh system-wide desktop database if needed
    if [ -d "$SYSTEM_DESKTOP_DIR" ]; then
        sudo update-desktop-database "$SYSTEM_DESKTOP_DIR" || true
    fi
fi


# 2. User-local removal (No sudo required)
if [ "$REMOVE_APP" = "true" ]; then
    echo -e "\n${BLUE}Checking for user-local Antigravity 2.0 components...${NC}"
    safe_remove "$HOME/.local/share/antigravity-Linux" "false"
    safe_remove "$HOME/.local/share/Antigravity-Linux" "false"
    safe_remove "$HOME/.local/share/Antigravity-x64" "false"
    safe_remove "$HOME/.local/bin/antigravity" "false"
    safe_remove "$USER_DESKTOP_DIR/antigravity.desktop" "false"
    safe_remove "$USER_DESKTOP_DIR/antigravity-legacy.desktop" "false"
    safe_remove "$USER_DESKTOP_DIR/antigravity-2.desktop" "false"
fi

if [ "$REMOVE_IDE" = "true" ]; then
    echo -e "\n${BLUE}Checking for user-local Antigravity IDE components...${NC}"
    safe_remove "$HOME/.local/share/antigravity-ide-Linux" "false"
    safe_remove "$HOME/.local/bin/antigravity-ide" "false"
    safe_remove "$USER_DESKTOP_DIR/antigravity-ide.desktop" "false"
    safe_remove "$USER_DESKTOP_DIR/antigravity-ide-legacy.desktop" "false"
fi

# Refresh user desktop database if needed
if [ -d "$USER_DESKTOP_DIR" ]; then
    update-desktop-database "$USER_DESKTOP_DIR" || true
fi

echo -e "\n${GREEN}${BOLD}✓ Uninstallation task completed successfully!${NC}"
