#!/bin/bash

# Script to install managed monitoring for Scenario A (opentelemetry-instrument)
# For Scenario B, use: PYTHONPATH=/path/to/poc:$PYTHONPATH python test_scenario_b_manual.py

set -e

echo "==================================================================="
echo "Installing Managed Monitoring for Scenario A"
echo "==================================================================="
echo

# Get the virtual environment's site-packages directory
VENV_SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")
TARGET_DIR="$VENV_SITE_PACKAGES/opentelemetry/instrumentation/auto_instrumentation"
TARGET_FILE="$TARGET_DIR/sitecustomize.py"
BACKUP_FILE="$TARGET_DIR/sitecustomize.py.original"

echo "Target: $TARGET_FILE"
echo

# Check if target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "ERROR: Target directory not found: $TARGET_DIR"
    echo "Make sure opentelemetry-instrumentation is installed."
    exit 1
fi

# Backup original file if not already backed up
if [ -f "$TARGET_FILE" ] && [ ! -f "$BACKUP_FILE" ]; then
    echo "Backing up original sitecustomize.py..."
    cp "$TARGET_FILE" "$BACKUP_FILE"
    echo "✓ Backup: $BACKUP_FILE"
    echo
fi

# Install Scenario A
echo "Installing managed monitoring sitecustomize.py..."
cp sitecustomize_replacement.py "$TARGET_FILE"
echo "✓ Installed!"
echo

# Copy my_managed_lib.py to the same directory
echo "Copying my_managed_lib.py..."
cp my_managed_lib.py "$TARGET_DIR/"
echo "✓ Copied!"
echo

echo "==================================================================="
echo "✅ Installation Complete!"
echo "==================================================================="
echo
echo "Scenario A (opentelemetry-instrument):"
echo "  opentelemetry-instrument python test_scenario_a_auto.py"
echo
echo "Scenario B (manual initialization):"
echo "  PYTHONPATH=\$(pwd):\$PYTHONPATH python test_scenario_b_manual.py"
echo
echo "To restore original:"
echo "  cp $BACKUP_FILE $TARGET_FILE"
echo
