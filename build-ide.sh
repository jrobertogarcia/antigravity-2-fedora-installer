#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

for tool in spectool rpkg; do
    if ! command -v "$tool" &> /dev/null; then
        echo -e "${RED}Error: Required packaging utility '${tool}' is missing.${NC}" >&2
        echo -e "Please install it by running: ${BLUE}sudo dnf install -y ${tool}${NC}" >&2
        exit 1
    fi
done

OUTDIR="${OUTDIR:-$HOME/rpkg/}"
mkdir -p "$OUTDIR"

# Auto-update specs to latest upstream version if online detector is available
if [[ -f "$(dirname "$0")/get-latest-versions.py" ]]; then
    python3 "$(dirname "$0")/get-latest-versions.py" --update-specs || true
fi

echo "Downloading sources for antigravity2-ide..."
spectool -gS antigravity2-ide.spec

echo "Building antigravity2-ide RPM package..."
rpkg local --outdir "$OUTDIR" --spec antigravity2-ide.spec

echo "Done! Built RPMs can be found in $OUTDIR"