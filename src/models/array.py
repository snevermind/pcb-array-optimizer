"""
Array data models for organizing PCBs into arrays.

All dimensions are stored in millimeters internally.
"""

from dataclasses import dataclass
from .pcb import PCB


@dataclass
class ArraySpacing:
    """Spacing parameters for PCBs within an array"""

    x_spacing: float  # mm between PCBs horizontally
    y_spacing: float  # mm between PCBs vertically

    def __post_init__(self):
        """Validate spacing"""
        if self.x_spacing < 0:
            raise ValueError(f"X spacing must be non-negative, got {self.x_spacing}")
        if self.y_spacing < 0:
            raise ValueError(f"Y spacing must be non-negative, got {self.y_spacing}")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "x_spacing": self.x_spacing,
            "y_spacing": self.y_spacing
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ArraySpacing':
        """Create from dictionary (JSON deserialization)"""
        return cls(
            x_spacing=data["x_spacing"],
            y_spacing=data["y_spacing"]
        )


@dataclass
class ArrayRails:
    """Outer rail dimensions for an array"""

    top: float     # mm
    bottom: float  # mm
    left: float    # mm
    right: float   # mm

    def __post_init__(self):
        """Validate rails"""
        if self.top < 0:
            raise ValueError(f"Top rail must be non-negative, got {self.top}")
        if self.bottom < 0:
            raise ValueError(f"Bottom rail must be non-negative, got {self.bottom}")
        if self.left < 0:
            raise ValueError(f"Left rail must be non-negative, got {self.left}")
        if self.right < 0:
            raise ValueError(f"Right rail must be non-negative, got {self.right}")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "top": self.top,
            "bottom": self.bottom,
            "left": self.left,
            "right": self.right
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ArrayRails':
        """Create from dictionary (JSON deserialization)"""
        return cls(
            top=data["top"],
            bottom=data["bottom"],
            left=data["left"],
            right=data["right"]
        )


@dataclass
class Array:
    """Represents an array of PCBs with spacing and rails"""

    pcb: PCB
    pcb_count_x: int
    pcb_count_y: int
    spacing: ArraySpacing
    rails: ArrayRails
    allow_rotation: bool  # Can array be rotated 90° on panel
    pcbs_rotated: bool    # Are PCBs rotated 90° in this array

    def __post_init__(self):
        """Validate array parameters"""
        if self.pcb_count_x <= 0:
            raise ValueError(f"PCB count X must be positive, got {self.pcb_count_x}")
        if self.pcb_count_y <= 0:
            raise ValueError(f"PCB count Y must be positive, got {self.pcb_count_y}")
        if self.pcbs_rotated and not self.pcb.allow_rotation:
            raise ValueError("Cannot rotate PCBs when rotation is not allowed")

    @property
    def width(self) -> float:
        """Calculate total array width in mm"""
        pcb_width = self.pcb.height if self.pcbs_rotated else self.pcb.width
        return (self.rails.left + self.rails.right +
                self.pcb_count_x * pcb_width +
                (self.pcb_count_x - 1) * self.spacing.x_spacing)

    @property
    def height(self) -> float:
        """Calculate total array height in mm"""
        pcb_height = self.pcb.width if self.pcbs_rotated else self.pcb.height
        return (self.rails.top + self.rails.bottom +
                self.pcb_count_y * pcb_height +
                (self.pcb_count_y - 1) * self.spacing.y_spacing)

    @property
    def pcb_count(self) -> int:
        """Total number of PCBs in this array"""
        return self.pcb_count_x * self.pcb_count_y

    @property
    def pcb_area(self) -> float:
        """Total PCB area in this array (mm²)"""
        return self.pcb.area * self.pcb_count

    @property
    def total_area(self) -> float:
        """Total array area including rails (mm²)"""
        return self.width * self.height

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "pcb": self.pcb.to_dict(),
            "pcb_count_x": self.pcb_count_x,
            "pcb_count_y": self.pcb_count_y,
            "spacing": self.spacing.to_dict(),
            "rails": self.rails.to_dict(),
            "allow_rotation": self.allow_rotation,
            "pcbs_rotated": self.pcbs_rotated
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Array':
        """Create from dictionary (JSON deserialization)"""
        return cls(
            pcb=PCB.from_dict(data["pcb"]),
            pcb_count_x=data["pcb_count_x"],
            pcb_count_y=data["pcb_count_y"],
            spacing=ArraySpacing.from_dict(data["spacing"]),
            rails=ArrayRails.from_dict(data["rails"]),
            allow_rotation=data["allow_rotation"],
            pcbs_rotated=data["pcbs_rotated"]
        )
