#!/bin/bash
# Start the React development server from the repo root
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT/frontend"

if command -v pnpm >/dev/null 2>&1; then
    PACKAGE_MANAGER="pnpm"
elif command -v npm >/dev/null 2>&1; then
    PACKAGE_MANAGER="npm"
else
    echo "❌ Neither pnpm nor npm is installed." >&2
    exit 1
fi

if [ ! -d node_modules ]; then
    "$PACKAGE_MANAGER" install
fi

"$PACKAGE_MANAGER" run dev

