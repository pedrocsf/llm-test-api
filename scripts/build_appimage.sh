#!/bin/sh
set -eu

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APPIMAGETOOL="${APPIMAGETOOL:-appimagetool}"
PYTHON="${PYTHON:-$PROJECT_ROOT/.venv/bin/python}"
APP_DIR="$PROJECT_ROOT/build/AppDir"
OUTPUT_FILE="$PROJECT_ROOT/dist/LlmEvaluator-x86_64.AppImage"

cd "$PROJECT_ROOT"

"$PYTHON" scripts/prefetch_model.py
"$PYTHON" -m PyInstaller --noconfirm llm_evaluator.spec

rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/usr/lib"
cp -r dist/LlmEvaluator "$APP_DIR/usr/lib/LlmEvaluator"
cp packaging/linux/AppRun "$APP_DIR/AppRun"
cp packaging/linux/llm-evaluator.desktop "$APP_DIR/llm-evaluator.desktop"
cp packaging/linux/llm-evaluator.png "$APP_DIR/llm-evaluator.png"
chmod +x "$APP_DIR/AppRun"

ARCH=x86_64 "$APPIMAGETOOL" "$APP_DIR" "$OUTPUT_FILE"
echo "AppImage gerado em $OUTPUT_FILE"
