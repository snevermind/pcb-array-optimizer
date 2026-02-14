#!/usr/bin/env python3
"""
Example: PCB Array Optimization

This demonstrates the complete optimization workflow using production panel templates.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models import PCB, ArraySpacing, ArrayRails, Configuration, UnitSystem
from src.models.units import UnitConverter
from src.core import LayoutOptimizer
from src.io.template_manager import TemplateManager


def main():
    print("=" * 70)
    print("PCB Array Optimizer - Example Optimization")
    print("=" * 70)
    print()

    # Example 1: Small PCB (common breakout board size)
    print("Example 1: Small Breakout Board (1.0\" x 0.8\")")
    print("-" * 70)

    pcb = PCB(
        width=25.4,   # 1.0 inch in mm
        height=20.32,  # 0.8 inch in mm
        allow_rotation=True
    )

    spacing = ArraySpacing(
        x_spacing=2.54,  # 0.10 inch
        y_spacing=2.54   # 0.10 inch
    )

    rails = ArrayRails(
        top=5.0,
        bottom=5.0,
        left=5.0,
        right=5.0
    )

    # Load production panel templates
    panel_sizes = TemplateManager.load_default_templates()

    # Create configuration
    config = Configuration(
        project_name="Breakout Board v1.0",
        pcb=pcb,
        array_spacing=spacing,
        array_rails=rails,
        allow_array_rotation=True,
        panel_sizes=panel_sizes[:3]  # Use first 3 templates for this example
    )

    print(f"PCB Dimensions: {UnitConverter.format_dimension(pcb.width, UnitSystem.IMPERIAL)} x "
          f"{UnitConverter.format_dimension(pcb.height, UnitSystem.IMPERIAL)}")
    print(f"Array Spacing: {UnitConverter.format_dimension(spacing.x_spacing, UnitSystem.IMPERIAL)}")
    print(f"Panel Templates: {len(config.panel_sizes)}")
    print()

    # Estimate search space
    print("Estimating search space...")
    stats = LayoutOptimizer.estimate_search_space(config)
    print(f"Total combinations to explore: ~{stats['total_combinations']:,}")
    print()

    # Run optimization
    print("Running optimization...")
    results = LayoutOptimizer.optimize(config, top_n=10)

    print(f"\nFound {len(results)} optimal configurations:")
    print()
    print("=" * 70)

    # Display top results
    for i, panel in enumerate(results[:5], 1):
        print(f"\nRank #{i}: {panel.utilization_percentage:.2f}% utilization")
        print(f"  Panel: {panel.panel_size.name}")
        print(f"  Array: {panel.array.pcb_count_x}x{panel.array.pcb_count_y} PCBs "
              f"({'rotated' if panel.array.pcbs_rotated else 'not rotated'})")
        print(f"  Arrays on Panel: {panel.array_count_x}x{panel.array_count_y} "
              f"({'rotated' if panel.arrays_rotated else 'not rotated'})")
        print(f"  Total PCBs per Panel: {panel.total_pcb_count}")
        print(f"  PCB Area: {panel.total_pcb_area:.2f} mm²")
        print(f"  Panel Area: {panel.panel_area:.2f} mm²")

    print()
    print("=" * 70)

    # Example 2: Larger PCB
    print("\n\nExample 2: Arduino-sized Board (2.7\" x 2.1\")")
    print("-" * 70)

    pcb2 = PCB(
        width=68.58,   # 2.7 inches in mm
        height=53.34,  # 2.1 inches in mm
        allow_rotation=True
    )

    config2 = Configuration(
        project_name="Arduino Clone",
        pcb=pcb2,
        array_spacing=spacing,
        array_rails=rails,
        allow_array_rotation=True,
        panel_sizes=panel_sizes[5:7]  # Different panel templates
    )

    print(f"PCB Dimensions: {UnitConverter.format_dimension(pcb2.width, UnitSystem.IMPERIAL)} x "
          f"{UnitConverter.format_dimension(pcb2.height, UnitSystem.IMPERIAL)}")
    print()

    # Find single best
    print("Finding best configuration...")
    best = LayoutOptimizer.find_single_best(config2)

    print(f"\nBest Configuration: {best.utilization_percentage:.2f}% utilization")
    print(f"  Panel: {best.panel_size.name}")
    print(f"  Panel Size: {UnitConverter.format_dual_dimension(best.panel_size.width, UnitSystem.IMPERIAL)} x "
          f"{UnitConverter.format_dual_dimension(best.panel_size.height, UnitSystem.IMPERIAL)}")
    print(f"  Array: {best.array.pcb_count_x}x{best.array.pcb_count_y} PCBs")
    print(f"  Arrays on Panel: {best.array_count_x}x{best.array_count_y}")
    print(f"  Total PCBs per Panel: {best.total_pcb_count}")

    print()
    print("=" * 70)
    print("Optimization complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
