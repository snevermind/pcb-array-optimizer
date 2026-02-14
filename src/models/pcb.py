"""
PCB (Printed Circuit Board) data model.

All dimensions are stored in millimeters internally.
"""

from dataclasses import dataclass


@dataclass
class PCB:
    """Represents a single PCB with dimensions and rotation allowance"""

    width: float          # mm (X dimension)
    height: float         # mm (Y dimension)
    allow_rotation: bool  # Can PCB be rotated 90° in array

    def __post_init__(self):
        """Validate PCB dimensions"""
        if self.width <= 0:
            raise ValueError(f"PCB width must be positive, got {self.width}")
        if self.height <= 0:
            raise ValueError(f"PCB height must be positive, got {self.height}")

    @property
    def area(self) -> float:
        """Calculate PCB area in mm²"""
        return self.width * self.height

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "width": self.width,
            "height": self.height,
            "allow_rotation": self.allow_rotation
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PCB':
        """Create from dictionary (JSON deserialization)"""
        return cls(
            width=data["width"],
            height=data["height"],
            allow_rotation=data["allow_rotation"]
        )
