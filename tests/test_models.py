"""
Unit tests for core data models.
"""

import pytest
from src.models import (
    PCB, ArraySpacing, ArrayRails, Array,
    PanelSize, Panel, Configuration,
    UnitSystem, UserPreferences
)


class TestPCB:
    """Test PCB data model"""

    def test_create_pcb(self):
        """Test creating a PCB"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=True)
        assert pcb.width == 100.0
        assert pcb.height == 80.0
        assert pcb.allow_rotation is True

    def test_pcb_area(self):
        """Test PCB area calculation"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=False)
        assert pcb.area == 8000.0

    def test_pcb_invalid_width(self):
        """Test PCB with invalid width"""
        with pytest.raises(ValueError, match="width must be positive"):
            PCB(width=0, height=80.0, allow_rotation=False)

    def test_pcb_invalid_height(self):
        """Test PCB with invalid height"""
        with pytest.raises(ValueError, match="height must be positive"):
            PCB(width=100.0, height=-10.0, allow_rotation=False)

    def test_pcb_serialization(self):
        """Test PCB to/from dict"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=True)
        data = pcb.to_dict()
        restored = PCB.from_dict(data)
        assert restored.width == pcb.width
        assert restored.height == pcb.height
        assert restored.allow_rotation == pcb.allow_rotation


class TestArraySpacing:
    """Test ArraySpacing data model"""

    def test_create_spacing(self):
        """Test creating array spacing"""
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        assert spacing.x_spacing == 3.0
        assert spacing.y_spacing == 3.0

    def test_zero_spacing(self):
        """Test zero spacing is valid"""
        spacing = ArraySpacing(x_spacing=0.0, y_spacing=0.0)
        assert spacing.x_spacing == 0.0
        assert spacing.y_spacing == 0.0

    def test_invalid_negative_spacing(self):
        """Test negative spacing is invalid"""
        with pytest.raises(ValueError, match="must be non-negative"):
            ArraySpacing(x_spacing=-1.0, y_spacing=3.0)

    def test_spacing_serialization(self):
        """Test ArraySpacing to/from dict"""
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=4.0)
        data = spacing.to_dict()
        restored = ArraySpacing.from_dict(data)
        assert restored.x_spacing == spacing.x_spacing
        assert restored.y_spacing == spacing.y_spacing


class TestArrayRails:
    """Test ArrayRails data model"""

    def test_create_rails(self):
        """Test creating array rails"""
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)
        assert rails.top == 5.0
        assert rails.bottom == 5.0
        assert rails.left == 5.0
        assert rails.right == 5.0

    def test_zero_rails(self):
        """Test zero rails are valid"""
        rails = ArrayRails(top=0.0, bottom=0.0, left=0.0, right=0.0)
        assert rails.top == 0.0

    def test_invalid_negative_rails(self):
        """Test negative rails are invalid"""
        with pytest.raises(ValueError, match="must be non-negative"):
            ArrayRails(top=-1.0, bottom=5.0, left=5.0, right=5.0)

    def test_rails_serialization(self):
        """Test ArrayRails to/from dict"""
        rails = ArrayRails(top=5.0, bottom=6.0, left=7.0, right=8.0)
        data = rails.to_dict()
        restored = ArrayRails.from_dict(data)
        assert restored.top == rails.top
        assert restored.bottom == rails.bottom
        assert restored.left == rails.left
        assert restored.right == rails.right


class TestArray:
    """Test Array data model"""

    def test_create_array(self):
        """Test creating an array"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=True)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)
        array = Array(
            pcb=pcb,
            pcb_count_x=6,
            pcb_count_y=4,
            spacing=spacing,
            rails=rails,
            allow_rotation=True,
            pcbs_rotated=False
        )
        assert array.pcb_count_x == 6
        assert array.pcb_count_y == 4

    def test_array_width_not_rotated(self):
        """Test array width calculation without rotation"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=True)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)
        array = Array(
            pcb=pcb,
            pcb_count_x=6,
            pcb_count_y=4,
            spacing=spacing,
            rails=rails,
            allow_rotation=True,
            pcbs_rotated=False
        )
        # Width = left + right + (6 * 100) + (5 * 3)
        #      = 5 + 5 + 600 + 15 = 625
        assert array.width == 625.0

    def test_array_height_not_rotated(self):
        """Test array height calculation without rotation"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=True)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)
        array = Array(
            pcb=pcb,
            pcb_count_x=6,
            pcb_count_y=4,
            spacing=spacing,
            rails=rails,
            allow_rotation=True,
            pcbs_rotated=False
        )
        # Height = top + bottom + (4 * 80) + (3 * 3)
        #        = 5 + 5 + 320 + 9 = 339
        assert array.height == 339.0

    def test_array_width_with_rotation(self):
        """Test array width when PCBs are rotated"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=True)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)
        array = Array(
            pcb=pcb,
            pcb_count_x=6,
            pcb_count_y=4,
            spacing=spacing,
            rails=rails,
            allow_rotation=True,
            pcbs_rotated=True  # Rotated!
        )
        # Width = left + right + (6 * 80) + (5 * 3)  # Using height as width
        #      = 5 + 5 + 480 + 15 = 505
        assert array.width == 505.0

    def test_array_pcb_count(self):
        """Test total PCB count"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)
        array = Array(
            pcb=pcb,
            pcb_count_x=6,
            pcb_count_y=4,
            spacing=spacing,
            rails=rails,
            allow_rotation=False,
            pcbs_rotated=False
        )
        assert array.pcb_count == 24

    def test_array_pcb_area(self):
        """Test total PCB area"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)
        array = Array(
            pcb=pcb,
            pcb_count_x=6,
            pcb_count_y=4,
            spacing=spacing,
            rails=rails,
            allow_rotation=False,
            pcbs_rotated=False
        )
        # PCB area = 100 * 80 = 8000
        # Total = 8000 * 24 = 192000
        assert array.pcb_area == 192000.0

    def test_array_invalid_rotation(self):
        """Test that PCBs can't be rotated if not allowed"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)
        with pytest.raises(ValueError, match="Cannot rotate PCBs"):
            Array(
                pcb=pcb,
                pcb_count_x=6,
                pcb_count_y=4,
                spacing=spacing,
                rails=rails,
                allow_rotation=False,
                pcbs_rotated=True  # Invalid!
            )

    def test_array_serialization(self):
        """Test Array to/from dict"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=True)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)
        array = Array(
            pcb=pcb,
            pcb_count_x=6,
            pcb_count_y=4,
            spacing=spacing,
            rails=rails,
            allow_rotation=True,
            pcbs_rotated=False
        )
        data = array.to_dict()
        restored = Array.from_dict(data)
        assert restored.pcb_count_x == array.pcb_count_x
        assert restored.pcb_count_y == array.pcb_count_y
        assert restored.pcbs_rotated == array.pcbs_rotated


class TestPanelSize:
    """Test PanelSize data model"""

    def test_create_panel_size(self):
        """Test creating a panel size"""
        ps = PanelSize(
            name="Eurocard",
            width=600.0,
            height=450.0,
            array_spacing_x=5.0,
            array_spacing_y=5.0,
            border_keepout_x=10.0,
            border_keepout_y=10.0
        )
        assert ps.name == "Eurocard"
        assert ps.width == 600.0

    def test_usable_dimensions(self):
        """Test usable dimensions calculation"""
        ps = PanelSize(
            name="Test",
            width=600.0,
            height=450.0,
            array_spacing_x=5.0,
            array_spacing_y=5.0,
            border_keepout_x=10.0,
            border_keepout_y=10.0
        )
        # Usable width = 600 - 2*10 = 580
        assert ps.usable_width == 580.0
        # Usable height = 450 - 2*10 = 430
        assert ps.usable_height == 430.0

    def test_panel_areas(self):
        """Test panel area calculations"""
        ps = PanelSize(
            name="Test",
            width=600.0,
            height=450.0,
            array_spacing_x=5.0,
            array_spacing_y=5.0,
            border_keepout_x=10.0,
            border_keepout_y=10.0
        )
        assert ps.total_area == 270000.0  # 600 * 450
        assert ps.usable_area == 249400.0  # 580 * 430

    def test_panel_size_invalid_keepout(self):
        """Test panel size with invalid keepouts"""
        with pytest.raises(ValueError, match="keepout.*too large"):
            PanelSize(
                name="Invalid",
                width=600.0,
                height=450.0,
                array_spacing_x=5.0,
                array_spacing_y=5.0,
                border_keepout_x=350.0,  # Too large!
                border_keepout_y=10.0
            )

    def test_panel_size_serialization(self):
        """Test PanelSize to/from dict"""
        ps = PanelSize(
            name="Eurocard",
            width=600.0,
            height=450.0,
            array_spacing_x=5.0,
            array_spacing_y=5.0,
            border_keepout_x=10.0,
            border_keepout_y=10.0
        )
        data = ps.to_dict()
        restored = PanelSize.from_dict(data)
        assert restored.name == ps.name
        assert restored.width == ps.width
        assert restored.height == ps.height


class TestPanel:
    """Test Panel data model"""

    def test_create_panel(self):
        """Test creating a panel"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)
        array = Array(
            pcb=pcb,
            pcb_count_x=4,  # Smaller array: 4x3 = 12 PCBs
            pcb_count_y=3,
            spacing=spacing,
            rails=rails,
            allow_rotation=False,
            pcbs_rotated=False
        )
        # Array is: 4*100 + 3*3 + 10 = 419mm wide, 3*80 + 2*3 + 10 = 256mm tall
        panel_size = PanelSize(
            name="Test",
            width=600.0,
            height=450.0,
            array_spacing_x=5.0,
            array_spacing_y=5.0,
            border_keepout_x=10.0,
            border_keepout_y=10.0
        )
        panel = Panel(
            panel_size=panel_size,
            array=array,
            array_count_x=1,
            array_count_y=1,
            arrays_rotated=False
        )
        assert panel.array_count_x == 1
        assert panel.array_count_y == 1

    def test_panel_total_pcb_count(self):
        """Test total PCB count on panel"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)
        array = Array(
            pcb=pcb,
            pcb_count_x=3,
            pcb_count_y=3,  # 9 PCBs per array
            spacing=spacing,
            rails=rails,
            allow_rotation=False,
            pcbs_rotated=False
        )
        # Array is: 3*100 + 2*3 + 10 = 316mm wide, 3*80 + 2*3 + 10 = 256mm tall
        panel_size = PanelSize(
            name="Test",
            width=700.0,
            height=600.0,
            array_spacing_x=5.0,
            array_spacing_y=5.0,
            border_keepout_x=10.0,
            border_keepout_y=10.0
        )
        # Usable: 680x580mm - can fit 2x2 arrays
        panel = Panel(
            panel_size=panel_size,
            array=array,
            array_count_x=2,  # 2x2 = 4 arrays
            array_count_y=2,
            arrays_rotated=False
        )
        # Total = 9 * 4 = 36 PCBs
        assert panel.total_pcb_count == 36

    def test_panel_utilization(self):
        """Test panel utilization calculation"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=0.0, y_spacing=0.0)
        rails = ArrayRails(top=0.0, bottom=0.0, left=0.0, right=0.0)
        array = Array(
            pcb=pcb,
            pcb_count_x=1,
            pcb_count_y=1,  # 1 PCB = 8000 mm²
            spacing=spacing,
            rails=rails,
            allow_rotation=False,
            pcbs_rotated=False
        )
        panel_size = PanelSize(
            name="Test",
            width=200.0,
            height=200.0,  # Panel = 40000 mm²
            array_spacing_x=0.0,
            array_spacing_y=0.0,
            border_keepout_x=0.0,
            border_keepout_y=0.0
        )
        panel = Panel(
            panel_size=panel_size,
            array=array,
            array_count_x=1,
            array_count_y=1,
            arrays_rotated=False
        )
        # Utilization = 8000 / 40000 = 0.2 = 20%
        assert panel.utilization_ratio == 0.2
        assert panel.utilization_percentage == 20.0

    def test_panel_arrays_dont_fit(self):
        """Test panel validation when arrays don't fit (with validate_fit=True)"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)
        array = Array(
            pcb=pcb,
            pcb_count_x=10,
            pcb_count_y=10,  # Very large array
            spacing=spacing,
            rails=rails,
            allow_rotation=False,
            pcbs_rotated=False
        )
        panel_size = PanelSize(
            name="Small",
            width=100.0,  # Too small!
            height=100.0,
            array_spacing_x=5.0,
            array_spacing_y=5.0,
            border_keepout_x=5.0,
            border_keepout_y=5.0
        )
        # Should raise exception when validate_fit=True (default)
        with pytest.raises(ValueError, match="don't fit"):
            Panel(
                panel_size=panel_size,
                array=array,
                array_count_x=1,
                array_count_y=1,
                arrays_rotated=False,
                validate_fit=True
            )

    def test_panel_is_valid(self):
        """Test panel validity checking"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)
        array = Array(
            pcb=pcb,
            pcb_count_x=10,
            pcb_count_y=10,  # Very large array
            spacing=spacing,
            rails=rails,
            allow_rotation=False,
            pcbs_rotated=False
        )
        panel_size = PanelSize(
            name="Small",
            width=100.0,  # Too small!
            height=100.0,
            array_spacing_x=5.0,
            array_spacing_y=5.0,
            border_keepout_x=5.0,
            border_keepout_y=5.0
        )
        # Create panel without validation
        panel = Panel(
            panel_size=panel_size,
            array=array,
            array_count_x=1,
            array_count_y=1,
            arrays_rotated=False,
            validate_fit=False  # Don't validate during construction
        )
        # Check validity explicitly
        assert panel.is_valid() is False

    def test_panel_get_fit_error(self):
        """Test getting fit error messages"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=0.0, y_spacing=0.0)
        rails = ArrayRails(top=0.0, bottom=0.0, left=0.0, right=0.0)
        array = Array(
            pcb=pcb,
            pcb_count_x=10,
            pcb_count_y=10,  # 1000x800mm array
            spacing=spacing,
            rails=rails,
            allow_rotation=False,
            pcbs_rotated=False
        )
        panel_size = PanelSize(
            name="Small",
            width=100.0,  # Only 90mm usable
            height=100.0,
            array_spacing_x=0.0,
            array_spacing_y=0.0,
            border_keepout_x=5.0,
            border_keepout_y=5.0
        )
        panel = Panel(
            panel_size=panel_size,
            array=array,
            array_count_x=1,
            array_count_y=1,
            arrays_rotated=False,
            validate_fit=False
        )
        error = panel.get_fit_error()
        assert "Width exceeds" in error
        assert "Height exceeds" in error

    def test_panel_valid_configuration_no_error(self):
        """Test that valid panels return empty error string"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=0.0, y_spacing=0.0)
        rails = ArrayRails(top=0.0, bottom=0.0, left=0.0, right=0.0)
        array = Array(
            pcb=pcb,
            pcb_count_x=1,
            pcb_count_y=1,
            spacing=spacing,
            rails=rails,
            allow_rotation=False,
            pcbs_rotated=False
        )
        panel_size = PanelSize(
            name="Large",
            width=200.0,
            height=200.0,
            array_spacing_x=0.0,
            array_spacing_y=0.0,
            border_keepout_x=0.0,
            border_keepout_y=0.0
        )
        panel = Panel(
            panel_size=panel_size,
            array=array,
            array_count_x=1,
            array_count_y=1,
            arrays_rotated=False
        )
        assert panel.is_valid() is True
        assert panel.get_fit_error() == ""

    def test_panel_serialization(self):
        """Test Panel to/from dict"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)
        array = Array(
            pcb=pcb,
            pcb_count_x=4,
            pcb_count_y=3,
            spacing=spacing,
            rails=rails,
            allow_rotation=False,
            pcbs_rotated=False
        )
        panel_size = PanelSize(
            name="Test",
            width=600.0,
            height=450.0,
            array_spacing_x=5.0,
            array_spacing_y=5.0,
            border_keepout_x=10.0,
            border_keepout_y=10.0
        )
        panel = Panel(
            panel_size=panel_size,
            array=array,
            array_count_x=1,
            array_count_y=1,
            arrays_rotated=False
        )
        data = panel.to_dict()
        restored = Panel.from_dict(data)
        assert restored.array_count_x == panel.array_count_x
        assert restored.arrays_rotated == panel.arrays_rotated
        assert restored.validate_fit == panel.validate_fit


class TestConfiguration:
    """Test Configuration data model"""

    def test_create_configuration(self):
        """Test creating a configuration"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=True)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)
        panel_size = PanelSize(
            name="Eurocard",
            width=600.0,
            height=450.0,
            array_spacing_x=5.0,
            array_spacing_y=5.0,
            border_keepout_x=10.0,
            border_keepout_y=10.0
        )
        config = Configuration(
            project_name="Test Project",
            pcb=pcb,
            array_spacing=spacing,
            array_rails=rails,
            allow_array_rotation=True,
            panel_sizes=[panel_size],
            user_preferences=UserPreferences(unit_system=UnitSystem.METRIC)
        )
        assert config.project_name == "Test Project"
        assert config.allow_array_rotation is True

    def test_configuration_no_panel_sizes(self):
        """Test configuration with no panel sizes"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=True)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)
        with pytest.raises(ValueError, match="At least one panel size"):
            Configuration(
                pcb=pcb,
                array_spacing=spacing,
                array_rails=rails,
                allow_array_rotation=True,
                panel_sizes=[]  # Empty!
            )

    def test_configuration_serialization(self):
        """Test Configuration to/from dict"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=True)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)
        panel_size = PanelSize(
            name="Eurocard",
            width=600.0,
            height=450.0,
            array_spacing_x=5.0,
            array_spacing_y=5.0,
            border_keepout_x=10.0,
            border_keepout_y=10.0
        )
        config = Configuration(
            project_name="Test",
            pcb=pcb,
            array_spacing=spacing,
            array_rails=rails,
            allow_array_rotation=True,
            panel_sizes=[panel_size],
            user_preferences=UserPreferences(unit_system=UnitSystem.IMPERIAL)
        )
        data = config.to_dict()
        restored = Configuration.from_dict(data)
        assert restored.project_name == config.project_name
        assert restored.user_preferences.unit_system == UnitSystem.IMPERIAL
        assert len(restored.panel_sizes) == 1
