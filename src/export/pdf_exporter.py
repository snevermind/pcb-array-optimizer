"""
PDF export functionality using ReportLab.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, mm as reportlab_mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group
from reportlab.graphics import renderPDF

from typing import List, Optional
from datetime import datetime

from src.models import Panel, Configuration, UnitSystem
from src.models.units import UnitConverter


class PDFExporter:
    """Export optimization results to PDF"""

    def __init__(self, page_size=letter):
        """
        Initialize PDF exporter.

        Args:
            page_size: Page size (letter or A4)
        """
        self.page_size = page_size
        self.width, self.height = page_size
        self.margin = 0.75 * inch
        self.styles = getSampleStyleSheet()

        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            alignment=TA_CENTER
        )

        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2a2a2a'),
            spaceAfter=10,
            spaceBefore=10
        )

        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#3a3a3a')
        )

    def export_results(
        self,
        file_path: str,
        configuration: Configuration,
        results: List[Panel],
        selected_panel: Optional[Panel] = None
    ):
        """
        Export optimization results to PDF.

        Args:
            file_path: Output PDF file path
            configuration: Optimization configuration
            results: List of panel results
            selected_panel: Currently selected panel (highlighted in report)
        """
        # Create PDF document
        doc = SimpleDocTemplate(
            file_path,
            pagesize=self.page_size,
            leftMargin=self.margin,
            rightMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )

        # Build content
        story = []

        if selected_panel:
            rank = results.index(selected_panel) + 1 if selected_panel in results else 1

            # Page 1: Array graphic with title and key stats
            story.extend(self._create_graphic_page(configuration, selected_panel, rank))
            story.append(PageBreak())

            # Page 2: Detailed specifications
            story.extend(self._create_specs_page(configuration, selected_panel, rank))
        else:
            story.extend(self._create_title_page(configuration))

        # Build PDF
        doc.build(story, onFirstPage=self._add_footer, onLaterPages=self._add_footer)

    def _create_graphic_page(self, configuration: Configuration, panel: Panel, rank: int) -> List:
        """Page 1: Array graphic with title and key stats"""
        story = []

        unit_system = UnitSystem.METRIC
        if configuration.user_preferences:
            unit_system = configuration.user_preferences.unit_system

        array = panel.array
        rot = " (PCBs Rotated)" if array.pcbs_rotated else ""

        # Title
        story.append(Paragraph("PCB Array Optimization Report", self.title_style))
        story.append(Spacer(1, 0.15 * inch))

        # Key stats line
        arr_w = UnitConverter.format_dimension(array.width, unit_system)
        arr_h = UnitConverter.format_dimension(array.height, unit_system)
        stats = (
            f"<b>Rank #{rank}</b> &nbsp;|&nbsp; "
            f"{array.pcb_count_x} × {array.pcb_count_y} PCBs{rot} &nbsp;|&nbsp; "
            f"Array: {arr_w} × {arr_h} &nbsp;|&nbsp; "
            f"{panel.total_pcb_count} PCBs/panel &nbsp;|&nbsp; "
            f"{panel.utilization_percentage:.1f}% utilization"
        )
        stats_style = ParagraphStyle('Stats', parent=self.body_style,
                                     fontSize=10, alignment=TA_CENTER)
        story.append(Paragraph(stats, stats_style))
        story.append(Spacer(1, 0.25 * inch))

        # Array drawing — use available width, cap height to leave room
        avail_width = self.width - 2 * self.margin
        max_height = 6.5 * inch  # leave room for title + stats + legend
        drawing = self._create_array_drawing(configuration, panel, avail_width, max_height)
        story.append(drawing)
        story.append(Spacer(1, 0.15 * inch))

        # Legend
        legend_style = ParagraphStyle('Legend', parent=self.body_style,
                                      fontSize=9, alignment=TA_CENTER,
                                      textColor=colors.HexColor('#666666'))
        story.append(Paragraph(
            '<font color="#649664">&#9632;</font> PCB &nbsp;&nbsp; '
            '<font color="#B4B4B4">&#9632;</font> Rails',
            legend_style
        ))

        return story

    def _create_specs_page(self, configuration: Configuration, panel: Panel, rank: int) -> List:
        """Page 2: Detailed specifications"""
        story = []

        unit_system = UnitSystem.METRIC
        if configuration.user_preferences:
            unit_system = configuration.user_preferences.unit_system

        story.append(Paragraph(f"Specifications — Rank #{rank}", self.heading_style))
        story.append(Spacer(1, 0.1 * inch))

        # PCB
        story.append(Paragraph("<b>PCB</b>", self.body_style))
        story.append(Spacer(1, 0.05 * inch))
        pcb_data = [
            ['Width', UnitConverter.format_dimension(configuration.pcb.width, unit_system)],
            ['Height', UnitConverter.format_dimension(configuration.pcb.height, unit_system)],
            ['Rotation', 'Yes' if configuration.pcb.allow_rotation else 'No'],
        ]
        story.append(Table(pcb_data, colWidths=[2*inch, 4*inch]))
        story[-1].setStyle(self._get_table_style())
        story.append(Spacer(1, 0.15 * inch))

        # Array
        story.append(Paragraph("<b>Array Configuration</b>", self.body_style))
        story.append(Spacer(1, 0.05 * inch))
        array_data = [
            ['PCBs per Array', f'{panel.array.pcb_count_x} × {panel.array.pcb_count_y}'
             f' ({"Rotated" if panel.array.pcbs_rotated else "Not Rotated"})'],
            ['Array Dimensions',
             f'{UnitConverter.format_dimension(panel.array.width, unit_system)} × '
             f'{UnitConverter.format_dimension(panel.array.height, unit_system)}'],
            ['PCB Spacing',
             f'X: {UnitConverter.format_dimension(configuration.array_spacing.x_spacing, unit_system)}  '
             f'Y: {UnitConverter.format_dimension(configuration.array_spacing.y_spacing, unit_system)}'],
            ['Rails',
             f'T: {UnitConverter.format_dimension(configuration.array_rails.top, unit_system)}  '
             f'B: {UnitConverter.format_dimension(configuration.array_rails.bottom, unit_system)}  '
             f'L: {UnitConverter.format_dimension(configuration.array_rails.left, unit_system)}  '
             f'R: {UnitConverter.format_dimension(configuration.array_rails.right, unit_system)}'],
        ]
        story.append(Table(array_data, colWidths=[2*inch, 4*inch]))
        story[-1].setStyle(self._get_table_style())
        story.append(Spacer(1, 0.15 * inch))

        # Panel
        story.append(Paragraph("<b>Panel</b>", self.body_style))
        story.append(Spacer(1, 0.05 * inch))
        panel_data = [
            ['Panel Size', panel.panel_size.name],
            ['Panel Dimensions',
             f'{UnitConverter.format_dimension(panel.panel_size.width, unit_system)} × '
             f'{UnitConverter.format_dimension(panel.panel_size.height, unit_system)}'],
            ['Border Keepout',
             f'{UnitConverter.format_dimension(panel.panel_size.border_keepout_x, unit_system)} × '
             f'{UnitConverter.format_dimension(panel.panel_size.border_keepout_y, unit_system)}'],
            ['Arrays on Panel',
             f'{panel.array_count_x} × {panel.array_count_y}'
             f' ({"Rotated" if panel.arrays_rotated else "Not Rotated"})'],
            ['Total PCBs', str(panel.total_pcb_count)],
            ['Utilization', f'{panel.utilization_percentage:.2f}%'],
        ]
        story.append(Table(panel_data, colWidths=[2*inch, 4*inch]))
        story[-1].setStyle(self._get_table_style())
        story.append(Spacer(1, 0.15 * inch))

        # Generation info
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(f"<i>Generated: {date_str}</i>", self.body_style))

        return story

    def _create_array_drawing(self, configuration: Configuration, panel: Panel,
                              max_width: float, max_height: float) -> Drawing:
        """Create a drawing of a single array (PCBs inside rails), top-down orientation."""
        array = panel.array

        # Fit array into available space maintaining aspect ratio
        aspect = array.height / array.width
        width = max_width
        height = width * aspect
        if height > max_height:
            height = max_height
            width = height / aspect

        drawing = Drawing(width, height)
        scale = width / array.width

        # Array background (rails)
        bg = Rect(0, 0, width, height)
        bg.fillColor = colors.HexColor('#c8c8c8')
        bg.strokeColor = colors.HexColor('#808080')
        bg.strokeWidth = 2
        drawing.add(bg)

        # PCB dimensions (account for rotation within array)
        if array.pcbs_rotated:
            pcb_w = configuration.pcb.height * scale
            pcb_h = configuration.pcb.width * scale
        else:
            pcb_w = configuration.pcb.width * scale
            pcb_h = configuration.pcb.height * scale

        rails = configuration.array_rails
        spacing = configuration.array_spacing

        # ReportLab Y=0 is bottom. To render top-down (matching GUI):
        # GUI top rail → ReportLab top = height - rails.top*scale
        # First PCB row starts at the top, stepping downward.
        start_x = rails.left * scale
        top_y = height - rails.top * scale  # top edge of first PCB row

        for py in range(array.pcb_count_y):
            for px in range(array.pcb_count_x):
                pcb_x = start_x + px * (pcb_w + spacing.x_spacing * scale)
                # Y goes downward from top
                pcb_y = top_y - pcb_h - py * (pcb_h + spacing.y_spacing * scale)

                pcb_rect = Rect(pcb_x, pcb_y, pcb_w, pcb_h)
                pcb_rect.fillColor = colors.HexColor('#649664')
                pcb_rect.strokeColor = colors.HexColor('#3C6432')
                pcb_rect.strokeWidth = 0.5
                drawing.add(pcb_rect)

        return drawing

    def _create_title_page(self, configuration: Configuration) -> List:
        """Create title page content"""
        story = []

        # Title
        story.append(Spacer(1, 1.5 * inch))
        title = Paragraph("PCB Array Optimization Report", self.title_style)
        story.append(title)

        story.append(Spacer(1, 0.3 * inch))

        # Project name
        project_name = configuration.project_name or "Untitled Project"
        project = Paragraph(f"<b>Project:</b> {project_name}", self.body_style)
        story.append(project)

        story.append(Spacer(1, 0.2 * inch))

        # Date
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date = Paragraph(f"<b>Generated:</b> {date_str}", self.body_style)
        story.append(date)

        story.append(Spacer(1, 0.5 * inch))

        # Summary box
        unit_system = UnitSystem.METRIC
        if configuration.user_preferences:
            unit_system = configuration.user_preferences.unit_system

        pcb_width = UnitConverter.format_dimension(configuration.pcb.width, unit_system)
        pcb_height = UnitConverter.format_dimension(configuration.pcb.height, unit_system)

        summary_data = [
            ['PCB Dimensions', f'{pcb_width} × {pcb_height}'],
            ['PCB Rotation', 'Allowed' if configuration.pcb.allow_rotation else 'Not Allowed'],
            ['Array Rotation', 'Allowed' if configuration.allow_array_rotation else 'Not Allowed'],
            ['Panel Templates', str(len(configuration.panel_sizes))]
        ]

        summary_table = Table(summary_data, colWidths=[2.5*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e0e0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(summary_table)

        return story

    def _create_configuration_summary(self, configuration: Configuration) -> List:
        """Create detailed configuration summary"""
        story = []

        unit_system = UnitSystem.METRIC
        if configuration.user_preferences:
            unit_system = configuration.user_preferences.unit_system

        # Heading
        story.append(Paragraph("Configuration Details", self.heading_style))
        story.append(Spacer(1, 0.1 * inch))

        # PCB Configuration
        story.append(Paragraph("<b>PCB Configuration</b>", self.body_style))
        story.append(Spacer(1, 0.05 * inch))

        pcb_data = [
            ['Width', UnitConverter.format_dimension(configuration.pcb.width, unit_system)],
            ['Height', UnitConverter.format_dimension(configuration.pcb.height, unit_system)],
            ['Area', f'{configuration.pcb.area:.2f} mm²'],
            ['Rotation Allowed', 'Yes' if configuration.pcb.allow_rotation else 'No']
        ]

        pcb_table = Table(pcb_data, colWidths=[2*inch, 4*inch])
        pcb_table.setStyle(self._get_table_style())
        story.append(pcb_table)

        story.append(Spacer(1, 0.2 * inch))

        # Array Configuration
        story.append(Paragraph("<b>Array Configuration</b>", self.body_style))
        story.append(Spacer(1, 0.05 * inch))

        array_data = [
            ['X Spacing', UnitConverter.format_dimension(configuration.array_spacing.x_spacing, unit_system)],
            ['Y Spacing', UnitConverter.format_dimension(configuration.array_spacing.y_spacing, unit_system)],
            ['Top Rail', UnitConverter.format_dimension(configuration.array_rails.top, unit_system)],
            ['Bottom Rail', UnitConverter.format_dimension(configuration.array_rails.bottom, unit_system)],
            ['Left Rail', UnitConverter.format_dimension(configuration.array_rails.left, unit_system)],
            ['Right Rail', UnitConverter.format_dimension(configuration.array_rails.right, unit_system)],
            ['Array Rotation', 'Allowed' if configuration.allow_array_rotation else 'Not Allowed']
        ]

        array_table = Table(array_data, colWidths=[2*inch, 4*inch])
        array_table.setStyle(self._get_table_style())
        story.append(array_table)

        return story

    def _create_results_table(
        self,
        configuration: Configuration,
        results: List[Panel],
        selected_panel: Optional[Panel]
    ) -> List:
        """Create results summary table"""
        story = []

        unit_system = UnitSystem.METRIC
        if configuration.user_preferences:
            unit_system = configuration.user_preferences.unit_system

        # Heading
        story.append(Paragraph("Optimization Results", self.heading_style))
        story.append(Spacer(1, 0.1 * inch))

        # Table header
        table_data = [
            ['Rank', 'Utilization', 'Panel Size', 'Array', 'Arrays', 'Total\nPCBs']
        ]

        # Add results
        for i, panel in enumerate(results, 1):
            array_config = f"{panel.array.pcb_count_x}×{panel.array.pcb_count_y}"
            if panel.array.pcbs_rotated:
                array_config += "R"

            arrays_config = f"{panel.array_count_x}×{panel.array_count_y}"
            if panel.arrays_rotated:
                arrays_config += "R"

            row = [
                f"#{i}",
                f"{panel.utilization_percentage:.1f}%",
                panel.panel_size.name,
                array_config,
                arrays_config,
                str(panel.total_pcb_count)
            ]
            table_data.append(row)

        # Create table
        results_table = Table(table_data, colWidths=[0.5*inch, 0.9*inch, 2.5*inch, 0.8*inch, 0.8*inch, 0.7*inch])

        # Style
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a4a4a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ])

        # Highlight selected panel
        if selected_panel and selected_panel in results:
            selected_idx = results.index(selected_panel) + 1
            style.add('BACKGROUND', (0, selected_idx), (-1, selected_idx), colors.HexColor('#ffffcc'))

        # Alternating row colors
        for i in range(1, len(table_data)):
            if selected_panel and selected_panel in results and i == results.index(selected_panel) + 1:
                continue  # Skip highlighted row
            if i % 2 == 0:
                style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f5f5f5'))

        results_table.setStyle(style)
        story.append(results_table)

        return story

    def _create_panel_detail(self, configuration: Configuration, panel: Panel, rank: int) -> List:
        """Create detailed panel layout page"""
        story = []

        unit_system = UnitSystem.METRIC
        if configuration.user_preferences:
            unit_system = configuration.user_preferences.unit_system

        # Heading
        title = f"Rank #{rank}: {panel.panel_size.name}"
        story.append(Paragraph(title, self.heading_style))
        story.append(Spacer(1, 0.1 * inch))

        # Utilization info
        util_text = f"<b>Utilization:</b> {panel.utilization_percentage:.2f}% " \
                   f"({panel.total_pcb_count} PCBs per panel)"
        story.append(Paragraph(util_text, self.body_style))
        story.append(Spacer(1, 0.15 * inch))

        # Panel visualization
        drawing = self._create_panel_drawing(configuration, panel, width=6*inch)
        story.append(drawing)
        story.append(Spacer(1, 0.2 * inch))

        # Detailed specifications
        story.append(Paragraph("<b>Specifications</b>", self.body_style))
        story.append(Spacer(1, 0.05 * inch))

        specs_data = [
            ['Panel Dimensions',
             f'{UnitConverter.format_dimension(panel.panel_size.width, unit_system)} × '
             f'{UnitConverter.format_dimension(panel.panel_size.height, unit_system)}'],
            ['Border Keepout',
             f'{UnitConverter.format_dimension(panel.panel_size.border_keepout_x, unit_system)} × '
             f'{UnitConverter.format_dimension(panel.panel_size.border_keepout_y, unit_system)}'],
            ['Array Spacing on Panel',
             f'{UnitConverter.format_dimension(panel.panel_size.array_spacing_x, unit_system)} × '
             f'{UnitConverter.format_dimension(panel.panel_size.array_spacing_y, unit_system)}'],
            ['', ''],
            ['Array Configuration',
             f'{panel.array.pcb_count_x} × {panel.array.pcb_count_y} PCBs '
             f'({"Rotated" if panel.array.pcbs_rotated else "Not Rotated"})'],
            ['Array Dimensions',
             f'{UnitConverter.format_dimension(panel.array.width, unit_system)} × '
             f'{UnitConverter.format_dimension(panel.array.height, unit_system)}'],
            ['Arrays on Panel',
             f'{panel.array_count_x} × {panel.array_count_y} = {panel.array_count_x * panel.array_count_y} arrays '
             f'({"Rotated" if panel.arrays_rotated else "Not Rotated"})'],
            ['', ''],
            ['Total PCBs per Panel', str(panel.total_pcb_count)],
            ['PCB Area Used', f'{panel.total_pcb_area:.2f} mm²'],
            ['Panel Area', f'{panel.panel_area:.2f} mm²'],
            ['Material Utilization', f'{panel.utilization_percentage:.2f}%']
        ]

        specs_table = Table(specs_data, colWidths=[2.2*inch, 4*inch])
        specs_table.setStyle(self._get_table_style())
        story.append(specs_table)

        return story

    def _create_panel_drawing(self, configuration: Configuration, panel: Panel, width: float) -> Drawing:
        """Create a drawing of the panel layout"""
        # Calculate aspect ratio
        aspect_ratio = panel.panel_size.height / panel.panel_size.width
        height = width * aspect_ratio

        # Create drawing
        drawing = Drawing(width, height)

        # Scale factor
        scale = width / panel.panel_size.width

        # Panel background
        panel_rect = Rect(0, 0, width, height)
        panel_rect.fillColor = colors.HexColor('#f0f0f0')
        panel_rect.strokeColor = colors.HexColor('#808080')
        panel_rect.strokeWidth = 2
        drawing.add(panel_rect)

        # Usable area (dashed)
        usable_x = panel.panel_size.border_keepout_x * scale
        usable_y = panel.panel_size.border_keepout_y * scale
        usable_width = panel.panel_size.usable_width * scale
        usable_height = panel.panel_size.usable_height * scale

        usable_rect = Rect(usable_x, usable_y, usable_width, usable_height)
        usable_rect.fillColor = None
        usable_rect.strokeColor = colors.HexColor('#c0c0c0')
        usable_rect.strokeWidth = 1
        usable_rect.strokeDashArray = [3, 3]
        drawing.add(usable_rect)

        # Draw arrays
        if panel.arrays_rotated:
            array_width = panel.array.height * scale
            array_height = panel.array.width * scale
        else:
            array_width = panel.array.width * scale
            array_height = panel.array.height * scale

        for ay in range(panel.array_count_y):
            for ax in range(panel.array_count_x):
                # Array position
                array_x = usable_x + ax * (array_width + panel.panel_size.array_spacing_x * scale)
                array_y = usable_y + ay * (array_height + panel.panel_size.array_spacing_y * scale)

                # Array background
                array_rect = Rect(array_x, array_y, array_width, array_height)
                array_rect.fillColor = colors.HexColor('#96B4DC')
                array_rect.strokeColor = colors.HexColor('#6478B4')
                array_rect.strokeWidth = 1.5
                drawing.add(array_rect)

                # Draw PCBs within array
                self._draw_pcbs_on_drawing(
                    drawing, configuration, panel,
                    array_x, array_y, scale
                )

        return drawing

    def _draw_pcbs_on_drawing(
        self, drawing: Drawing, configuration: Configuration,
        panel: Panel, array_x: float, array_y: float, scale: float
    ):
        """Draw PCBs within an array on the drawing"""
        array = panel.array

        # Get PCB dimensions based on rotation
        if array.pcbs_rotated:
            pcb_width = configuration.pcb.height * scale
            pcb_height = configuration.pcb.width * scale
        else:
            pcb_width = configuration.pcb.width * scale
            pcb_height = configuration.pcb.height * scale

        # Starting position (accounting for rails)
        start_x = array_x + configuration.array_rails.left * scale
        start_y = array_y + configuration.array_rails.bottom * scale

        # Draw each PCB
        for py in range(array.pcb_count_y):
            for px in range(array.pcb_count_x):
                pcb_x = start_x + px * (pcb_width + configuration.array_spacing.x_spacing * scale)
                pcb_y = start_y + py * (pcb_height + configuration.array_spacing.y_spacing * scale)

                pcb_rect = Rect(pcb_x, pcb_y, pcb_width, pcb_height)
                pcb_rect.fillColor = colors.HexColor('#649664')
                pcb_rect.strokeColor = colors.HexColor('#3C6432')
                pcb_rect.strokeWidth = 0.5
                drawing.add(pcb_rect)

    def _get_table_style(self) -> TableStyle:
        """Get standard table style"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8e8e8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ])

    def _add_footer(self, canvas_obj, doc):
        """Add footer to each page"""
        canvas_obj.saveState()

        # Page number
        page_num = canvas_obj.getPageNumber()
        text = f"Page {page_num}"
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.drawRightString(
            self.width - self.margin,
            self.margin / 2,
            text
        )

        # Generated by
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.grey)
        canvas_obj.drawString(
            self.margin,
            self.margin / 2,
            "Generated by PCB Array Optimizer"
        )

        canvas_obj.restoreState()
