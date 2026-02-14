"""
Visualization canvas for displaying PCB panel layouts.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QBrush
from PyQt6.QtCore import Qt, QRectF, QPointF
from typing import Optional

from src.models import Panel, Configuration, UnitSystem
from src.models.units import UnitConverter


class PanelCanvas(QWidget):
    """Canvas widget for drawing PCB panel layouts"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.panel: Optional[Panel] = None
        self.configuration: Optional[Configuration] = None
        self.unit_system = UnitSystem.METRIC
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0

        # Colors
        self.color_panel = QColor(240, 240, 240)
        self.color_border = QColor(200, 200, 200)
        self.color_array = QColor(150, 180, 220)
        self.color_pcb = QColor(100, 150, 100)
        self.color_text = QColor(0, 0, 0)
        self.color_dimension = QColor(0, 0, 200)

        self.setMinimumSize(400, 400)

    def set_panel(self, panel: Panel, configuration: Configuration):
        """Set the panel to display"""
        self.panel = panel
        self.configuration = configuration

        if configuration.user_preferences:
            self.unit_system = configuration.user_preferences.unit_system

        # Calculate scale to fit panel in view
        self._calculate_scale()
        self.update()

    def _calculate_scale(self):
        """Calculate scale factor to fit panel in widget"""
        if not self.panel:
            return

        # Get widget dimensions (with margins)
        margin = 60  # Space for dimensions and labels
        widget_width = self.width() - 2 * margin
        widget_height = self.height() - 2 * margin

        if widget_width <= 0 or widget_height <= 0:
            return

        # Panel dimensions in mm
        panel_width = self.panel.panel_size.width
        panel_height = self.panel.panel_size.height

        # Calculate scale to fit
        scale_x = widget_width / panel_width
        scale_y = widget_height / panel_height
        self.scale = min(scale_x, scale_y) * 0.9  # 90% to leave some space

        # Center the panel
        scaled_panel_width = panel_width * self.scale
        scaled_panel_height = panel_height * self.scale

        self.offset_x = (self.width() - scaled_panel_width) / 2
        self.offset_y = (self.height() - scaled_panel_height) / 2

    def paintEvent(self, event):
        """Paint the panel visualization"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self.panel or not self.configuration:
            self._draw_empty_message(painter)
            return

        self._draw_panel(painter)

    def _draw_empty_message(self, painter: QPainter):
        """Draw message when no panel is selected"""
        painter.setPen(QColor(150, 150, 150))
        font = QFont("Arial", 12)
        painter.setFont(font)
        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignCenter,
            "Select an optimization result to view panel layout"
        )

    def _draw_panel(self, painter: QPainter):
        """Draw the complete panel with arrays and PCBs"""
        panel = self.panel

        # Draw panel outline
        panel_rect = QRectF(
            self.offset_x,
            self.offset_y,
            panel.panel_size.width * self.scale,
            panel.panel_size.height * self.scale
        )

        painter.fillRect(panel_rect, self.color_panel)
        painter.setPen(QPen(self.color_border, 2))
        painter.drawRect(panel_rect)

        # Draw usable area
        usable_rect = QRectF(
            self.offset_x + panel.panel_size.border_keepout_x * self.scale,
            self.offset_y + panel.panel_size.border_keepout_y * self.scale,
            panel.panel_size.usable_width * self.scale,
            panel.panel_size.usable_height * self.scale
        )

        painter.setPen(QPen(self.color_border, 1, Qt.PenStyle.DashLine))
        painter.drawRect(usable_rect)

        # Draw arrays
        self._draw_arrays(painter)

        # Draw dimensions
        self._draw_dimensions(painter)

        # Draw labels
        self._draw_labels(painter)

    def _draw_arrays(self, painter: QPainter):
        """Draw all arrays on the panel"""
        panel = self.panel

        # Get array dimensions based on rotation
        if panel.arrays_rotated:
            array_width = panel.array.height
            array_height = panel.array.width
        else:
            array_width = panel.array.width
            array_height = panel.array.height

        # Starting position (top-left of usable area)
        start_x = self.offset_x + panel.panel_size.border_keepout_x * self.scale
        start_y = self.offset_y + panel.panel_size.border_keepout_y * self.scale

        # Draw each array
        for ay in range(panel.array_count_y):
            for ax in range(panel.array_count_x):
                # Calculate array position
                array_x = start_x + ax * (array_width + panel.panel_size.array_spacing_x) * self.scale
                array_y = start_y + ay * (array_height + panel.panel_size.array_spacing_y) * self.scale

                # Draw array background
                array_rect = QRectF(
                    array_x,
                    array_y,
                    array_width * self.scale,
                    array_height * self.scale
                )

                painter.fillRect(array_rect, self.color_array)
                painter.setPen(QPen(QColor(100, 120, 180), 2))
                painter.drawRect(array_rect)

                # Draw PCBs within array
                self._draw_pcbs_in_array(painter, array_x, array_y)

    def _draw_pcbs_in_array(self, painter: QPainter, array_x: float, array_y: float):
        """Draw individual PCBs within an array"""
        panel = self.panel
        array = panel.array
        config = self.configuration

        # Get PCB dimensions based on rotation
        if array.pcbs_rotated:
            pcb_width = config.pcb.height
            pcb_height = config.pcb.width
        else:
            pcb_width = config.pcb.width
            pcb_height = config.pcb.height

        # Starting position (accounting for rails)
        start_x = array_x + config.array_rails.left * self.scale
        start_y = array_y + config.array_rails.top * self.scale

        # Draw each PCB
        for py in range(array.pcb_count_y):
            for px in range(array.pcb_count_x):
                # Calculate PCB position
                pcb_x = start_x + px * (pcb_width + config.array_spacing.x_spacing) * self.scale
                pcb_y = start_y + py * (pcb_height + config.array_spacing.y_spacing) * self.scale

                # Draw PCB
                pcb_rect = QRectF(
                    pcb_x,
                    pcb_y,
                    pcb_width * self.scale,
                    pcb_height * self.scale
                )

                painter.fillRect(pcb_rect, self.color_pcb)
                painter.setPen(QPen(QColor(60, 100, 60), 1))
                painter.drawRect(pcb_rect)

    def _draw_dimensions(self, painter: QPainter):
        """Draw dimension annotations"""
        panel = self.panel

        painter.setPen(QPen(self.color_dimension, 1))
        font = QFont("Arial", 8)
        painter.setFont(font)

        # Panel width dimension (top)
        panel_width_text = UnitConverter.format_dimension(
            panel.panel_size.width,
            self.unit_system
        )

        dim_y = self.offset_y - 20
        painter.drawLine(
            int(self.offset_x),
            int(dim_y),
            int(self.offset_x + panel.panel_size.width * self.scale),
            int(dim_y)
        )

        painter.drawText(
            QRectF(
                self.offset_x,
                dim_y - 15,
                panel.panel_size.width * self.scale,
                15
            ),
            Qt.AlignmentFlag.AlignCenter,
            panel_width_text
        )

        # Panel height dimension (left)
        panel_height_text = UnitConverter.format_dimension(
            panel.panel_size.height,
            self.unit_system
        )

        dim_x = self.offset_x - 20
        painter.drawLine(
            int(dim_x),
            int(self.offset_y),
            int(dim_x),
            int(self.offset_y + panel.panel_size.height * self.scale)
        )

        # Rotate text for vertical dimension
        painter.save()
        painter.translate(dim_x - 15, self.offset_y + panel.panel_size.height * self.scale / 2)
        painter.rotate(-90)
        painter.drawText(0, 0, panel_height_text)
        painter.restore()

    def _draw_labels(self, painter: QPainter):
        """Draw informational labels"""
        panel = self.panel

        painter.setPen(self.color_text)
        font = QFont("Arial", 9, QFont.Weight.Bold)
        painter.setFont(font)

        # Panel info at top
        info_text = f"{panel.panel_size.name}"
        painter.drawText(
            QRectF(self.offset_x, self.offset_y + panel.panel_size.height * self.scale + 10,
                   panel.panel_size.width * self.scale, 20),
            Qt.AlignmentFlag.AlignCenter,
            info_text
        )

        # Utilization info
        util_text = f"{panel.utilization_percentage:.1f}% utilization - {panel.total_pcb_count} PCBs"
        font.setBold(False)
        painter.setFont(font)
        painter.drawText(
            QRectF(self.offset_x, self.offset_y + panel.panel_size.height * self.scale + 25,
                   panel.panel_size.width * self.scale, 20),
            Qt.AlignmentFlag.AlignCenter,
            util_text
        )

    def resizeEvent(self, event):
        """Handle widget resize"""
        if self.panel:
            self._calculate_scale()
        super().resizeEvent(event)


class VisualizationPanel(QWidget):
    """Panel containing the canvas and controls"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Panel Layout Visualization")
        title.setStyleSheet("font-size: 12pt; font-weight: bold;")
        layout.addWidget(title)

        # Canvas
        self.canvas = PanelCanvas()
        layout.addWidget(self.canvas, 1)  # Stretch to fill

        # Controls
        controls_layout = QHBoxLayout()

        # Legend
        legend = QLabel(
            "<b>Legend:</b> "
            '<span style="color: #649664;">■</span> PCB  '
            '<span style="color: #96B4DC;">■</span> Array  '
            '<span style="color: #C8C8C8;">□</span> Panel Border'
        )
        controls_layout.addWidget(legend)

        controls_layout.addStretch()

        layout.addLayout(controls_layout)

    def set_panel(self, panel: Panel, configuration: Configuration):
        """Set the panel to visualize"""
        self.canvas.set_panel(panel, configuration)

    def clear(self):
        """Clear the visualization"""
        self.canvas.panel = None
        self.canvas.configuration = None
        self.canvas.update()


class ArrayCanvas(QWidget):
    """Canvas widget for drawing a single array with PCBs inside."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.panel: Optional[Panel] = None
        self.configuration: Optional[Configuration] = None
        self.unit_system = UnitSystem.METRIC
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0

        self.color_rail = QColor(180, 180, 180)
        self.color_pcb = QColor(100, 150, 100)
        self.color_pcb_border = QColor(60, 100, 60)
        self.color_spacing = QColor(220, 220, 220)

        self.setMinimumSize(400, 400)

    def set_data(self, panel: Panel, configuration: Configuration):
        self.panel = panel
        self.configuration = configuration
        if configuration.user_preferences:
            self.unit_system = configuration.user_preferences.unit_system
        self._calculate_scale()
        self.update()

    def _calculate_scale(self):
        if not self.panel:
            return
        margin = 70
        avail_w = self.width() - 2 * margin
        avail_h = self.height() - 2 * margin
        if avail_w <= 0 or avail_h <= 0:
            return

        array = self.panel.array
        scale_x = avail_w / array.width
        scale_y = avail_h / array.height
        self.scale = min(scale_x, scale_y) * 0.9

        self.offset_x = (self.width() - array.width * self.scale) / 2
        self.offset_y = (self.height() - array.height * self.scale) / 2

    def resizeEvent(self, event):
        if self.panel:
            self._calculate_scale()
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self.panel or not self.configuration:
            painter.setPen(self.palette().color(self.foregroundRole()))
            painter.setFont(QFont("Arial", 12))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "Select an optimization result to view")
            return

        array = self.panel.array
        config = self.configuration
        s = self.scale
        ox, oy = self.offset_x, self.offset_y

        # Draw array outline (rails area)
        array_rect = QRectF(ox, oy, array.width * s, array.height * s)
        painter.fillRect(array_rect, self.color_rail)
        painter.setPen(QPen(QColor(120, 120, 120), 2))
        painter.drawRect(array_rect)

        # Rail labels
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.setFont(QFont("Arial", 8))
        rails = config.array_rails

        # Top rail
        if rails.top > 0:
            top_h = rails.top * s
            painter.drawText(QRectF(ox, oy, array.width * s, top_h),
                             Qt.AlignmentFlag.AlignCenter,
                             UnitConverter.format_dimension(rails.top, self.unit_system))
        # Bottom rail
        if rails.bottom > 0:
            bot_h = rails.bottom * s
            painter.drawText(QRectF(ox, oy + array.height * s - bot_h, array.width * s, bot_h),
                             Qt.AlignmentFlag.AlignCenter,
                             UnitConverter.format_dimension(rails.bottom, self.unit_system))
        # Left rail
        if rails.left > 0:
            left_w = rails.left * s
            painter.save()
            painter.translate(ox + left_w / 2, oy + array.height * s / 2)
            painter.rotate(-90)
            painter.drawText(QRectF(-array.height * s / 2, -left_w / 2, array.height * s, left_w),
                             Qt.AlignmentFlag.AlignCenter,
                             UnitConverter.format_dimension(rails.left, self.unit_system))
            painter.restore()
        # Right rail
        if rails.right > 0:
            right_w = rails.right * s
            painter.save()
            painter.translate(ox + array.width * s - right_w / 2, oy + array.height * s / 2)
            painter.rotate(-90)
            painter.drawText(QRectF(-array.height * s / 2, -right_w / 2, array.height * s, right_w),
                             Qt.AlignmentFlag.AlignCenter,
                             UnitConverter.format_dimension(rails.right, self.unit_system))
            painter.restore()

        # PCB dimensions
        if array.pcbs_rotated:
            pcb_w, pcb_h = config.pcb.height, config.pcb.width
        else:
            pcb_w, pcb_h = config.pcb.width, config.pcb.height

        start_x = ox + rails.left * s
        start_y = oy + rails.top * s

        # Draw PCBs
        for py in range(array.pcb_count_y):
            for px in range(array.pcb_count_x):
                pcb_x = start_x + px * (pcb_w + config.array_spacing.x_spacing) * s
                pcb_y = start_y + py * (pcb_h + config.array_spacing.y_spacing) * s
                pcb_rect = QRectF(pcb_x, pcb_y, pcb_w * s, pcb_h * s)
                painter.fillRect(pcb_rect, self.color_pcb)
                painter.setPen(QPen(self.color_pcb_border, 1))
                painter.drawRect(pcb_rect)

        # Dimension annotations — use palette foreground for theme compatibility
        fg = self.palette().color(self.foregroundRole())
        painter.setPen(QPen(fg, 1))
        painter.setFont(QFont("Arial", 9))

        # Array width (top)
        dim_y = oy - 20
        painter.drawLine(int(ox), int(dim_y), int(ox + array.width * s), int(dim_y))
        painter.drawText(QRectF(ox, dim_y - 16, array.width * s, 16),
                         Qt.AlignmentFlag.AlignCenter,
                         UnitConverter.format_dimension(array.width, self.unit_system))

        # Array height (left)
        dim_x = ox - 20
        painter.drawLine(int(dim_x), int(oy), int(dim_x), int(oy + array.height * s))
        painter.save()
        painter.translate(dim_x - 14, oy + array.height * s / 2)
        painter.rotate(-90)
        painter.drawText(0, 0, UnitConverter.format_dimension(array.height, self.unit_system))
        painter.restore()

        # PCB dimension label (inside first PCB)
        if array.pcb_count_x > 0 and array.pcb_count_y > 0:
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
            first_pcb = QRectF(start_x, start_y, pcb_w * s, pcb_h * s)
            pcb_label = (f"{UnitConverter.format_dimension(config.pcb.width, self.unit_system)} × "
                         f"{UnitConverter.format_dimension(config.pcb.height, self.unit_system)}")
            painter.drawText(first_pcb, Qt.AlignmentFlag.AlignCenter, pcb_label)


class VisualizationDialog(QDialog):
    """Popup dialog showing a single array configuration."""

    def __init__(self, panel: Panel, configuration: Configuration, parent=None):
        super().__init__(parent)

        array = panel.array
        rot_label = " (PCBs rotated)" if array.pcbs_rotated else ""
        self.setWindowTitle(
            f"Array Config: {array.pcb_count_x}×{array.pcb_count_y}{rot_label}"
        )
        self.setModal(True)

        # Size to 90% of main window, centered on it
        if parent:
            main_win = parent.window()
            geom = main_win.geometry()
            w = int(geom.width() * 0.9)
            h = int(geom.height() * 0.9)
            self.resize(w, h)
            self.move(
                geom.x() + (geom.width() - w) // 2,
                geom.y() + (geom.height() - h) // 2,
            )
        else:
            self.resize(1000, 700)

        layout = QVBoxLayout(self)

        # Header — array-centric
        unit_sys = UnitSystem.METRIC
        if configuration.user_preferences:
            unit_sys = configuration.user_preferences.unit_system
        arr_w = UnitConverter.format_dimension(array.width, unit_sys)
        arr_h = UnitConverter.format_dimension(array.height, unit_sys)

        header = QLabel(
            f"<b>{array.pcb_count_x} × {array.pcb_count_y} PCBs{rot_label}</b>"
            f" &nbsp;|&nbsp; Array: {arr_w} × {arr_h}"
            f" &nbsp;|&nbsp; {panel.total_pcb_count} PCBs/panel"
            f" &nbsp;|&nbsp; {panel.utilization_percentage:.1f}% utilization"
        )
        header.setStyleSheet("font-size: 13pt; padding: 8px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Array canvas
        canvas = ArrayCanvas()
        canvas.set_data(panel, configuration)
        layout.addWidget(canvas, 1)

        # Legend
        legend = QLabel(
            "<b>Legend:</b> "
            '<span style="color: #649664;">&#9632;</span> PCB &nbsp; '
            '<span style="color: #B4B4B4;">&#9632;</span> Rails'
        )
        legend.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(legend)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(120)
        close_btn.setFixedHeight(36)
        close_btn.setStyleSheet("font-size: 11pt;")
        close_btn.clicked.connect(self.accept)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
