"""
Panel builder - fits arrays into panels and generates valid panel configurations.
"""

from typing import Iterator
from ..models import Array, Panel, PanelSize


class PanelBuilder:
    """Builds panel configurations by fitting arrays into panel sizes"""

    @staticmethod
    def generate_panels(
        array: Array,
        panel_size: PanelSize,
        try_rotation: bool = True
    ) -> Iterator[Panel]:
        """
        Generate all valid panel configurations for a given array and panel size.

        Args:
            array: Array to fit into panels
            panel_size: Panel size specification
            try_rotation: If True and array allows rotation, try both orientations

        Yields:
            Valid Panel configurations (arrays fit within panel)
        """
        # Determine rotation states to try
        rotation_states = [False]
        if try_rotation and array.allow_rotation:
            rotation_states.append(True)

        # Try each rotation state
        for arrays_rotated in rotation_states:
            # Get effective array dimensions based on rotation
            array_width = array.height if arrays_rotated else array.width
            array_height = array.width if arrays_rotated else array.height

            # Calculate maximum array counts that could fit
            max_count_x = PanelBuilder._calculate_max_arrays(
                array_width,
                panel_size.array_spacing_x,
                panel_size.usable_width
            )
            max_count_y = PanelBuilder._calculate_max_arrays(
                array_height,
                panel_size.array_spacing_y,
                panel_size.usable_height
            )

            # Generate all combinations
            for count_x in range(1, max_count_x + 1):
                for count_y in range(1, max_count_y + 1):
                    # Create panel without validation
                    panel = Panel(
                        panel_size=panel_size,
                        array=array,
                        array_count_x=count_x,
                        array_count_y=count_y,
                        arrays_rotated=arrays_rotated,
                        validate_fit=False  # We'll validate explicitly
                    )

                    # Only yield if valid
                    if panel.is_valid():
                        yield panel

    @staticmethod
    def _calculate_max_arrays(
        array_dimension: float,
        spacing: float,
        usable_panel_dimension: float
    ) -> int:
        """
        Calculate maximum number of arrays that can fit in one dimension.

        Args:
            array_dimension: Array size in this dimension (mm)
            spacing: Spacing between arrays (mm)
            usable_panel_dimension: Usable panel size (mm)

        Returns:
            Maximum count of arrays
        """
        if usable_panel_dimension <= 0 or array_dimension <= 0:
            return 0

        # Formula: n * array_dimension + (n-1) * spacing <= usable
        # Solving for n: n <= (usable + spacing) / (array_dimension + spacing)
        if array_dimension + spacing <= 0:
            return 0

        max_count = int((usable_panel_dimension + spacing) / (array_dimension + spacing))

        return max(0, max_count)

    @staticmethod
    def count_possible_panels(
        array: Array,
        panel_size: PanelSize,
        try_rotation: bool = True
    ) -> int:
        """
        Count how many valid panel configurations would be generated.

        Args:
            Same as generate_panels()

        Returns:
            Number of valid panel configurations
        """
        count = 0
        for _ in PanelBuilder.generate_panels(array, panel_size, try_rotation):
            count += 1
        return count

    @staticmethod
    def find_best_fit(
        array: Array,
        panel_size: PanelSize,
        try_rotation: bool = True
    ) -> Panel:
        """
        Find the single best panel configuration (highest utilization).

        Args:
            Same as generate_panels()

        Returns:
            Panel with highest utilization, or None if no valid configuration

        Raises:
            ValueError: If no valid panel configuration exists
        """
        best_panel = None
        best_utilization = 0.0

        for panel in PanelBuilder.generate_panels(array, panel_size, try_rotation):
            if panel.utilization_ratio > best_utilization:
                best_utilization = panel.utilization_ratio
                best_panel = panel

        if best_panel is None:
            raise ValueError(
                f"No valid panel configuration found for array "
                f"{array.width:.2f}x{array.height:.2f}mm on panel "
                f"{panel_size.name} ({panel_size.usable_width:.2f}x{panel_size.usable_height:.2f}mm usable)"
            )

        return best_panel
