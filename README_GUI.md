# PCB Array Optimizer - GUI Application

## Milestone 3: Basic GUI - COMPLETED

The GUI application has been implemented with full functionality for PCB array optimization.

## Features Implemented

### Main Window
- Menu bar with File, Tools, and Help menus
- File operations: New, Open, Save, Save As
- Splitter layout with input panel (left) and results panel (right)
- Optimize and Export to PDF buttons

### Input Panel
- **Unit System Selection**: Toggle between Metric (mm) and Imperial (inches)
- **Unit-Aware Fields**: All dimension inputs automatically convert between units
- **PCB Dimensions**: Width, height, and rotation allowance
- **Array Spacing**: X and Y spacing between PCBs in arrays
- **Array Rails**: Top, bottom, left, right border widths
- **Array Rotation**: Allow arrays to be rotated on panels
- **Panel Size Management**: Uses production panel templates

### Results Panel
- **Results Table**: Displays top 10 optimization results with:
  - Rank
  - Utilization percentage
  - Panel size name
  - Array configuration (e.g., 6x4R for rotated)
  - Arrays on panel (e.g., 3x2)
  - Total PCBs per panel
  - PCB area
- **Configuration Details**: Shows detailed breakdown of selected result
- **Unit-Aware Display**: All dimensions shown in user's selected unit system

### Key Features
- Real-time unit conversion (mm ↔ inches)
- Live configuration updates as inputs change
- Graceful error handling for invalid configurations
- Production panel templates (18x24", 24x18", 18x21")
- Save/load configurations to JSON files

## Running the Application

### Prerequisites
```bash
# Install dependencies (virtual environment recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Launch the GUI
```bash
# Using the launcher script
./pcb_optimizer.py

# Or using the virtual environment
venv/bin/python pcb_optimizer.py

# Or directly
venv/bin/python -m src.main
```

## Usage

1. **Configure PCB Parameters**
   - Select your preferred unit system (Metric or Imperial)
   - Enter PCB dimensions
   - Set array spacing and rail widths
   - Choose rotation options

2. **Run Optimization**
   - Click "Optimize" button
   - Results appear in the table, sorted by utilization

3. **Review Results**
   - Select any row to view detailed configuration
   - Details panel shows:
     - Utilization statistics
     - Panel size information
     - PCB and array configurations
     - Panel layout details

4. **Save/Load Configurations**
   - File → Save to store current configuration
   - File → Open to load previously saved configuration

5. **Export to PDF** (Coming in Milestone 5)
   - Select desired configuration
   - Click "Export to PDF"

## File Structure

```
src/
├── gui/
│   ├── __init__.py          # GUI module exports
│   ├── main_window.py       # Main application window
│   ├── input_panel.py       # Input parameter panel with unit conversion
│   └── results_panel.py     # Results display and details
├── main.py                  # Application entry point
└── ...

pcb_optimizer.py             # Launcher script
```

## Technical Details

### Unit Conversion
- All dimensions stored internally in millimeters (mm)
- Display converts to user's selected unit system
- Imperial displays as inches (for values ≥ 0.1") or mils (for values < 0.1")
- Conversions use exact constant: 1 inch = 25.4 mm

### Optimization Integration
- Uses `LayoutOptimizer.optimize()` from core module
- Returns top 10 configurations by utilization
- Handles invalid configurations gracefully
- Provides user-friendly error messages

### Qt Widgets Used
- `QMainWindow` - Main application window
- `QSplitter` - Resizable panel layout
- `QTableWidget` - Results display
- `QTextEdit` - Details view
- Custom `DimensionInput` widget - Unit-aware input fields

## Testing

All existing tests still pass with GUI code:
```bash
venv/bin/pytest tests/ -v
# 89 passed, 20 warnings
```

## Next Steps

### Milestone 4: Visualization
- 2D preview canvas showing panel layout
- Visual representation of PCBs in arrays
- Dimension annotations
- Clickable elements for details

### Milestone 5: PDF Export
- ReportLab integration
- Multi-page PDF with:
  - Configuration summary
  - Panel layout diagrams
  - Dimension tables
  - Dual-unit annotations

### Milestone 6: Polish & Distribution
- PyInstaller single-file executable
- Platform-specific builds (Windows, Linux)
- Application icon
- Installer/distribution packages
- User documentation
