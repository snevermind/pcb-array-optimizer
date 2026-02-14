"""
Portable preferences persistence — saves/loads user settings
next to the application executable (or project root in dev mode).
"""

import json
import os
import sys
from typing import List, Optional

from ..models import PanelSize, UnitSystem

PREFS_FILENAME = "preferences.json"


def _get_prefs_path() -> str:
    """Return the path to the preferences file next to the executable."""
    if getattr(sys, '_MEIPASS', None):
        # PyInstaller one-file: executable lives in dist/
        app_dir = os.path.dirname(sys.executable)
    else:
        # Dev mode: use the project root (two levels up from src/io/)
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(app_dir, PREFS_FILENAME)


def load_preferences() -> Optional[dict]:
    """Load saved preferences. Returns None if no file exists or on error."""
    path = _get_prefs_path()
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def save_preferences(unit_system: UnitSystem, panel_sizes: List[PanelSize],
                     selected_panel_name: Optional[str] = None):
    """Save unit system, panel sizes, and selected panel name."""
    data = {
        "unit_system": unit_system.value,
        "panels": [ps.to_dict() for ps in panel_sizes],
        "selected_panel": selected_panel_name,
    }
    try:
        with open(_get_prefs_path(), 'w') as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass  # Silently fail — non-critical


def parse_preferences(data: dict):
    """
    Parse a preferences dict into (UnitSystem, List[PanelSize], selected_name).
    Returns (None, None, None) on invalid data.
    """
    try:
        unit_system = UnitSystem(data["unit_system"])
        panels = [PanelSize.from_dict(p) for p in data["panels"]]
        selected_name = data.get("selected_panel")
        if not panels:
            return None, None, None
        return unit_system, panels, selected_name
    except (KeyError, ValueError, TypeError):
        return None, None, None
