# PCB Array Optimizer

An open-source desktop application for optimizing PCB panelization for manufacturing. Given a PCB size, spacing, rail widths, and a supplier's panel dimensions, the optimizer calculates the best array configurations ranked by panel utilization.

## Features

- Calculate optimal PCB-to-array-to-panel configurations
- Support for rotation options at both PCB and array levels
- Multi-unit support (Imperial/Metric) with appropriate precision
- Configurable panel size templates for different PCB manufacturers
- Top results ranked by area utilization
- Interactive visualization popup (double-click a result row)
- PDF export with array graphic and detailed specifications
- Persistent user preferences (unit system, selected supplier panel)
- Cross-platform standalone executables (Linux & Windows)

## Download

Pre-built executables are available from the [Releases](../../releases) page — no Python installation required.

## Development

### Prerequisites

- Python 3.10+
- pip

### Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python pcb_optimizer.py

# Run tests
pip install -r requirements-dev.txt
pytest
```

### Building Standalone Executables

```bash
pip install pyinstaller

# Linux
pyinstaller pcb_optimizer_linux.spec --clean

# Windows
pyinstaller pcb_optimizer_windows.spec --clean
```

Executables are output to the `dist/` directory.

## License

MIT License
