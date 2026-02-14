"""
Layout optimizer - finds the best PCB array configurations for given panel sizes.

Uses brute force search to exhaustively explore the solution space and
return the top configurations by utilization ratio.
"""

from typing import List
from ..models import Configuration, Panel
from .array_builder import ArrayBuilder
from .panel_builder import PanelBuilder


class LayoutOptimizer:
    """Optimizes PCB layout by finding best array and panel configurations"""

    # Minimum utilization threshold (skip configurations below this)
    MIN_UTILIZATION = 0.10  # 10%

    @staticmethod
    def optimize(
        config: Configuration,
        top_n: int = 10,
        min_utilization: float = None
    ) -> List[Panel]:
        """
        Find the best panel configurations for the given project configuration.

        This is the main entry point for optimization. It uses a brute force
        approach to explore all valid combinations and returns the top results.

        Args:
            config: Project configuration with PCB specs and panel sizes
            top_n: Number of top results to return (default 10)
            min_utilization: Minimum utilization ratio to consider (default 0.10)

        Returns:
            List of Panel configurations, sorted by utilization ratio (descending)
            Length will be at most top_n, but may be less if fewer valid configs exist

        Algorithm:
            1. For each panel size:
                2. Generate all possible array configurations
                3. For each array:
                    4. Generate all valid panel configurations
                    5. Filter by minimum utilization
                    6. Add to results
            7. Sort by utilization descending
            8. Return top N
        """
        if min_utilization is None:
            min_utilization = LayoutOptimizer.MIN_UTILIZATION

        results = []

        # Process each panel size
        for panel_size in config.panel_sizes:
            # Generate arrays that could potentially fit
            # Use panel usable dimensions as constraints to reduce search space
            arrays = ArrayBuilder.generate_arrays(
                pcb=config.pcb,
                spacing=config.array_spacing,
                rails=config.array_rails,
                allow_array_rotation=config.allow_array_rotation,
                max_width_mm=panel_size.usable_width,
                max_height_mm=panel_size.usable_height
            )

            # For each array, try fitting into panels
            for array in arrays:
                panels = PanelBuilder.generate_panels(
                    array=array,
                    panel_size=panel_size,
                    try_rotation=config.allow_array_rotation
                )

                # Filter and collect valid panels
                for panel in panels:
                    if panel.utilization_ratio >= min_utilization:
                        results.append(panel)

        # Sort by utilization ratio (descending) and take top N
        results.sort(key=lambda p: p.utilization_ratio, reverse=True)
        return results[:top_n]

    @staticmethod
    def estimate_search_space(config: Configuration) -> dict:
        """
        Estimate the size of the search space for a given configuration.
        Useful for understanding computation requirements.

        Args:
            config: Project configuration

        Returns:
            Dictionary with search space statistics:
            - total_combinations: Total array+panel combinations to explore
            - arrays_per_panel: List of array counts per panel size
            - panel_count: Number of panel sizes
        """
        stats = {
            'total_combinations': 0,
            'arrays_per_panel': [],
            'panel_count': len(config.panel_sizes)
        }

        for panel_size in config.panel_sizes:
            # Count arrays for this panel size
            array_count = ArrayBuilder.count_possible_arrays(
                pcb=config.pcb,
                spacing=config.array_spacing,
                rails=config.array_rails,
                allow_array_rotation=config.allow_array_rotation,
                max_width_mm=panel_size.usable_width,
                max_height_mm=panel_size.usable_height
            )

            stats['arrays_per_panel'].append({
                'panel_name': panel_size.name,
                'array_count': array_count
            })

            # Estimate panel configurations per array (rough estimate: ~10-20 on average)
            # Actual count varies widely, but this gives order of magnitude
            estimated_panels_per_array = 15
            stats['total_combinations'] += array_count * estimated_panels_per_array

        return stats

    @staticmethod
    def find_single_best(config: Configuration) -> Panel:
        """
        Find the single best configuration (highest utilization).

        Args:
            config: Project configuration

        Returns:
            Panel with highest utilization

        Raises:
            ValueError: If no valid configuration exists
        """
        results = LayoutOptimizer.optimize(config, top_n=1, min_utilization=0.0)

        if not results:
            raise ValueError(
                "No valid panel configuration found. PCB may be too large for "
                f"available panel sizes. PCB: {config.pcb.width}x{config.pcb.height}mm, "
                f"Panels: {', '.join(ps.name for ps in config.panel_sizes)}"
            )

        return results[0]
