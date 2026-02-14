"""
Panel size manager dialog for viewing, adding, editing, and removing panel templates.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox,
    QDialogButtonBox
)
from PyQt6.QtCore import Qt
from typing import List

from src.models import PanelSize, UnitSystem
from src.models.units import UnitConverter
from src.io.template_manager import TemplateManager


class PanelEditDialog(QDialog):
    """Dialog for adding or editing a single panel size"""

    def __init__(self, unit_system: UnitSystem, panel_size: PanelSize = None, parent=None):
        super().__init__(parent)
        self.unit_system = unit_system
        self.result_panel: PanelSize = None

        if panel_size:
            self.setWindowTitle("Edit Panel Size")
        else:
            self.setWindowTitle("Add Panel Size")

        self._init_ui(panel_size)
        self.setMinimumWidth(350)

    def _init_ui(self, panel_size: PanelSize = None):
        layout = QVBoxLayout(self)

        unit_label = "in" if self.unit_system == UnitSystem.IMPERIAL else "mm"

        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Dimensions
        dim_group = QGroupBox("Panel Dimensions")
        dim_layout = QVBoxLayout(dim_group)

        self.width_input = self._add_field(dim_layout, f"Width ({unit_label}):")
        self.height_input = self._add_field(dim_layout, f"Height ({unit_label}):")
        layout.addWidget(dim_group)

        # Border keepout
        border_group = QGroupBox("Border Keepout")
        border_layout = QVBoxLayout(border_group)

        self.border_x_input = self._add_field(border_layout, f"X Border ({unit_label}):")
        self.border_y_input = self._add_field(border_layout, f"Y Border ({unit_label}):")
        layout.addWidget(border_group)

        # Array spacing
        spacing_group = QGroupBox("Array Spacing on Panel")
        spacing_layout = QVBoxLayout(spacing_group)

        self.spacing_x_input = self._add_field(spacing_layout, f"X Spacing ({unit_label}):")
        self.spacing_y_input = self._add_field(spacing_layout, f"Y Spacing ({unit_label}):")
        layout.addWidget(spacing_group)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Populate fields if editing
        if panel_size:
            self.name_input.setText(panel_size.name)
            self._set_display(self.width_input, panel_size.width)
            self._set_display(self.height_input, panel_size.height)
            self._set_display(self.border_x_input, panel_size.border_keepout_x)
            self._set_display(self.border_y_input, panel_size.border_keepout_y)
            self._set_display(self.spacing_x_input, panel_size.array_spacing_x)
            self._set_display(self.spacing_y_input, panel_size.array_spacing_y)

    def _add_field(self, layout: QVBoxLayout, label_text: str) -> QLineEdit:
        row = QHBoxLayout()
        label = QLabel(label_text)
        label.setMinimumWidth(120)
        row.addWidget(label)
        field = QLineEdit()
        field.setMaximumWidth(120)
        row.addWidget(field)
        row.addStretch()
        layout.addLayout(row)
        return field

    def _set_display(self, field: QLineEdit, value_mm: float):
        if self.unit_system == UnitSystem.IMPERIAL:
            field.setText(f"{UnitConverter.mm_to_inches(value_mm):.4f}")
        else:
            field.setText(f"{value_mm:.2f}")

    def _parse_value(self, field: QLineEdit, field_name: str) -> float:
        """Parse a field value and convert to mm"""
        text = field.text().strip()
        if not text:
            raise ValueError(f"{field_name} is required")
        try:
            value = float(text)
        except ValueError:
            raise ValueError(f"{field_name} must be a number")
        if value < 0:
            raise ValueError(f"{field_name} must be non-negative")
        if self.unit_system == UnitSystem.IMPERIAL:
            return UnitConverter.inches_to_mm(value)
        return value

    def _on_accept(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Panel name is required.")
            return

        try:
            width = self._parse_value(self.width_input, "Width")
            height = self._parse_value(self.height_input, "Height")
            border_x = self._parse_value(self.border_x_input, "X Border")
            border_y = self._parse_value(self.border_y_input, "Y Border")
            spacing_x = self._parse_value(self.spacing_x_input, "X Spacing")
            spacing_y = self._parse_value(self.spacing_y_input, "Y Spacing")

            self.result_panel = PanelSize(
                name=name,
                width=width,
                height=height,
                array_spacing_x=spacing_x,
                array_spacing_y=spacing_y,
                border_keepout_x=border_x,
                border_keepout_y=border_y
            )
            self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Validation Error", str(e))


class PanelManagerDialog(QDialog):
    """Dialog for managing panel size templates"""

    def __init__(self, panel_sizes: List[PanelSize], unit_system: UnitSystem, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Panel Sizes")
        self.setMinimumSize(700, 500)

        self.panel_sizes = [ps for ps in panel_sizes]  # Copy the list
        self.unit_system = unit_system

        self._init_ui()
        self._populate_table()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Name", "Width", "Height", "Border X", "Border Y", "Spacing X", "Spacing Y"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in range(1, 7):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()

        add_button = QPushButton("Add...")
        add_button.clicked.connect(self._on_add)
        button_layout.addWidget(add_button)

        edit_button = QPushButton("Edit...")
        edit_button.clicked.connect(self._on_edit)
        button_layout.addWidget(edit_button)

        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(self._on_remove)
        button_layout.addWidget(remove_button)

        button_layout.addStretch()

        defaults_button = QPushButton("Reset to Defaults")
        defaults_button.clicked.connect(self._on_reset_defaults)
        button_layout.addWidget(defaults_button)

        layout.addLayout(button_layout)

        # OK / Cancel
        dialog_buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        dialog_buttons.accepted.connect(self.accept)
        dialog_buttons.rejected.connect(self.reject)
        layout.addWidget(dialog_buttons)

    def _format_dim(self, value_mm: float) -> str:
        return UnitConverter.format_dimension(value_mm, self.unit_system)

    def _populate_table(self):
        self.table.setRowCount(len(self.panel_sizes))

        for i, ps in enumerate(self.panel_sizes):
            self.table.setItem(i, 0, QTableWidgetItem(ps.name))
            self.table.setItem(i, 1, QTableWidgetItem(self._format_dim(ps.width)))
            self.table.setItem(i, 2, QTableWidgetItem(self._format_dim(ps.height)))
            self.table.setItem(i, 3, QTableWidgetItem(self._format_dim(ps.border_keepout_x)))
            self.table.setItem(i, 4, QTableWidgetItem(self._format_dim(ps.border_keepout_y)))
            self.table.setItem(i, 5, QTableWidgetItem(self._format_dim(ps.array_spacing_x)))
            self.table.setItem(i, 6, QTableWidgetItem(self._format_dim(ps.array_spacing_y)))

            for col in range(1, 7):
                self.table.item(i, col).setTextAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )

    def _get_selected_row(self) -> int:
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return -1
        return selected[0].row()

    def _on_add(self):
        dialog = PanelEditDialog(self.unit_system, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.result_panel:
            self.panel_sizes.append(dialog.result_panel)
            self._populate_table()

    def _on_edit(self):
        row = self._get_selected_row()
        if row < 0:
            QMessageBox.information(self, "Edit", "Select a panel size to edit.")
            return

        dialog = PanelEditDialog(self.unit_system, self.panel_sizes[row], parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.result_panel:
            self.panel_sizes[row] = dialog.result_panel
            self._populate_table()

    def _on_remove(self):
        row = self._get_selected_row()
        if row < 0:
            QMessageBox.information(self, "Remove", "Select a panel size to remove.")
            return

        name = self.panel_sizes[row].name
        reply = QMessageBox.question(
            self,
            "Confirm Remove",
            f"Remove panel size \"{name}\"?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            del self.panel_sizes[row]
            self._populate_table()

    def _on_reset_defaults(self):
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "Replace all panel sizes with the default production templates?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.panel_sizes = TemplateManager.load_default_templates()
            self._populate_table()

    def get_panel_sizes(self) -> List[PanelSize]:
        return self.panel_sizes
