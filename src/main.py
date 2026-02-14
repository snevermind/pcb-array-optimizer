#!/usr/bin/env python3
"""
PCB Array Optimizer - Main Application Entry Point
"""

import sys
from PyQt6.QtWidgets import QApplication
from src.gui import MainWindow


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("PCB Array Optimizer")
    app.setOrganizationName("PCB Array Optimizer")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
