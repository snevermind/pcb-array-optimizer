"""
Array builder - generates all possible array configurations from a PCB.

This module creates arrays by systematically trying different PCB counts
and rotation states within reasonable bounds.
"""

from typing import List, Iterator
from ..models import PCB, Array, ArraySpacing, ArrayRails


class ArrayBuilder:
    """Builds array configurations from PCB specifications"""

    # Maximum array dimensions to prevent excessive computation
    MAX_ARRAY_DIMENSION = 50

    @staticmethod
    def generate_arrays(
        pcb: PCB,
        spacing: ArraySpacing,
        rails: ArrayRails,
        allow_array_rotation: bool,
        max_width_mm: float = None,
        max_height_mm: float = None
    ) -> Iterator[Array]:
        """
        Generate all possible array configurations for a given PCB.

        Args:
            pcb: PCB specifications
            spacing: Spacing between PCBs in array
            rails: Rail dimensions for array borders
            allow_array_rotation: Whether arrays can be rotated on panel
            max_width_mm: Optional maximum array width to consider
            max_height_mm: Optional maximum array height to consider

        Yields:
            Array configurations in order of increasing size
        """
        # Determine rotation states to try
        rotation_states = [False]
        if pcb.allow_rotation:
            rotation_states.append(True)

        # Generate arrays for each rotation state
        for pcbs_rotated in rotation_states:
            # Determine effective PCB dimensions based on rotation
            pcb_width = pcb.height if pcbs_rotated else pcb.width
            pcb_height = pcb.width if pcbs_rotated else pcb.height

            # Calculate maximum array counts based on constraints
            max_count_x = ArrayBuilder._calculate_max_count(
                pcb_width, spacing.x_spacing, rails.left, rails.right, max_width_mm
            )
            max_count_y = ArrayBuilder._calculate_max_count(
                pcb_height, spacing.y_spacing, rails.top, rails.bottom, max_height_mm
            )

            # Generate arrays from 1x1 up to max dimensions
            for count_x in range(1, max_count_x + 1):
                for count_y in range(1, max_count_y + 1):
                    try:
                        array = Array(
                            pcb=pcb,
                            pcb_count_x=count_x,
                            pcb_count_y=count_y,
                            spacing=spacing,
                            rails=rails,
                            allow_rotation=allow_array_rotation,
                            pcbs_rotated=pcbs_rotated
                        )
                        yield array
                    except ValueError:
                        # Skip invalid configurations
                        continue

    @staticmethod
    def _calculate_max_count(
        pcb_dimension: float,
        spacing: float,
        rail_start: float,
        rail_end: float,
        max_total: float = None
    ) -> int:
        """
        Calculate maximum number of PCBs that can fit in one dimension.

        Args:
            pcb_dimension: PCB size in this dimension (mm)
            spacing: Spacing between PCBs (mm)
            rail_start: Start rail size (mm)
            rail_end: End rail size (mm)
            max_total: Optional maximum total dimension (mm)

        Returns:
            Maximum count (capped at MAX_ARRAY_DIMENSION)
        """
        if max_total is None:
            # No constraint, use maximum
            return ArrayBuilder.MAX_ARRAY_DIMENSION

        # Calculate usable space
        usable = max_total - rail_start - rail_end

        if usable <= 0:
            return 0

        # Calculate how many PCBs fit
        # Formula: n * pcb_dimension + (n-1) * spacing <= usable
        # Solving for n: n <= (usable + spacing) / (pcb_dimension + spacing)
        if pcb_dimension + spacing <= 0:
            return 0

        max_count = int((usable + spacing) / (pcb_dimension + spacing))

        # Cap at maximum to prevent excessive computation
        return min(max_count, ArrayBuilder.MAX_ARRAY_DIMENSION)

    @staticmethod
    def count_possible_arrays(
        pcb: PCB,
        spacing: ArraySpacing,
        rails: ArrayRails,
        allow_array_rotation: bool,
        max_width_mm: float = None,
        max_height_mm: float = None
    ) -> int:
        """
        Count how many array configurations would be generated.
        Useful for estimating computation time.

        Args:
            Same as generate_arrays()

        Returns:
            Number of array configurations that would be generated
        """
        count = 0
        for _ in ArrayBuilder.generate_arrays(
            pcb, spacing, rails, allow_array_rotation, max_width_mm, max_height_mm
        ):
            count += 1
        return count
