"""
Results panel for displaying optimization results.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QTextEdit, QTabWidget
)
from PyQt6.QtCore import Qt
from typing import List, Optional

from src.models import Configuration, Panel, UnitSystem
from src.models.units import UnitConverter
from src.core import LayoutOptimizer
from src.gui.visualization_canvas import VisualizationPanel, VisualizationDialog
from src.export import PDFExporter


class ResultsPanel(QWidget):
    """Panel for displaying optimization results"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.configuration: Optional[Configuration] = None
        self.results: List[Panel] = []
        self.selected_panel: Optional[Panel] = None

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Optimization Results")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)

        # Splitter for table and details
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Rank",
            "Utilization",
            "Panel Size",
            "Array Config",
            "Arrays on Panel",
            "Total PCBs",
            "PCB Area"
        ])

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.cellDoubleClicked.connect(self._on_row_double_clicked)

        splitter.addWidget(self.table)

        # Tab widget for details and visualization
        self.tab_widget = QTabWidget()

        # Details tab
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(5, 5, 5, 5)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)

        self.tab_widget.addTab(details_widget, "Details")

        # Visualization tab
        self.visualization = VisualizationPanel()
        self.tab_widget.addTab(self.visualization, "Visualization")

        splitter.addWidget(self.tab_widget)

        # Set initial splitter sizes
        splitter.setSizes([400, 300])

        layout.addWidget(splitter)

        # Initial message
        self._show_empty_message()

    def _show_empty_message(self):
        """Show message when no results"""
        self.table.setRowCount(0)
        self.details_text.setPlainText(
            "No results yet.\n\n"
            "Configure your PCB parameters on the left and click 'Optimize' to find "
            "the best panel layouts."
        )

    def run_optimization(self, config: Configuration):
        """Run optimization with given configuration"""
        self.configuration = config
        self.results = []
        self.selected_panel = None

        # Show progress message
        self.table.setRowCount(0)
        self.details_text.setPlainText("Running optimization...\n\nThis may take a moment.")

        # Run optimization
        try:
            self.results = LayoutOptimizer.optimize(config, top_n=10)
            self._display_results()
        except ValueError as e:
            # No valid configurations
            self.details_text.setPlainText(
                f"Optimization Error\n\n{str(e)}\n\n"
                "Try adjusting your PCB dimensions or spacing settings."
            )

    def _display_results(self):
        """Display optimization results in table"""
        if not self.results:
            self._show_empty_message()
            return

        # Get unit system from configuration
        unit_system = UnitSystem.METRIC
        if self.configuration and self.configuration.user_preferences:
            unit_system = self.configuration.user_preferences.unit_system

        # Populate table
        self.table.setRowCount(len(self.results))

        for i, panel in enumerate(self.results):
            # Rank
            rank_item = QTableWidgetItem(f"#{i+1}")
            rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, rank_item)

            # Utilization
            util_item = QTableWidgetItem(f"{panel.utilization_percentage:.2f}%")
            util_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 1, util_item)

            # Panel size
            panel_item = QTableWidgetItem(panel.panel_size.name)
            self.table.setItem(i, 2, panel_item)

            # Array config
            rotation_text = "R" if panel.array.pcbs_rotated else ""
            array_item = QTableWidgetItem(
                f"{panel.array.pcb_count_x}x{panel.array.pcb_count_y}{rotation_text}"
            )
            array_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 3, array_item)

            # Arrays on panel
            arrays_rotation_text = "R" if panel.arrays_rotated else ""
            arrays_item = QTableWidgetItem(
                f"{panel.array_count_x}x{panel.array_count_y}{arrays_rotation_text}"
            )
            arrays_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 4, arrays_item)

            # Total PCBs
            pcb_item = QTableWidgetItem(f"{panel.total_pcb_count}")
            pcb_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 5, pcb_item)

            # PCB Area
            area_text = f"{panel.total_pcb_area:.0f} mm²"
            area_item = QTableWidgetItem(area_text)
            area_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 6, area_item)

        # Select first row by default
        if len(self.results) > 0:
            self.table.selectRow(0)

    def _on_selection_changed(self):
        """Handle row selection change"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows or not self.results:
            return

        row = selected_rows[0].row()
        if 0 <= row < len(self.results):
            self.selected_panel = self.results[row]
            self._display_details()
            self._update_visualization()

    def _display_details(self):
        """Display detailed information about selected panel"""
        if not self.selected_panel or not self.configuration:
            return

        panel = self.selected_panel
        config = self.configuration

        # Get unit system
        unit_system = UnitSystem.METRIC
        if config.user_preferences:
            unit_system = config.user_preferences.unit_system

        # Build details text
        details = []
        details.append("=" * 60)
        details.append(f"Configuration Details - Rank #{self.results.index(panel) + 1}")
        details.append("=" * 60)
        details.append("")

        details.append("UTILIZATION")
        details.append(f"  PCB Area:   {panel.total_pcb_area:.2f} mm²")
        details.append(f"  Panel Area: {panel.panel_area:.2f} mm²")
        details.append(f"  Utilization: {panel.utilization_percentage:.2f}%")
        details.append("")

        details.append("PANEL SIZE")
        details.append(f"  Name: {panel.panel_size.name}")
        details.append(f"  Dimensions: {UnitConverter.format_dimension(panel.panel_size.width, unit_system)} x "
                      f"{UnitConverter.format_dimension(panel.panel_size.height, unit_system)}")
        details.append(f"  Border Keepout: {UnitConverter.format_dimension(panel.panel_size.border_keepout_x, unit_system)} x "
                      f"{UnitConverter.format_dimension(panel.panel_size.border_keepout_y, unit_system)}")
        details.append(f"  Array Spacing: {UnitConverter.format_dimension(panel.panel_size.array_spacing_x, unit_system)} x "
                      f"{UnitConverter.format_dimension(panel.panel_size.array_spacing_y, unit_system)}")
        details.append("")

        details.append("PCB")
        details.append(f"  Dimensions: {UnitConverter.format_dimension(config.pcb.width, unit_system)} x "
                      f"{UnitConverter.format_dimension(config.pcb.height, unit_system)}")
        details.append(f"  Rotation: {'Yes' if config.pcb.allow_rotation else 'No'}")
        details.append("")

        details.append("ARRAY CONFIGURATION")
        details.append(f"  PCBs per Array: {panel.array.pcb_count_x} x {panel.array.pcb_count_y} = {panel.array.pcb_count}")
        details.append(f"  PCBs Rotated: {'Yes' if panel.array.pcbs_rotated else 'No'}")
        details.append(f"  Array Dimensions: {UnitConverter.format_dimension(panel.array.width, unit_system)} x "
                      f"{UnitConverter.format_dimension(panel.array.height, unit_system)}")
        details.append(f"  Array Spacing: {UnitConverter.format_dimension(config.array_spacing.x_spacing, unit_system)} x "
                      f"{UnitConverter.format_dimension(config.array_spacing.y_spacing, unit_system)}")
        details.append(f"  Array Rails: T:{UnitConverter.format_dimension(config.array_rails.top, unit_system)} "
                      f"B:{UnitConverter.format_dimension(config.array_rails.bottom, unit_system)} "
                      f"L:{UnitConverter.format_dimension(config.array_rails.left, unit_system)} "
                      f"R:{UnitConverter.format_dimension(config.array_rails.right, unit_system)}")
        details.append(f"  Max Array Size: {UnitConverter.format_dimension(config.max_array_size.max_width, unit_system)} x "
                      f"{UnitConverter.format_dimension(config.max_array_size.max_height, unit_system)}")
        details.append("")

        details.append("PANEL LAYOUT")
        details.append(f"  Arrays on Panel: {panel.array_count_x} x {panel.array_count_y} = {panel.array_count_x * panel.array_count_y}")
        details.append(f"  Arrays Rotated: {'Yes' if panel.arrays_rotated else 'No'}")
        details.append(f"  Total PCBs per Panel: {panel.total_pcb_count}")
        details.append("")

        details.append("=" * 60)

        self.details_text.setPlainText("\n".join(details))

    def has_results(self) -> bool:
        """Check if results are available"""
        return len(self.results) > 0

    def export_to_pdf(self, file_path: str):
        """Export current results to PDF"""
        if not self.configuration or not self.results:
            raise ValueError("No results to export")

        # Create PDF exporter
        exporter = PDFExporter()

        # Export with selected panel highlighted
        exporter.export_results(
            file_path=file_path,
            configuration=self.configuration,
            results=self.results,
            selected_panel=self.selected_panel
        )

    def _update_visualization(self):
        """Update the visualization with selected panel"""
        if self.selected_panel and self.configuration:
            self.visualization.set_panel(self.selected_panel, self.configuration)
        else:
            self.visualization.clear()

    def _on_row_double_clicked(self, row: int, column: int):
        """Open visualization popup on double-click"""
        if not self.results or not self.configuration:
            return
        if 0 <= row < len(self.results):
            panel = self.results[row]
            dialog = VisualizationDialog(panel, self.configuration, parent=self)
            dialog.exec()

    def clear(self):
        """Clear all results"""
        self.configuration = None
        self.results = []
        self.selected_panel = None
        self._show_empty_message()
        self.visualization.clear()
