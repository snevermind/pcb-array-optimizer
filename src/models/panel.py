"""
Panel data model for production panels containing arrays.

All dimensions are stored in millimeters internally.
"""

from dataclasses import dataclass
from .array import Array
from .panel_size import PanelSize


@dataclass
class Panel:
    """Represents a production panel containing arrays

    Note: Panel validation is performed only for basic parameter checks.
    Use is_valid() to check if arrays actually fit on the panel.
    This allows the optimizer to try configurations without exceptions.
    """

    panel_size: PanelSize
    array: Array
    array_count_x: int
    array_count_y: int
    arrays_rotated: bool  # Are arrays rotated 90° on panel
    validate_fit: bool = True  # If True, raise exception if arrays don't fit

    def __post_init__(self):
        """Validate panel configuration"""
        if self.array_count_x <= 0:
            raise ValueError(f"Array count X must be positive, got {self.array_count_x}")
        if self.array_count_y <= 0:
            raise ValueError(f"Array count Y must be positive, got {self.array_count_y}")
        if self.arrays_rotated and not self.array.allow_rotation:
            raise ValueError("Cannot rotate arrays when rotation is not allowed")

        # Optionally check that arrays fit within usable panel area
        if self.validate_fit and not self.is_valid():
            raise ValueError(f"Arrays don't fit on panel: {self.array_count_x}x{self.array_count_y} arrays of {self.array_width:.2f}x{self.array_height:.2f}mm on {self.panel_size.usable_width:.2f}x{self.panel_size.usable_height:.2f}mm usable area")

    @property
    def array_width(self) -> float:
        """Width of array (potentially rotated) in mm"""
        return self.array.height if self.arrays_rotated else self.array.width

    @property
    def array_height(self) -> float:
        """Height of array (potentially rotated) in mm"""
        return self.array.width if self.arrays_rotated else self.array.height

    def is_valid(self) -> bool:
        """
        Check if this panel configuration is valid (arrays fit within panel).

        This is a public method that can be called during optimization
        to filter out invalid configurations without raising exceptions.

        Returns:
            True if arrays fit within the usable panel area
        """
        # Calculate total width needed for arrays
        total_width = (self.array_count_x * self.array_width +
                      (self.array_count_x - 1) * self.panel_size.array_spacing_x)

        # Calculate total height needed for arrays
        total_height = (self.array_count_y * self.array_height +
                       (self.array_count_y - 1) * self.panel_size.array_spacing_y)

        # Small tolerance for floating point comparisons
        TOLERANCE = 1e-6

        return (total_width <= self.panel_size.usable_width + TOLERANCE and
                total_height <= self.panel_size.usable_height + TOLERANCE)

    def get_fit_error(self) -> str:
        """
        Get a human-readable error message if arrays don't fit.

        Returns:
            Error message string, or empty string if panel is valid
        """
        if self.is_valid():
            return ""

        total_width = (self.array_count_x * self.array_width +
                      (self.array_count_x - 1) * self.panel_size.array_spacing_x)
        total_height = (self.array_count_y * self.array_height +
                       (self.array_count_y - 1) * self.panel_size.array_spacing_y)

        errors = []
        if total_width > self.panel_size.usable_width:
            excess_width = total_width - self.panel_size.usable_width
            errors.append(f"Width exceeds usable area by {excess_width:.2f}mm "
                         f"({total_width:.2f}mm needed, {self.panel_size.usable_width:.2f}mm available)")

        if total_height > self.panel_size.usable_height:
            excess_height = total_height - self.panel_size.usable_height
            errors.append(f"Height exceeds usable area by {excess_height:.2f}mm "
                         f"({total_height:.2f}mm needed, {self.panel_size.usable_height:.2f}mm available)")

        return "; ".join(errors)

    @property
    def total_array_count(self) -> int:
        """Total number of arrays on this panel"""
        return self.array_count_x * self.array_count_y

    @property
    def total_pcb_count(self) -> int:
        """Total number of PCBs on this panel"""
        return self.array.pcb_count * self.total_array_count

    @property
    def total_pcb_area(self) -> float:
        """Total PCB area on this panel (mm²)"""
        return self.array.pcb_area * self.total_array_count

    @property
    def panel_area(self) -> float:
        """Total panel area (mm²)"""
        return self.panel_size.total_area

    @property
    def utilization_ratio(self) -> float:
        """PCB area / Panel area - primary ranking metric"""
        return self.total_pcb_area / self.panel_area

    @property
    def utilization_percentage(self) -> float:
        """Utilization as a percentage"""
        return self.utilization_ratio * 100

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "panel_size": self.panel_size.to_dict(),
            "array": self.array.to_dict(),
            "array_count_x": self.array_count_x,
            "array_count_y": self.array_count_y,
            "arrays_rotated": self.arrays_rotated,
            "validate_fit": self.validate_fit
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Panel':
        """Create from dictionary (JSON deserialization)"""
        return cls(
            panel_size=PanelSize.from_dict(data["panel_size"]),
            array=Array.from_dict(data["array"]),
            array_count_x=data["array_count_x"],
            array_count_y=data["array_count_y"],
            arrays_rotated=data["arrays_rotated"],
            validate_fit=data.get("validate_fit", True)
        )
