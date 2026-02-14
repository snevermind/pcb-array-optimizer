"""
Panel size template data model.

All dimensions are stored in millimeters internally.
"""

from dataclasses import dataclass


@dataclass
class PanelSize:
    """Template for standard panel dimensions"""

    name: str
    width: float              # mm
    height: float             # mm
    array_spacing_x: float    # mm between arrays horizontally
    array_spacing_y: float    # mm between arrays vertically
    border_keepout_x: float   # mm keepout from left/right edges
    border_keepout_y: float   # mm keepout from top/bottom edges

    def __post_init__(self):
        """Validate panel size parameters"""
        if self.width <= 0:
            raise ValueError(f"Panel width must be positive, got {self.width}")
        if self.height <= 0:
            raise ValueError(f"Panel height must be positive, got {self.height}")
        if self.array_spacing_x < 0:
            raise ValueError(f"Array spacing X must be non-negative, got {self.array_spacing_x}")
        if self.array_spacing_y < 0:
            raise ValueError(f"Array spacing Y must be non-negative, got {self.array_spacing_y}")
        if self.border_keepout_x < 0:
            raise ValueError(f"Border keepout X must be non-negative, got {self.border_keepout_x}")
        if self.border_keepout_y < 0:
            raise ValueError(f"Border keepout Y must be non-negative, got {self.border_keepout_y}")

        # Ensure keepouts don't exceed panel dimensions
        if 2 * self.border_keepout_x >= self.width:
            raise ValueError(f"Border keepout X ({self.border_keepout_x}mm) too large for panel width ({self.width}mm)")
        if 2 * self.border_keepout_y >= self.height:
            raise ValueError(f"Border keepout Y ({self.border_keepout_y}mm) too large for panel height ({self.height}mm)")

    @property
    def usable_width(self) -> float:
        """Usable width after border keepouts (mm)"""
        return self.width - 2 * self.border_keepout_x

    @property
    def usable_height(self) -> float:
        """Usable height after border keepouts (mm)"""
        return self.height - 2 * self.border_keepout_y

    @property
    def total_area(self) -> float:
        """Total panel area (mm²)"""
        return self.width * self.height

    @property
    def usable_area(self) -> float:
        """Usable area after border keepouts (mm²)"""
        return self.usable_width * self.usable_height

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "array_spacing_x": self.array_spacing_x,
            "array_spacing_y": self.array_spacing_y,
            "border_keepout_x": self.border_keepout_x,
            "border_keepout_y": self.border_keepout_y
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PanelSize':
        """Create from dictionary (JSON deserialization)"""
        return cls(
            name=data["name"],
            width=data["width"],
            height=data["height"],
            array_spacing_x=data["array_spacing_x"],
            array_spacing_y=data["array_spacing_y"],
            border_keepout_x=data["border_keepout_x"],
            border_keepout_y=data["border_keepout_y"]
        )
