"""
Unit system and conversion utilities for PCB Array Optimizer.

All internal calculations use millimeters (mm). This module provides
conversion to/from imperial units (inches and mils) for display purposes.
"""

from enum import Enum
from dataclasses import dataclass


class UnitSystem(Enum):
    """Supported measurement systems"""
    METRIC = "metric"
    IMPERIAL = "imperial"


class UnitConverter:
    """Handles conversion between metric and imperial units"""

    # Conversion constants (exact by definition)
    MM_PER_INCH = 25.4
    MILS_PER_INCH = 1000

    # Floating point tolerance for comparisons (1 nanometer)
    EPSILON = 1e-9

    @staticmethod
    def mm_to_inches(mm: float) -> float:
        """Convert millimeters to inches

        Args:
            mm: Dimension in millimeters

        Returns:
            Dimension in inches
        """
        return mm / UnitConverter.MM_PER_INCH

    @staticmethod
    def inches_to_mm(inches: float) -> float:
        """Convert inches to millimeters

        Args:
            inches: Dimension in inches

        Returns:
            Dimension in millimeters
        """
        return inches * UnitConverter.MM_PER_INCH

    @staticmethod
    def mm_to_mils(mm: float) -> float:
        """Convert millimeters to mils (thousandths of an inch)

        Args:
            mm: Dimension in millimeters

        Returns:
            Dimension in mils
        """
        return (mm / UnitConverter.MM_PER_INCH) * UnitConverter.MILS_PER_INCH

    @staticmethod
    def mils_to_mm(mils: float) -> float:
        """Convert mils to millimeters

        Args:
            mils: Dimension in mils

        Returns:
            Dimension in millimeters
        """
        return (mils / UnitConverter.MILS_PER_INCH) * UnitConverter.MM_PER_INCH

    @staticmethod
    def format_dimension(mm: float, unit_system: UnitSystem,
                        precision: int = None) -> str:
        """
        Format dimension for display with appropriate precision.

        Args:
            mm: Dimension in millimeters (internal representation)
            unit_system: Target unit system for display
            precision: Decimal places (auto-calculated if None)

        Returns:
            Formatted string with units (e.g., "100.00 mm", "3.937 in")
        """
        if unit_system == UnitSystem.METRIC:
            # Metric: 0.01mm precision (10 microns)
            if precision is None:
                precision = 2
            return f"{mm:.{precision}f} mm"
        else:
            # Imperial: decide between inches and mils
            inches = UnitConverter.mm_to_inches(mm)

            # Use mils for small dimensions (< 0.1 inches)
            if inches < 0.1:
                mils = UnitConverter.mm_to_mils(mm)
                if precision is None:
                    precision = 1
                return f"{mils:.{precision}f} mil"
            else:
                # Use inches with appropriate precision
                # 0.001" precision is standard for PCB work
                if precision is None:
                    precision = 3
                return f"{inches:.{precision}f} in"

    @staticmethod
    def parse_dimension(value_str: str, unit_system: UnitSystem) -> float:
        """
        Parse user input dimension string to millimeters.

        Args:
            value_str: User input (e.g., "100", "3.937")
            unit_system: Current unit system context

        Returns:
            Dimension in millimeters

        Raises:
            ValueError: If input cannot be parsed
        """
        try:
            value = float(value_str.strip())
        except ValueError:
            raise ValueError(f"Invalid dimension: {value_str}")

        if unit_system == UnitSystem.IMPERIAL:
            # Convert from inches to mm
            return UnitConverter.inches_to_mm(value)
        else:
            # Already in mm
            return value

    @staticmethod
    def get_display_value(mm: float, unit_system: UnitSystem) -> float:
        """
        Get numeric value for display (without unit string).
        Used for populating input fields.

        Args:
            mm: Dimension in millimeters
            unit_system: Target unit system

        Returns:
            Numeric value in target unit system, appropriately rounded
        """
        if unit_system == UnitSystem.METRIC:
            return round(mm, 2)
        else:
            inches = UnitConverter.mm_to_inches(mm)
            # Use mils for small values
            if inches < 0.1:
                return round(UnitConverter.mm_to_mils(mm), 1)
            else:
                return round(inches, 3)

    @staticmethod
    def get_unit_label(unit_system: UnitSystem, value_mm: float = None) -> str:
        """
        Get the unit label for display (e.g., "mm", "in", "mil").
        If value_mm provided, automatically choose in/mil for imperial.

        Args:
            unit_system: Current unit system
            value_mm: Optional value to determine in vs mil for imperial

        Returns:
            Unit label string
        """
        if unit_system == UnitSystem.METRIC:
            return "mm"
        else:
            if value_mm is not None:
                inches = UnitConverter.mm_to_inches(value_mm)
                return "mil" if inches < 0.1 else "in"
            else:
                return "in"  # Default to inches

    @staticmethod
    def format_dual_dimension(mm: float, primary_system: UnitSystem) -> str:
        """
        Format dimension with both units for PDF export.

        Args:
            mm: Dimension in millimeters
            primary_system: Primary unit system (shown first)

        Returns:
            Formatted string with both units

        Examples:
            100.00 mm (3.937 in)
            3.937 in (100.00 mm)
        """
        if primary_system == UnitSystem.METRIC:
            primary = f"{mm:.2f} mm"
            secondary = f"{mm/UnitConverter.MM_PER_INCH:.3f} in"
        else:
            inches = mm / UnitConverter.MM_PER_INCH
            primary = f"{inches:.3f} in"
            secondary = f"{mm:.2f} mm"

        return f"{primary} ({secondary})"

    @staticmethod
    def validate_dimension_input(value_str: str, unit_system: UnitSystem) -> tuple[bool, float, str]:
        """
        Validate user input and convert to mm.

        Args:
            value_str: User input string
            unit_system: Current unit system

        Returns:
            Tuple of (is_valid, value_in_mm, error_message)
        """
        try:
            value = float(value_str.strip())
        except ValueError:
            return (False, 0.0, "Invalid number format")

        if value <= 0:
            return (False, 0.0, "Dimension must be positive")

        # Convert to mm
        if unit_system == UnitSystem.IMPERIAL:
            value_mm = value * UnitConverter.MM_PER_INCH
        else:
            value_mm = value

        # Sanity checks
        if value_mm < 0.1:
            return (False, 0.0, "Dimension too small (min 0.1mm / 4 mil)")
        if value_mm > 10000:
            return (False, 0.0, "Dimension too large (max 10000mm / 394in)")

        return (True, value_mm, "")

    @staticmethod
    def dimensions_equal(a_mm: float, b_mm: float, tolerance: float = None) -> bool:
        """
        Compare dimensions with tolerance for floating-point error

        Args:
            a_mm: First dimension in mm
            b_mm: Second dimension in mm
            tolerance: Optional tolerance (defaults to EPSILON)

        Returns:
            True if dimensions are equal within tolerance
        """
        if tolerance is None:
            tolerance = UnitConverter.EPSILON
        return abs(a_mm - b_mm) < tolerance


@dataclass
class UserPreferences:
    """User preferences stored with project configuration"""
    unit_system: UnitSystem = UnitSystem.METRIC

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {"unit_system": self.unit_system.value}

    @classmethod
    def from_dict(cls, data: dict) -> 'UserPreferences':
        """Create from dictionary (JSON deserialization)"""
        return cls(unit_system=UnitSystem(data.get("unit_system", "metric")))
