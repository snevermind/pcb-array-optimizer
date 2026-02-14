"""
Main window for PCB Array Optimizer application.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QPushButton, QMenuBar, QMenu, QFileDialog,
    QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from typing import Optional
import json
import os
import sys

from src.models import Configuration, UnitSystem
from src.io.template_manager import TemplateManager
from src.gui.input_panel import InputPanel
from src.gui.results_panel import ResultsPanel


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.configuration: Optional[Configuration] = None
        self.current_file: Optional[str] = None

        self._init_ui()
        self._create_menu_bar()

    @staticmethod
    def _find_icon() -> Optional[str]:
        """Locate the application icon, works for both dev and PyInstaller builds"""
        # PyInstaller sets _MEIPASS for bundled apps
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        candidates = [
            os.path.join(base_path, 'src', 'resources', 'icons', 'app_icon.png'),
            os.path.join(base_path, 'icon.png'),
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return None

    def _init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("PCB Array Optimizer")
        self.setGeometry(100, 100, 1200, 800)

        # Set application icon
        icon_path = self._find_icon()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create splitter for input and results
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Input panel
        self.input_panel = InputPanel()
        self.input_panel.configuration_changed.connect(self._on_configuration_changed)
        splitter.addWidget(self.input_panel)

        # Right panel: Results
        self.results_panel = ResultsPanel()
        splitter.addWidget(self.results_panel)

        # Set initial splitter sizes (40% input, 60% results)
        splitter.setSizes([480, 720])

        main_layout.addWidget(splitter)

        # Bottom: Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.optimize_button = QPushButton("Optimize")
        self.optimize_button.setEnabled(False)
        self.optimize_button.clicked.connect(self._on_optimize_clicked)
        button_layout.addWidget(self.optimize_button)

        self.export_button = QPushButton("Export to PDF")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self._on_export_clicked)
        button_layout.addWidget(self.export_button)

        main_layout.addLayout(button_layout)

    def _create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = file_menu.addAction("&New")
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._on_new)

        open_action = file_menu.addAction("&Open...")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_open)

        save_action = file_menu.addAction("&Save")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._on_save)

        save_as_action = file_menu.addAction("Save &As...")
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self._on_save_as)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("E&xit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        panels_action = tools_menu.addAction("Manage &Panel Sizes...")
        panels_action.triggered.connect(self._on_manage_panels)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(self._on_about)

    def _on_configuration_changed(self, config: Configuration):
        """Handle configuration changes from input panel"""
        self.configuration = config
        self.optimize_button.setEnabled(config is not None)

    def _on_optimize_clicked(self):
        """Run optimization"""
        if not self.configuration:
            return

        try:
            self.results_panel.run_optimization(self.configuration)
            self.export_button.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Optimization Error",
                f"An error occurred during optimization:\n\n{str(e)}"
            )

    def _on_export_clicked(self):
        """Export current results to PDF"""
        if not self.results_panel.has_results():
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export to PDF",
            "",
            "PDF Files (*.pdf)"
        )

        if file_path:
            try:
                self.results_panel.export_to_pdf(file_path)
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Results exported to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"An error occurred during export:\n\n{str(e)}"
                )

    def _on_new(self):
        """Create a new configuration"""
        # TODO: Check for unsaved changes
        self.input_panel.reset()
        self.results_panel.clear()
        self.configuration = None
        self.current_file = None
        self.optimize_button.setEnabled(False)
        self.export_button.setEnabled(False)

    def _on_open(self):
        """Open a configuration file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Configuration",
            "",
            "JSON Files (*.json)"
        )

        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    config = Configuration.from_dict(data)
                    self.input_panel.load_configuration(config)
                    self.current_file = file_path
                    self.setWindowTitle(f"PCB Array Optimizer - {file_path}")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Open Error",
                    f"Failed to open configuration:\n\n{str(e)}"
                )

    def _on_save(self):
        """Save current configuration"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self._on_save_as()

    def _on_save_as(self):
        """Save configuration to a new file"""
        if not self.configuration:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Configuration",
            "",
            "JSON Files (*.json)"
        )

        if file_path:
            self._save_to_file(file_path)

    def _save_to_file(self, file_path: str):
        """Save configuration to file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.configuration.to_dict(), f, indent=2)
            self.current_file = file_path
            self.setWindowTitle(f"PCB Array Optimizer - {file_path}")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save configuration:\n\n{str(e)}"
            )

    def _on_manage_panels(self):
        """Open panel size manager dialog"""
        self.input_panel._on_manage_panels()

    def _on_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About PCB Array Optimizer",
            "<h3>PCB Array Optimizer</h3>"
            "<p>Version 1.0</p>"
            "<p>An open source tool for optimizing PCB panel layouts.</p>"
            "<p>Calculates optimal arrangements of PCB arrays on production panels "
            "to maximize material utilization.</p>"
        )
