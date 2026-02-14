#!/bin/bash
#
# Build script for PCB Array Optimizer - Linux
#
# This script creates a standalone executable for Linux using PyInstaller.
#

set -e  # Exit on error

echo "======================================"
echo "PCB Array Optimizer - Linux Build"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run: python3 -m venv venv && venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Check if PyInstaller is installed
if ! venv/bin/python -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller not found. Installing..."
    venv/bin/pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist
mkdir -p dist

# Run PyInstaller
echo ""
echo "Building standalone executable..."
venv/bin/pyinstaller pcb_optimizer_linux.spec --clean

# Check if build succeeded
if [ -f "dist/PCBArrayOptimizer" ]; then
    echo ""
    echo "======================================"
    echo "Build completed successfully!"
    echo "======================================"
    echo ""
    echo "Executable location: dist/PCBArrayOptimizer"

    # Get file size
    SIZE=$(du -h dist/PCBArrayOptimizer | cut -f1)
    echo "File size: $SIZE"

    # Make executable
    chmod +x dist/PCBArrayOptimizer

    echo ""
    echo "To run the application:"
    echo "  ./dist/PCBArrayOptimizer"
    echo ""
else
    echo ""
    echo "Build failed! Check the output above for errors."
    exit 1
fi
