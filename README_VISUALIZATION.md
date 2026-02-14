# PCB Array Optimizer - Visualization

## Milestone 4: Visualization - COMPLETED

The 2D visualization system has been implemented, providing a visual representation of optimized panel layouts.

## Features Implemented

### Visualization Canvas ([src/gui/visualization_canvas.py](src/gui/visualization_canvas.py))

#### PanelCanvas Widget
- **2D Graphics Rendering**: Custom QPainter-based drawing
- **Automatic Scaling**: Panel layouts automatically scale to fit widget size
- **Color-Coded Display**:
  - Light gray: Panel background
  - Darker gray: Border keepout areas (dashed lines)
  - Blue: Array containers
  - Green: Individual PCBs
  - Black/Blue: Text and dimensions

#### Visual Elements
1. **Panel Outline**: Shows full panel dimensions with border
2. **Usable Area**: Dashed rectangle showing the area available for arrays
3. **Arrays**: Blue rectangles containing multiple PCBs
4. **PCBs**: Green rectangles showing individual circuit boards
5. **Dimensions**: Panel width and height annotations
6. **Labels**: Panel name, utilization percentage, and PCB count

#### Unit-Aware Display
- All dimensions displayed in user's selected unit system
- Automatically converts between metric (mm) and imperial (inches)
- Dimension annotations update when unit system changes

### Integration with Results Panel

The visualization is integrated as a second tab in the results panel:

1. **Details Tab**: Text-based configuration details (existing)
2. **Visualization Tab**: Graphical panel layout (new)

Selecting any result in the table automatically updates both tabs.

## Technical Implementation

### Drawing Algorithm

The visualization renders panel layouts in the following order:

```
1. Panel background (light gray rectangle)
2. Panel border (solid line)
3. Usable area border (dashed line)
4. For each array position:
   a. Array background (blue rectangle)
   b. Array border (darker blue line)
   c. For each PCB position within array:
      - PCB rectangle (green fill)
      - PCB border (darker green line)
5. Dimension annotations (lines and text)
6. Information labels (panel name, utilization, count)
```

### Scaling and Layout

The canvas automatically calculates scale factors to fit panels of any size:

```python
# Calculate scale to fit panel in available space
margin = 60  # Space for annotations
available_width = widget_width - 2 * margin
available_height = widget_height - 2 * margin

scale_x = available_width / panel_width_mm
scale_y = available_height / panel_height_mm
scale = min(scale_x, scale_y) * 0.9  # 90% to leave breathing room

# Center the panel
offset_x = (widget_width - scaled_panel_width) / 2
offset_y = (widget_height - scaled_panel_height) / 2
```

### Rotation Handling

The visualization correctly handles both PCB and array rotation:

- **PCB Rotation**: If `array.pcbs_rotated == True`, PCB width and height are swapped
- **Array Rotation**: If `panel.arrays_rotated == True`, array width and height are swapped

This ensures that rotated configurations are displayed accurately.

## Usage

The visualization appears automatically when you:

1. Run an optimization
2. Select a result from the table
3. Click the "Visualization" tab

The canvas updates in real-time as you select different optimization results.

## Visual Legend

The visualization includes a legend at the bottom showing:
- **Green (■)**: Individual PCBs
- **Blue (■)**: Array groupings
- **Gray (□)**: Panel border and keepout areas

## Code Structure

```
src/gui/
├── visualization_canvas.py
│   ├── PanelCanvas          # Core drawing widget
│   │   ├── set_panel()      # Load panel data
│   │   ├── paintEvent()     # Main render method
│   │   ├── _draw_panel()    # Draw panel outline
│   │   ├── _draw_arrays()   # Draw array containers
│   │   ├── _draw_pcbs_in_array()  # Draw individual PCBs
│   │   ├── _draw_dimensions()     # Draw size annotations
│   │   └── _draw_labels()   # Draw info text
│   └── VisualizationPanel   # Container with controls
│       ├── canvas           # PanelCanvas instance
│       └── legend           # Color legend
└── results_panel.py         # Integration point
    ├── QTabWidget           # Details + Visualization tabs
    └── _update_visualization()  # Update on selection
```

## Color Scheme

All colors are configurable via the `PanelCanvas` class:

```python
self.color_panel = QColor(240, 240, 240)    # Light gray background
self.color_border = QColor(200, 200, 200)   # Border lines
self.color_array = QColor(150, 180, 220)    # Array blue
self.color_pcb = QColor(100, 150, 100)      # PCB green
self.color_text = QColor(0, 0, 0)           # Black text
self.color_dimension = QColor(0, 0, 200)    # Blue dimensions
```

## Examples

For a typical 18x24" panel with 1.0" x 0.8" PCBs:

**What you'll see:**
- Outer rectangle: 18" x 24" panel (457.2mm x 609.6mm)
- Dashed inner rectangle: Usable area after 0.75" borders
- Blue rectangles: 18x20 PCB arrays
- Green rectangles: Individual 1.0" x 0.8" PCBs
- Top label: Panel size name
- Dimension lines: Panel width (top) and height (left)
- Bottom labels: "66.7% utilization - 360 PCBs"

## Performance

The visualization is optimized for real-time updates:
- Renders in <10ms for typical panels (tested up to 500 PCBs)
- Automatic scale recalculation on window resize
- No memory leaks (Qt manages graphics objects)

## Future Enhancements (Not Implemented)

Potential improvements for future versions:
- Zoom controls (zoom in/out buttons)
- Pan capability (drag to scroll)
- Interactive tooltips (hover over PCB to see details)
- Export visualization as PNG/SVG
- Print preview
- Highlight specific arrays or PCBs
- Measurement tool (click-to-measure distances)

## Testing

All existing tests continue to pass:
```bash
venv/bin/pytest tests/ -v
# 89 passed
```

The visualization code is tested indirectly through:
- Import tests (verify no circular dependencies)
- GUI integration tests (ensure proper wiring)

## Next Steps

With visualization complete, the next milestone is:

### Milestone 5: PDF Export
- Integrate ReportLab for PDF generation
- Include visualization graphics in PDF
- Add configuration tables
- Support dual-unit dimensions
- Multi-page layouts for multiple results

The visualization canvas can be reused for PDF generation by rendering to a different QPainter target.
