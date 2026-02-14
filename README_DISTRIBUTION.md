# PCB Array Optimizer - Distribution Guide

## Milestone 6: Distribution - IN PROGRESS

This document covers building and distributing standalone executables for the PCB Array Optimizer.

## Linux Build - COMPLETED ✅

### Prerequisites

- Python 3.10 or higher
- Virtual environment with dependencies installed
- PyInstaller (installed automatically by build script)

### Building the Linux Executable

#### Quick Build

Run the build script:
```bash
./build_linux.sh
```

This will:
1. Check for required dependencies
2. Clean previous builds
3. Run PyInstaller
4. Create standalone executable in `dist/PCBArrayOptimizer`

#### Manual Build

If you prefer manual control:
```bash
# Clean previous builds
rm -rf build dist

# Run PyInstaller
venv/bin/pyinstaller pcb_optimizer_linux.spec --clean

# Make executable
chmod +x dist/PCBArrayOptimizer
```

### Output

**Location**: `dist/PCBArrayOptimizer`
**Size**: ~66 MB
**Type**: Single-file executable (all dependencies bundled)

### Running the Executable

```bash
./dist/PCBArrayOptimizer
```

The application will launch with the full GUI interface.

### What's Included

The standalone executable bundles:
- Python 3.12 runtime
- PyQt6 libraries
- ReportLab for PDF generation
- All application code
- Panel template JSON files
- All required dependencies

No installation or additional dependencies needed!

### Distribution

You can distribute the `PCBArrayOptimizer` executable to any Linux system with:
- x86_64 architecture
- glibc 2.39 or compatible
- X11 display server (for GUI)

**No Python installation required on target system!**

### Known Limitations

The executable includes warnings about `libxcb-cursor.so.0` during build. This library is used by Qt for X11 cursor support. The application will work on most systems, but if you encounter cursor-related issues, install the library:

```bash
# Ubuntu/Debian
sudo apt-get install libxcb-cursor0

# Fedora/RHEL
sudo dnf install xcb-util-cursor

# Arch Linux
sudo pacman -S xcb-util-cursor
```

## Windows Build - TODO

### Prerequisites (for building on Windows)

- Python 3.10 or higher
- Virtual environment with dependencies
- PyInstaller

### Build Script

A Windows build script will be created: `build_windows.bat`

### Expected Output

**Location**: `dist\PCBArrayOptimizer.exe`
**Size**: ~70-80 MB (estimated)
**Type**: Single-file executable

### Distribution Notes

Windows executables can be distributed to any Windows 10/11 system without Python installed.

## PyInstaller Configuration

### Linux Spec File: `pcb_optimizer_linux.spec`

Key configurations:
- **One-file mode**: All dependencies in single executable
- **No console**: GUI-only application
- **UPX compression**: Enabled for smaller file size
- **Excludes**: Unnecessary packages (matplotlib, numpy, scipy, pandas, tkinter)
- **Hidden imports**: PyQt6 and ReportLab modules
- **Data files**: Panel template JSON files

### Included Resources

The build includes:
```
src/resources/templates/*.json  → Panel size templates
```

### Hidden Imports

Explicitly included modules:
- PyQt6.QtCore, QtGui, QtWidgets
- ReportLab graphics and PDF generation modules

## File Size Optimization

Current Linux build: **66 MB**

Optimization strategies applied:
- ✅ UPX compression enabled
- ✅ Excluded unnecessary packages (matplotlib, numpy, scipy, pandas, tkinter)
- ✅ One-file mode (no separate DLLs to distribute)

Further optimization possible:
- Strip debug symbols (already applied)
- More aggressive UPX settings (may break compatibility)
- Split to one-directory mode (faster startup, more files)

## Testing the Build

### Basic Smoke Test

```bash
# Test that executable launches
./dist/PCBArrayOptimizer

# Test from command line in headless mode (if supported)
./dist/PCBArrayOptimizer --help  # (not implemented yet)
```

### Full Test Checklist

On target system:
- [ ] Executable launches without errors
- [ ] GUI displays correctly
- [ ] Can enter PCB dimensions
- [ ] Can switch between metric/imperial
- [ ] Optimization runs successfully
- [ ] Results table displays
- [ ] Visualization tab shows panel layout
- [ ] PDF export works
- [ ] Can save/load configurations

## Deployment Options

### Option 1: Direct Distribution

Simply distribute the executable file:
- Zip the file: `PCBArrayOptimizer.zip`
- Upload to GitHub releases
- Share directly

Users extract and run immediately.

### Option 2: Installer Package (Future)

Create an installer with:
- Desktop shortcut
- Start menu entry
- File associations (.json config files)
- Uninstaller

Tools for Linux:
- AppImage
- Flatpak
- Snap package
- Debian package (.deb)
- RPM package (.rpm)

### Option 3: Portable Package

Create a portable distribution:
```
PCBArrayOptimizer-v1.0-Linux/
├── PCBArrayOptimizer          # Executable
├── README.txt                 # Quick start guide
├── LICENSE.txt               # License file
└── examples/                 # Example configuration files
    ├── breakout_board.json
    └── arduino_clone.json
```

## Version Information

Embed version information in builds (future enhancement):
- Version number in executable metadata
- About dialog shows version
- Check for updates feature

## Code Signing (Optional)

For professional distribution:
- Linux: Not typically required
- Windows: Recommended (prevents "Unknown Publisher" warning)

## Distribution Checklist

Before distributing:
- [ ] Test on clean system
- [ ] Verify all features work
- [ ] Check file permissions
- [ ] Include README with instructions
- [ ] Include LICENSE file
- [ ] Create release notes
- [ ] Tag version in git
- [ ] Upload to distribution platform

## Build Artifacts

After building:
```
build/                    # Temporary build files (can be deleted)
dist/
└── PCBArrayOptimizer    # Standalone executable (distribute this)
```

## Troubleshooting

### Build Fails

**Error**: "Module not found"
- Ensure all dependencies in `requirements.txt` are installed
- Check `hiddenimports` in spec file

**Error**: "Library not found"
- Some warnings are expected (libxcb-cursor)
- Critical errors will prevent build completion

### Runtime Errors

**Error**: "Failed to execute script"
- Check PyInstaller warnings during build
- Add missing modules to `hiddenimports`

**Error**: "Qt platform plugin not found"
- Install libxcb-cursor0 on target system
- Check QT_QPA_PLATFORM environment variable

## Next Steps

1. ✅ Linux build complete and working
2. TODO: Create Windows build
3. TODO: Test on multiple systems
4. TODO: Create release packages
5. TODO: Write user documentation
6. TODO: Set up distribution platform (GitHub releases)

## File Locations

```
Project Root/
├── build_linux.sh              # Linux build script
├── pcb_optimizer_linux.spec    # PyInstaller config for Linux
├── dist/
│   └── PCBArrayOptimizer      # Linux executable (66 MB)
└── README_DISTRIBUTION.md     # This file
```

## Resources

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [PyQt6 Deployment](https://www.riverbankcomputing.com/static/Docs/PyQt6/deployment.html)
- [ReportLab Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf)
