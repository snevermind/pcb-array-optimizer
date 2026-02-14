"""
Project configuration data model.

All dimensions are stored in millimeters internally.
"""

from dataclasses import dataclass, field
from typing import List
from datetime import datetime
from .pcb import PCB
from .array import ArraySpacing, ArrayRails
from .panel_size import PanelSize
from .units import UserPreferences


@dataclass
class Configuration:
    """Complete project configuration"""

    pcb: PCB
    array_spacing: ArraySpacing
    array_rails: ArrayRails
    allow_array_rotation: bool
    panel_sizes: List[PanelSize]
    user_preferences: UserPreferences = field(default_factory=UserPreferences)
    project_name: str = "Untitled"
    created: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    modified: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def __post_init__(self):
        """Validate configuration"""
        if not self.panel_sizes:
            raise ValueError("At least one panel size must be configured")

    def update_modified_timestamp(self):
        """Update the modified timestamp to current time"""
        self.modified = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "project_name": self.project_name,
            "created": self.created,
            "modified": self.modified,
            "user_preferences": self.user_preferences.to_dict(),
            "pcb": self.pcb.to_dict(),
            "array_spacing": self.array_spacing.to_dict(),
            "array_rails": self.array_rails.to_dict(),
            "allow_array_rotation": self.allow_array_rotation,
            "panel_sizes": [ps.to_dict() for ps in self.panel_sizes]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Configuration':
        """Create from dictionary (JSON deserialization)"""
        return cls(
            project_name=data.get("project_name", "Untitled"),
            created=data.get("created", datetime.utcnow().isoformat() + "Z"),
            modified=data.get("modified", datetime.utcnow().isoformat() + "Z"),
            user_preferences=UserPreferences.from_dict(data.get("user_preferences", {})),
            pcb=PCB.from_dict(data["pcb"]),
            array_spacing=ArraySpacing.from_dict(data["array_spacing"]),
            array_rails=ArrayRails.from_dict(data["array_rails"]),
            allow_array_rotation=data["allow_array_rotation"],
            panel_sizes=[PanelSize.from_dict(ps) for ps in data["panel_sizes"]]
        )
