# PCB Array Optimizer - User Guide

## Introduction

PCB Array Optimizer is a tool for calculating optimal arrangements of PCB arrays on production panels to maximize material utilization and minimize waste.

### What It Does

- Calculates optimal PCB array configurations
- Tests multiple panel sizes and orientations
- Finds arrangements with best material utilization
- Provides visual representations of panel layouts
- Exports professional PDF reports

### Why Use This Tool?

When manufacturing PCBs in volume, manufacturers arrange multiple PCBs on large panels. Finding the optimal arrangement can:
- Reduce material costs
- Increase PCBs per panel
- Minimize waste
- Speed up production planning

## Getting Started

### Running the Application

**Linux:**
```bash
./PCBArrayOptimizer
```

**Windows:**
Double-click `PCBArrayOptimizer.exe`

The application window will open with input controls on the left and results area on the right.

## Basic Workflow

### 1. Configure PCB Parameters

#### Unit System
Choose your preferred measurement system:
- **Metric**: Millimeters (mm)
- **Imperial**: Inches (in) and mils (thousandths of an inch)

All inputs and outputs will use your selected units.

#### PCB Dimensions
Enter your PCB size:
- **Width**: Horizontal dimension
- **Height**: Vertical dimension
- **Allow PCB rotation**: Check if PCBs can be rotated 90°

**Example**: For a 1" × 0.8" breakout board:
- Width: 1.0 (inches) or 25.4 (mm)
- Height: 0.8 (inches) or 20.32 (mm)

#### Array Spacing
Spacing between individual PCBs within an array:
- **X Spacing**: Horizontal gap between PCBs
- **Y Spacing**: Vertical gap between PCBs

**Typical values**: 0.1" (2.54mm) for v-scoring, 0.062" (1.57mm) minimum

#### Array Rails
Border/frame around the array edges:
- **Top**: Top edge clearance
- **Bottom**: Bottom edge clearance
- **Left**: Left edge clearance
- **Right**: Right edge clearance

**Typical values**: 5mm (0.2") for mounting and handling

#### Array Options
- **Allow array rotation on panel**: Check if entire arrays can be rotated 90° when placing on panel

### 2. Run Optimization

Click the **"Optimize"** button at the bottom.

The optimizer will:
1. Generate all possible array configurations
2. Test each array on available panel sizes
3. Try both orientations (if rotation allowed)
4. Calculate utilization for each combination
5. Return top 10 results ranked by material utilization

**Processing time**: Usually <1 second for typical configurations

### 3. Review Results

#### Results Table

The table shows top 10 configurations with:
- **Rank**: #1 is best utilization
- **Utilization**: Percentage of panel used for PCBs
- **Panel Size**: Panel template name with dimensions
- **Array Config**: PCBs per array (e.g., "18×20R" means 18×20 with rotation)
- **Arrays on Panel**: Number of arrays on panel
- **Total PCBs**: Total PCBs per panel

Click any row to see details.

#### Details Tab

Shows comprehensive information:
- Utilization statistics
- Panel dimensions and specifications
- Array configuration details
- PCB spacing and rails
- Total counts and areas

#### Visualization Tab

Displays a graphical representation:
- **Gray**: Panel outline
- **Dashed gray**: Usable area (after border keepout)
- **Blue rectangles**: Array containers
- **Green rectangles**: Individual PCBs

The diagram shows actual proportions and layout.

### 4. Export to PDF

Once you have results:
1. Select your preferred configuration in the table
2. Click **"Export to PDF"** button
3. Choose save location
4. Open the generated PDF

The PDF includes:
- Title page with configuration summary
- Detailed specifications
- Results table (all 10 results)
- Visual diagrams of top configurations

Perfect for:
- Sharing with PCB manufacturers
- Documentation
- Project records

## Understanding Results

### Utilization Percentage

The most important metric. Higher is better.

**Formula**: (Total PCB Area / Panel Area) × 100%

**Example**: 66.67% utilization means 2/3 of panel is PCBs, 1/3 is waste

**Good utilization**: 60-75% is excellent for most designs
**Typical range**: 40-70% depending on PCB size and panel size

### Array Configuration

**Format**: `[width]×[height][R]`
- Width: Number of PCBs horizontally
- Height: Number of PCBs vertically
- R: Rotated (if present)

**Examples**:
- `18×20`: 18 PCBs wide, 20 tall, not rotated
- `20×18R`: 20 wide, 18 tall, PCBs rotated 90°
- `1×1`: Single PCB (no array)

### Arrays on Panel

**Format**: `[x]×[y][R]`
- x: Number of arrays horizontally
- y: Number of arrays vertically
- R: Rotated (if present)

**Examples**:
- `1×1`: Single array fills panel
- `2×2`: Four arrays on panel
- `3×2R`: 3×2 arrays, rotated 90°

### Total PCBs per Panel

Multiply to verify:
`(PCBs per Array X) × (PCBs per Array Y) × (Arrays X) × (Arrays Y) = Total PCBs`

**Example**: 18×20 array, 1×1 arrays = 18 × 20 × 1 × 1 = 360 PCBs per panel

## Common Scenarios

### Small PCBs (< 2" / 50mm)

For small PCBs like breakout boards:
- Use larger arrays (10×10 or more)
- Higher utilization achievable (65-75%)
- More arrays may fit on panel
- V-scoring typically used (0.1" spacing)

**Typical result**: 300-500 PCBs per panel

### Medium PCBs (2-4" / 50-100mm)

For development boards, Arduino-sized:
- Arrays of 5×5 to 10×10
- Good utilization (55-70%)
- May fit multiple arrays per panel
- V-scoring or tab routing

**Typical result**: 50-200 PCBs per panel

### Large PCBs (> 4" / 100mm)

For larger boards:
- Smaller arrays (2×2 to 5×5)
- Lower utilization (45-60%)
- Usually single array per panel
- Tab routing typically used

**Typical result**: 10-50 PCBs per panel

### Maximum Density

For highest PCB count:
1. Enable PCB rotation
2. Enable array rotation
3. Use minimum spacing (manufacturer's limit)
4. Use small rails (5mm minimum)
5. Try multiple panel sizes

### Cost Optimization

For lowest cost per PCB:
1. Focus on utilization percentage
2. Consider manufacturer's panel pricing
3. Balance setup costs vs. utilization
4. Check minimum order quantities

## Panel Size Templates

The application includes standard PCB production panel sizes:

### Standard Panels

**18" × 24"** (457.2mm × 609.6mm)
- Most common production size
- Multiple spacing options (0.062", 0.09", 0.10", 0.12")
- Border keepout: 0.75" or 1.0"

**24" × 18"** (609.6mm × 457.2mm)
- Portrait orientation of 18×24
- Same spacing options
- Border keepout: 0.75" or 1.0"

**18" × 21"** (457.2mm × 533.4mm)
- Alternate production size
- Spacing: 0.09", 0.10"
- Border keepout: 0.75" or 1.0"

### Panel Specifications

Each template includes:
- Panel dimensions (width × height)
- Border keepout (unusable edge area)
- Array spacing (gap between arrays)

These match real PCB manufacturer specifications.

## File Operations

### Save Configuration

**File → Save** or **Ctrl+S**

Saves your input parameters to a JSON file:
- PCB dimensions and rotation settings
- Array spacing and rails
- Array rotation setting
- Unit system preference

Does NOT save optimization results.

### Load Configuration

**File → Open** or **Ctrl+O**

Loads a previously saved configuration.

All input fields will be populated with saved values.

### New Configuration

**File → New** or **Ctrl+N**

Resets all inputs to default values.

Clears any existing results.

## Tips and Best Practices

### Optimization Strategy

1. **Start with typical values**:
   - Spacing: 0.1" (2.54mm)
   - Rails: 5mm all around
   - Enable both rotations

2. **Run initial optimization** to see baseline

3. **Adjust parameters** based on results:
   - Reduce spacing if utilization is low
   - Try different rail sizes
   - Disable rotation if results are similar

4. **Compare top results**:
   - Top 3-5 often have similar utilization
   - Consider ease of manufacturing
   - Check manufacturer's preferences

### Understanding Trade-offs

**Tight spacing** (0.062" / 1.57mm)
- Pros: Higher utilization, more PCBs per panel
- Cons: Harder to separate, may need special tooling

**Loose spacing** (0.12" / 3mm+)
- Pros: Easier to separate, less risk of damage
- Cons: Lower utilization, fewer PCBs per panel

**Small rails** (< 5mm)
- Pros: More space for PCBs
- Cons: Less area for tooling holes, may be fragile

**Large rails** (> 10mm)
- Pros: Robust, more mounting options
- Cons: Wastes material

### Manufacturer Coordination

Before finalizing:
1. Check manufacturer's panel size capabilities
2. Verify minimum spacing requirements
3. Confirm tooling hole requirements
4. Ask about preferred array configurations
5. Get quote for different utilization levels

### Documentation

Always export a PDF before manufacturing:
- Provides visual reference
- Shows exact dimensions
- Serves as project documentation
- Can be shared with team/manufacturer

## Troubleshooting

### "No valid panel configuration found"

**Cause**: PCB too large for available panels, or constraints too tight

**Solutions**:
- Check PCB dimensions (typo?)
- Enable PCB rotation
- Try larger panel templates
- Reduce rail sizes
- Reduce spacing (carefully)

### Low Utilization (<40%)

**Causes**:
- PCB size doesn't fit panel geometry well
- Large rails or spacing
- Rotation disabled

**Solutions**:
- Enable all rotation options
- Try different panel sizes
- Reduce rails to minimum (5mm)
- Reduce spacing to manufacturer minimum
- Consider redesigning PCB dimensions if possible

### Results Don't Update

**Solution**: Click "Optimize" button again

The tool doesn't auto-optimize on input changes.

### PDF Export Fails

**Causes**:
- No results to export
- Invalid file path
- Insufficient disk space

**Solution**:
- Run optimization first
- Choose valid save location
- Check disk space

## Keyboard Shortcuts

- **Ctrl+N**: New configuration
- **Ctrl+O**: Open configuration
- **Ctrl+S**: Save configuration
- **Ctrl+Shift+S**: Save as
- **Ctrl+Q**: Quit application

## Technical Specifications

### Input Limits

- **PCB dimensions**: 1mm to 1000mm (or equivalent in inches)
- **Spacing**: 0mm to 100mm
- **Rails**: 0mm to 100mm

### Performance

- **Optimization speed**: <1 second for typical configurations
- **Maximum array size**: 50×50 PCBs (limited to prevent excessive computation)
- **Results returned**: Top 10 configurations

### Accuracy

- **Internal precision**: All calculations in millimeters (mm)
- **Display precision**:
  - Metric: 0.01mm
  - Imperial: 0.001" or 0.1 mil
- **Conversion**: 1 inch = 25.4mm (exact)

## Support and Feedback

### Getting Help

1. Check this user guide
2. Review example configurations
3. Try the example optimization script
4. Check GitHub issues page

### Reporting Issues

When reporting problems, include:
- PCB dimensions used
- Array spacing and rails
- Panel sizes tried
- Error message (if any)
- Expected vs. actual behavior

### Feature Requests

The tool is open source. Feature requests welcome!

Potential future features:
- Custom panel sizes
- Multiple PCB designs on one panel
- Cost calculation
- Panelization score beyond simple utilization
- Export to CAD formats

## Appendix: PCB Manufacturing Terms

**Panel**: Large PCB sheet containing multiple arrays or PCBs

**Array**: Group of identical PCBs arranged in rows and columns

**V-scoring**: V-shaped groove cut between PCBs for easy separation

**Tab routing**: Small tabs holding PCBs to panel, routed/broken for separation

**Border keepout**: Unusable edge area of panel for clamping and tooling

**Tooling holes**: Holes for aligning and securing panel during manufacturing

**Utilization**: Percentage of panel area used for PCBs (vs. waste)

**Rails**: Frame/border around array for structural support

## Version Information

**Application**: PCB Array Optimizer
**Version**: 1.0
**Documentation**: 2026-02-07

---

For more information, visit the project repository or contact the developers.
