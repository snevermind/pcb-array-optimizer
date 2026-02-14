"""
Input panel for configuring PCB array optimization parameters.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QCheckBox, QRadioButton,
    QButtonGroup, QPushButton, QScrollArea, QDialog,
    QComboBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import Optional, List

from src.models import (
    PCB, ArraySpacing, ArrayRails, PanelSize, Configuration,
    UnitSystem, UserPreferences
)
from src.models.units import UnitConverter
from src.io.template_manager import TemplateManager
from src.io.preferences import load_preferences, save_preferences, parse_preferences
from src.gui.panel_manager import PanelManagerDialog


class DimensionInput(QWidget):
    """Widget for entering dimensions with unit awareness"""

    value_changed = pyqtSignal(float)  # Always emits value in mm

    def __init__(self, label: str, default_mm: float = 0.0, parent=None):
        super().__init__(parent)
        self.unit_system = UnitSystem.METRIC
        self._value_mm = default_mm

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label)
        self.label.setMinimumWidth(100)
        layout.addWidget(self.label)

        self.input = QLineEdit()
        self.input.setMaximumWidth(120)
        self.input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.input)

        self.unit_label = QLabel("mm")
        self.unit_label.setMinimumWidth(40)
        layout.addWidget(self.unit_label)

        layout.addStretch()

        self._update_display()

    def _on_text_changed(self, text: str):
        """Handle text changes and convert to mm"""
        try:
            value = float(text)
            if value < 0:
                return

            # Convert to mm based on current unit system
            if self.unit_system == UnitSystem.METRIC:
                self._value_mm = value
            else:
                self._value_mm = UnitConverter.inches_to_mm(value)

            self.value_changed.emit(self._value_mm)
        except ValueError:
            pass  # Ignore invalid input

    def _update_display(self):
        """Update displayed value based on unit system"""
        if self.unit_system == UnitSystem.METRIC:
            self.input.setText(f"{self._value_mm:.2f}")
            self.unit_label.setText("mm")
        else:
            inches = UnitConverter.mm_to_inches(self._value_mm)
            self.input.setText(f"{inches:.4f}")
            self.unit_label.setText("in")

    def set_unit_system(self, unit_system: UnitSystem):
        """Change the unit system"""
        if self.unit_system != unit_system:
            self.unit_system = unit_system
            self._update_display()

    def get_value_mm(self) -> float:
        """Get current value in mm"""
        return self._value_mm

    def set_value_mm(self, value_mm: float):
        """Set value in mm"""
        self._value_mm = value_mm
        self._update_display()


class InputPanel(QWidget):
    """Panel for all optimization input parameters"""

    configuration_changed = pyqtSignal(Configuration)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.unit_system = UnitSystem.METRIC
        self.panel_sizes: List[PanelSize] = TemplateManager.load_default_templates()
        self._selected_panel_name: Optional[str] = None

        # Restore saved preferences (unit system, panel sizes, selected panel)
        saved = load_preferences()
        if saved:
            unit, panels, selected_name = parse_preferences(saved)
            if unit is not None:
                self.unit_system = unit
            if panels is not None:
                self.panel_sizes = panels
            if selected_name is not None:
                self._selected_panel_name = selected_name

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface"""
        # Create scroll area for inputs
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_widget = QWidget()
        scroll.setWidget(scroll_widget)

        layout = QVBoxLayout(scroll_widget)

        # Unit system selection
        unit_group = QGroupBox("Unit System")
        unit_layout = QHBoxLayout(unit_group)

        self.unit_button_group = QButtonGroup()
        self.metric_radio = QRadioButton("Metric (mm)")
        self.imperial_radio = QRadioButton("Imperial (inches)")
        self.metric_radio.setChecked(True)

        self.unit_button_group.addButton(self.metric_radio, 0)
        self.unit_button_group.addButton(self.imperial_radio, 1)
        self.unit_button_group.buttonClicked.connect(self._on_unit_changed)

        unit_layout.addWidget(self.metric_radio)
        unit_layout.addWidget(self.imperial_radio)
        unit_layout.addStretch()

        layout.addWidget(unit_group)

        # PCB Dimensions
        pcb_group = QGroupBox("PCB Dimensions")
        pcb_layout = QVBoxLayout(pcb_group)

        self.pcb_width = DimensionInput("Width:", 100.0)
        self.pcb_height = DimensionInput("Height:", 80.0)
        self.pcb_rotation = QCheckBox("Allow PCB rotation")
        self.pcb_rotation.setChecked(True)

        pcb_layout.addWidget(self.pcb_width)
        pcb_layout.addWidget(self.pcb_height)
        pcb_layout.addWidget(self.pcb_rotation)

        layout.addWidget(pcb_group)

        # Array Spacing
        spacing_group = QGroupBox("Array Spacing")
        spacing_layout = QVBoxLayout(spacing_group)

        self.spacing_x = DimensionInput("X Spacing:", 2.54)
        self.spacing_y = DimensionInput("Y Spacing:", 2.54)

        spacing_layout.addWidget(self.spacing_x)
        spacing_layout.addWidget(self.spacing_y)

        layout.addWidget(spacing_group)

        # Array Rails
        rails_group = QGroupBox("Array Rails (Border)")
        rails_layout = QVBoxLayout(rails_group)

        self.rail_top = DimensionInput("Top:", 5.0)
        self.rail_bottom = DimensionInput("Bottom:", 5.0)
        self.rail_left = DimensionInput("Left:", 5.0)
        self.rail_right = DimensionInput("Right:", 5.0)

        rails_layout.addWidget(self.rail_top)
        rails_layout.addWidget(self.rail_bottom)
        rails_layout.addWidget(self.rail_left)
        rails_layout.addWidget(self.rail_right)

        layout.addWidget(rails_group)

        # Array Rotation
        array_rotation_group = QGroupBox("Array Options")
        array_rotation_layout = QVBoxLayout(array_rotation_group)

        self.array_rotation = QCheckBox("Allow array rotation on panel")
        self.array_rotation.setChecked(True)

        array_rotation_layout.addWidget(self.array_rotation)

        layout.addWidget(array_rotation_group)

        # Panel Size Selection
        panel_group = QGroupBox("Panel Size (Supplier)")
        panel_layout = QVBoxLayout(panel_group)

        self.panel_combo = QComboBox()
        self.panel_combo.currentIndexChanged.connect(self._on_panel_selected)
        panel_layout.addWidget(self.panel_combo)

        self.panel_info_label = QLabel()
        self.panel_info_label.setWordWrap(True)
        self.panel_info_label.setStyleSheet("color: #555; font-size: 9pt;")
        panel_layout.addWidget(self.panel_info_label)

        manage_button = QPushButton("Manage Panel Sizes...")
        manage_button.clicked.connect(self._on_manage_panels)
        panel_layout.addWidget(manage_button)

        layout.addWidget(panel_group)

        layout.addStretch()

        # Set scroll area as main widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Connect all inputs to update configuration
        self.pcb_width.value_changed.connect(self._update_configuration)
        self.pcb_height.value_changed.connect(self._update_configuration)
        self.pcb_rotation.stateChanged.connect(self._update_configuration)
        self.spacing_x.value_changed.connect(self._update_configuration)
        self.spacing_y.value_changed.connect(self._update_configuration)
        self.rail_top.value_changed.connect(self._update_configuration)
        self.rail_bottom.value_changed.connect(self._update_configuration)
        self.rail_left.value_changed.connect(self._update_configuration)
        self.rail_right.value_changed.connect(self._update_configuration)
        self.array_rotation.stateChanged.connect(self._update_configuration)

        # Apply restored unit system to radio buttons and dimension inputs
        if self.unit_system == UnitSystem.IMPERIAL:
            self.imperial_radio.setChecked(True)
            self._on_unit_changed()

        # Populate panel combo and restore selection
        self._populate_panel_combo()
        self._update_configuration()

    def _populate_panel_combo(self):
        """Populate the panel selection combobox"""
        self.panel_combo.blockSignals(True)
        self.panel_combo.clear()

        for ps in self.panel_sizes:
            self.panel_combo.addItem(ps.name)

        # Restore previously selected panel by name
        target = self._selected_panel_name
        if target:
            idx = self.panel_combo.findText(target)
            if idx >= 0:
                self.panel_combo.setCurrentIndex(idx)

        self.panel_combo.blockSignals(False)
        self._update_panel_info()

    def _on_panel_selected(self, index: int):
        """Handle panel selection change"""
        self._update_panel_info()
        self._save_prefs()
        self._update_configuration()

    def _update_panel_info(self):
        """Update the info label below the combobox"""
        ps = self._get_selected_panel()
        if ps:
            w = UnitConverter.format_dimension(ps.width, self.unit_system)
            h = UnitConverter.format_dimension(ps.height, self.unit_system)
            bx = UnitConverter.format_dimension(ps.border_keepout_x, self.unit_system)
            by = UnitConverter.format_dimension(ps.border_keepout_y, self.unit_system)
            self.panel_info_label.setText(f"{w} × {h}  |  Border: {bx} × {by}")
        else:
            self.panel_info_label.setText("No panel sizes configured!")

    def _get_selected_panel(self) -> Optional[PanelSize]:
        """Return the currently selected PanelSize, or None"""
        idx = self.panel_combo.currentIndex()
        if 0 <= idx < len(self.panel_sizes):
            return self.panel_sizes[idx]
        return None

    def _on_unit_changed(self):
        """Handle unit system change"""
        if self.metric_radio.isChecked():
            self.unit_system = UnitSystem.METRIC
        else:
            self.unit_system = UnitSystem.IMPERIAL

        # Update all dimension inputs
        self.pcb_width.set_unit_system(self.unit_system)
        self.pcb_height.set_unit_system(self.unit_system)
        self.spacing_x.set_unit_system(self.unit_system)
        self.spacing_y.set_unit_system(self.unit_system)
        self.rail_top.set_unit_system(self.unit_system)
        self.rail_bottom.set_unit_system(self.unit_system)
        self.rail_left.set_unit_system(self.unit_system)
        self.rail_right.set_unit_system(self.unit_system)

        self._update_panel_info()
        self._save_prefs()
        self._update_configuration()

    def _update_configuration(self):
        """Build configuration from current inputs and emit signal"""
        try:
            # Create PCB
            pcb = PCB(
                width=self.pcb_width.get_value_mm(),
                height=self.pcb_height.get_value_mm(),
                allow_rotation=self.pcb_rotation.isChecked()
            )

            # Create spacing
            spacing = ArraySpacing(
                x_spacing=self.spacing_x.get_value_mm(),
                y_spacing=self.spacing_y.get_value_mm()
            )

            # Create rails
            rails = ArrayRails(
                top=self.rail_top.get_value_mm(),
                bottom=self.rail_bottom.get_value_mm(),
                left=self.rail_left.get_value_mm(),
                right=self.rail_right.get_value_mm()
            )

            # Create user preferences
            preferences = UserPreferences(
                unit_system=self.unit_system
            )

            # Only optimize for the selected panel
            selected = self._get_selected_panel()
            if not selected:
                return

            # Create configuration
            config = Configuration(
                project_name="Untitled Project",
                pcb=pcb,
                array_spacing=spacing,
                array_rails=rails,
                allow_array_rotation=self.array_rotation.isChecked(),
                panel_sizes=[selected],
                user_preferences=preferences
            )

            self.configuration_changed.emit(config)

        except Exception as e:
            # Invalid input - don't emit configuration
            pass

    def _on_manage_panels(self):
        """Open panel manager dialog"""
        dialog = PanelManagerDialog(self.panel_sizes, self.unit_system, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Remember current selection name before repopulating
            self._selected_panel_name = self.panel_combo.currentText()
            self.panel_sizes = dialog.get_panel_sizes()
            self._populate_panel_combo()
            self._save_prefs()
            self._update_configuration()

    def _save_prefs(self):
        """Persist unit system, panel list, and selected panel name"""
        selected_name = self.panel_combo.currentText() if self.panel_combo.currentIndex() >= 0 else None
        save_preferences(self.unit_system, self.panel_sizes, selected_name)

    def reset(self):
        """Reset all inputs to defaults"""
        self.metric_radio.setChecked(True)
        self.unit_system = UnitSystem.METRIC

        self.pcb_width.set_value_mm(100.0)
        self.pcb_height.set_value_mm(80.0)
        self.pcb_rotation.setChecked(True)

        self.spacing_x.set_value_mm(2.54)
        self.spacing_y.set_value_mm(2.54)

        self.rail_top.set_value_mm(5.0)
        self.rail_bottom.set_value_mm(5.0)
        self.rail_left.set_value_mm(5.0)
        self.rail_right.set_value_mm(5.0)

        self.array_rotation.setChecked(True)

        self.panel_sizes = TemplateManager.load_default_templates()
        self._selected_panel_name = None
        self._populate_panel_combo()
        self._update_configuration()

    def load_configuration(self, config: Configuration):
        """Load configuration into inputs"""
        # Set unit system
        if config.user_preferences:
            self.unit_system = config.user_preferences.unit_system
            if self.unit_system == UnitSystem.METRIC:
                self.metric_radio.setChecked(True)
            else:
                self.imperial_radio.setChecked(True)

        # Set PCB values
        self.pcb_width.set_value_mm(config.pcb.width)
        self.pcb_height.set_value_mm(config.pcb.height)
        self.pcb_rotation.setChecked(config.pcb.allow_rotation)

        # Set spacing
        self.spacing_x.set_value_mm(config.array_spacing.x_spacing)
        self.spacing_y.set_value_mm(config.array_spacing.y_spacing)

        # Set rails
        self.rail_top.set_value_mm(config.array_rails.top)
        self.rail_bottom.set_value_mm(config.array_rails.bottom)
        self.rail_left.set_value_mm(config.array_rails.left)
        self.rail_right.set_value_mm(config.array_rails.right)

        # Set array rotation
        self.array_rotation.setChecked(config.allow_array_rotation)

        # Set panel sizes — loaded config may have a subset
        if config.panel_sizes:
            # If one panel was saved, select it by name
            self._selected_panel_name = config.panel_sizes[0].name
        self._populate_panel_combo()

        # Update unit displays
        self._on_unit_changed()
