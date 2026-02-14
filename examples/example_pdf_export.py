#!/usr/bin/env python3
"""
Example: PDF Export

Demonstrates exporting optimization results to PDF.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models import PCB, ArraySpacing, ArrayRails, Configuration, UnitSystem
from src.core import LayoutOptimizer
from src.io.template_manager import TemplateManager
from src.export import PDFExporter


def main():
    print("=" * 70)
    print("PCB Array Optimizer - PDF Export Example")
    print("=" * 70)
    print()

    # Create a simple configuration
    pcb = PCB(
        width=25.4,   # 1.0 inch
        height=20.32,  # 0.8 inch
        allow_rotation=True
    )

    spacing = ArraySpacing(
        x_spacing=2.54,  # 0.10 inch
        y_spacing=2.54
    )

    rails = ArrayRails(
        top=5.0,
        bottom=5.0,
        left=5.0,
        right=5.0
    )

    # Load panel templates (use first 3)
    panel_sizes = TemplateManager.load_default_templates()[:3]

    config = Configuration(
        project_name="1.0\" x 0.8\" Breakout Board",
        pcb=pcb,
        array_spacing=spacing,
        array_rails=rails,
        allow_array_rotation=True,
        panel_sizes=panel_sizes
    )

    print("Running optimization...")
    results = LayoutOptimizer.optimize(config, top_n=10)
    print(f"Found {len(results)} optimal configurations")
    print()

    # Export to PDF
    output_file = "optimization_results.pdf"
    print(f"Exporting to {output_file}...")

    exporter = PDFExporter()
    exporter.export_results(
        file_path=output_file,
        configuration=config,
        results=results,
        selected_panel=results[0] if results else None
    )

    print(f"✓ PDF exported successfully to {output_file}")
    print()

    # Show summary
    print("PDF Contents:")
    print("  - Title page with project summary")
    print("  - Configuration details (PCB, array, rails)")
    print("  - Results table (top 10 configurations)")
    print("  - Detailed panel layouts for top results")
    print("  - Visual diagrams of panel arrangements")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
