"""
Template manager for loading and saving panel size templates.
"""

import json
import os
import sys
from typing import List
from ..models import PanelSize


class TemplateManager:
    """Manages panel size templates"""

    @staticmethod
    def load_default_templates() -> List[PanelSize]:
        """
        Load default panel size templates bundled with the application.

        Returns:
            List of PanelSize objects from default templates

        Raises:
            FileNotFoundError: If default templates file not found
            ValueError: If template file is invalid
        """
        # In PyInstaller bundle, _MEIPASS is the temp extraction root
        # and data files are at src/resources/templates/ under it.
        # In dev mode, __file__ is inside src/io/, so go up to src/.
        if getattr(sys, '_MEIPASS', None):
            base = sys._MEIPASS
            template_path = os.path.join(
                base, 'src', 'resources', 'templates', 'default_panels.json'
            )
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(
                current_dir, '..', 'resources', 'templates', 'default_panels.json'
            )

        return TemplateManager.load_from_file(template_path)

    @staticmethod
    def load_from_file(file_path: str) -> List[PanelSize]:
        """
        Load panel size templates from a JSON file.

        Args:
            file_path: Path to JSON template file

        Returns:
            List of PanelSize objects

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Template file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in template file: {e}")

        if 'panels' not in data:
            raise ValueError("Template file must contain 'panels' array")

        panel_sizes = []
        for panel_data in data['panels']:
            try:
                panel_size = PanelSize.from_dict(panel_data)
                panel_sizes.append(panel_size)
            except (KeyError, ValueError) as e:
                # Skip invalid panels but continue loading others
                print(f"Warning: Skipping invalid panel template: {e}")
                continue

        if not panel_sizes:
            raise ValueError("No valid panel templates found in file")

        return panel_sizes

    @staticmethod
    def save_to_file(panel_sizes: List[PanelSize], file_path: str, template_name: str = "Custom Templates"):
        """
        Save panel size templates to a JSON file.

        Args:
            panel_sizes: List of PanelSize objects to save
            file_path: Path where template file should be saved
            template_name: Name for this template collection
        """
        data = {
            "template_name": template_name,
            "version": "1.0",
            "panels": [ps.to_dict() for ps in panel_sizes]
        }

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def get_panel_by_name(panel_sizes: List[PanelSize], name: str) -> PanelSize:
        """
        Find a panel size by name.

        Args:
            panel_sizes: List of panel sizes to search
            name: Panel name to find

        Returns:
            PanelSize with matching name

        Raises:
            ValueError: If no panel with that name exists
        """
        for panel_size in panel_sizes:
            if panel_size.name == name:
                return panel_size

        raise ValueError(f"No panel size found with name: {name}")
