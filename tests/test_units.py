"""
Unit tests for unit conversion and formatting.
"""

import pytest
from src.models.units import UnitSystem, UnitConverter, UserPreferences


class TestUnitConverter:
    """Test unit conversion functionality"""

    def test_mm_to_inches_exact(self):
        """Test exact conversion from mm to inches"""
        assert UnitConverter.mm_to_inches(25.4) == 1.0
        assert UnitConverter.mm_to_inches(254.0) == 10.0
        assert UnitConverter.mm_to_inches(0.0) == 0.0

    def test_inches_to_mm_exact(self):
        """Test exact conversion from inches to mm"""
        assert UnitConverter.inches_to_mm(1.0) == 25.4
        assert UnitConverter.inches_to_mm(10.0) == 254.0
        assert UnitConverter.inches_to_mm(0.0) == 0.0

    def test_mm_to_mils(self):
        """Test conversion from mm to mils"""
        assert UnitConverter.mm_to_mils(25.4) == 1000.0
        assert UnitConverter.mm_to_mils(2.54) == 100.0
        assert abs(UnitConverter.mm_to_mils(1.0) - 39.3700787) < 0.0001

    def test_mils_to_mm(self):
        """Test conversion from mils to mm"""
        assert UnitConverter.mils_to_mm(1000.0) == 25.4
        assert UnitConverter.mils_to_mm(100.0) == 2.54
        assert abs(UnitConverter.mils_to_mm(39.37) - 1.0) < 0.001

    def test_round_trip_mm_to_inches(self):
        """Test round-trip conversion mm -> in -> mm"""
        test_values = [100.0, 50.5, 1.27, 0.254, 1000.0]
        for mm in test_values:
            inches = UnitConverter.mm_to_inches(mm)
            back_to_mm = UnitConverter.inches_to_mm(inches)
            assert abs(mm - back_to_mm) < UnitConverter.EPSILON

    def test_round_trip_mm_to_mils(self):
        """Test round-trip conversion mm -> mils -> mm"""
        test_values = [100.0, 50.5, 1.27, 0.254, 1000.0]
        for mm in test_values:
            mils = UnitConverter.mm_to_mils(mm)
            back_to_mm = UnitConverter.mils_to_mm(mils)
            assert abs(mm - back_to_mm) < UnitConverter.EPSILON

    def test_format_dimension_metric(self):
        """Test formatting dimensions in metric system"""
        assert UnitConverter.format_dimension(100.0, UnitSystem.METRIC) == "100.00 mm"
        assert UnitConverter.format_dimension(50.5, UnitSystem.METRIC) == "50.50 mm"
        assert UnitConverter.format_dimension(1.234, UnitSystem.METRIC) == "1.23 mm"
        assert UnitConverter.format_dimension(0.1, UnitSystem.METRIC) == "0.10 mm"

    def test_format_dimension_imperial_inches(self):
        """Test formatting dimensions in imperial (inches) for larger values"""
        # 100mm = 3.937 inches (should use inches, not mils)
        assert UnitConverter.format_dimension(100.0, UnitSystem.IMPERIAL) == "3.937 in"
        # 25.4mm = 1.000 inches
        assert UnitConverter.format_dimension(25.4, UnitSystem.IMPERIAL) == "1.000 in"

    def test_format_dimension_imperial_mils(self):
        """Test formatting dimensions in imperial (mils) for small values"""
        # 2.54mm = 0.1 inches = 100 mils (boundary case)
        # Values < 0.1 inches should use mils
        result = UnitConverter.format_dimension(2.0, UnitSystem.IMPERIAL)
        assert "mil" in result
        # 1mm = 39.37 mils
        assert UnitConverter.format_dimension(1.0, UnitSystem.IMPERIAL) == "39.4 mil"

    def test_format_dimension_custom_precision(self):
        """Test formatting with custom precision"""
        assert UnitConverter.format_dimension(100.123, UnitSystem.METRIC, precision=3) == "100.123 mm"
        assert UnitConverter.format_dimension(100.123, UnitSystem.METRIC, precision=1) == "100.1 mm"

    def test_parse_dimension_metric(self):
        """Test parsing metric dimension strings"""
        assert UnitConverter.parse_dimension("100", UnitSystem.METRIC) == 100.0
        assert UnitConverter.parse_dimension("50.5", UnitSystem.METRIC) == 50.5
        assert UnitConverter.parse_dimension("  1.234  ", UnitSystem.METRIC) == 1.234

    def test_parse_dimension_imperial(self):
        """Test parsing imperial dimension strings (assumes inches)"""
        # 1 inch = 25.4 mm
        assert UnitConverter.parse_dimension("1", UnitSystem.IMPERIAL) == 25.4
        # 10 inches = 254 mm
        assert UnitConverter.parse_dimension("10", UnitSystem.IMPERIAL) == 254.0
        # 3.937 inches ≈ 100 mm
        result = UnitConverter.parse_dimension("3.937", UnitSystem.IMPERIAL)
        assert abs(result - 100.0) < 0.01

    def test_parse_dimension_invalid(self):
        """Test parsing invalid dimension strings"""
        with pytest.raises(ValueError):
            UnitConverter.parse_dimension("abc", UnitSystem.METRIC)
        with pytest.raises(ValueError):
            UnitConverter.parse_dimension("", UnitSystem.METRIC)
        with pytest.raises(ValueError):
            UnitConverter.parse_dimension("12.34.56", UnitSystem.METRIC)

    def test_get_display_value_metric(self):
        """Test getting display values for metric system"""
        assert UnitConverter.get_display_value(100.0, UnitSystem.METRIC) == 100.0
        assert UnitConverter.get_display_value(50.567, UnitSystem.METRIC) == 50.57
        assert UnitConverter.get_display_value(1.234, UnitSystem.METRIC) == 1.23

    def test_get_display_value_imperial_inches(self):
        """Test getting display values for imperial (inches)"""
        # 100mm = 3.937 inches
        assert UnitConverter.get_display_value(100.0, UnitSystem.IMPERIAL) == 3.937
        # 25.4mm = 1.000 inches
        assert UnitConverter.get_display_value(25.4, UnitSystem.IMPERIAL) == 1.0

    def test_get_display_value_imperial_mils(self):
        """Test getting display values for imperial (mils) for small values"""
        # 1mm = 39.37 mils (< 0.1 inches, should use mils)
        assert UnitConverter.get_display_value(1.0, UnitSystem.IMPERIAL) == 39.4
        # 2mm = 78.74 mils
        assert UnitConverter.get_display_value(2.0, UnitSystem.IMPERIAL) == 78.7

    def test_get_unit_label_metric(self):
        """Test getting unit labels for metric system"""
        assert UnitConverter.get_unit_label(UnitSystem.METRIC) == "mm"
        assert UnitConverter.get_unit_label(UnitSystem.METRIC, 100.0) == "mm"

    def test_get_unit_label_imperial_inches(self):
        """Test getting unit labels for imperial (inches)"""
        assert UnitConverter.get_unit_label(UnitSystem.IMPERIAL) == "in"
        # 100mm > 0.1 inches, should return "in"
        assert UnitConverter.get_unit_label(UnitSystem.IMPERIAL, 100.0) == "in"

    def test_get_unit_label_imperial_mils(self):
        """Test getting unit labels for imperial (mils)"""
        # 1mm < 0.1 inches, should return "mil"
        assert UnitConverter.get_unit_label(UnitSystem.IMPERIAL, 1.0) == "mil"
        # 2mm < 0.1 inches, should return "mil"
        assert UnitConverter.get_unit_label(UnitSystem.IMPERIAL, 2.0) == "mil"

    def test_format_dual_dimension_metric_primary(self):
        """Test dual dimension formatting with metric primary"""
        result = UnitConverter.format_dual_dimension(100.0, UnitSystem.METRIC)
        assert result == "100.00 mm (3.937 in)"

        result = UnitConverter.format_dual_dimension(25.4, UnitSystem.METRIC)
        assert result == "25.40 mm (1.000 in)"

    def test_format_dual_dimension_imperial_primary(self):
        """Test dual dimension formatting with imperial primary"""
        result = UnitConverter.format_dual_dimension(100.0, UnitSystem.IMPERIAL)
        assert result == "3.937 in (100.00 mm)"

        result = UnitConverter.format_dual_dimension(25.4, UnitSystem.IMPERIAL)
        assert result == "1.000 in (25.40 mm)"

    def test_validate_dimension_input_valid_metric(self):
        """Test validation of valid metric inputs"""
        is_valid, value_mm, error = UnitConverter.validate_dimension_input("100", UnitSystem.METRIC)
        assert is_valid
        assert value_mm == 100.0
        assert error == ""

    def test_validate_dimension_input_valid_imperial(self):
        """Test validation of valid imperial inputs"""
        is_valid, value_mm, error = UnitConverter.validate_dimension_input("4", UnitSystem.IMPERIAL)
        assert is_valid
        assert value_mm == 101.6  # 4 inches = 101.6 mm
        assert error == ""

    def test_validate_dimension_input_invalid_format(self):
        """Test validation of invalid format"""
        is_valid, value_mm, error = UnitConverter.validate_dimension_input("abc", UnitSystem.METRIC)
        assert not is_valid
        assert value_mm == 0.0
        assert "Invalid number format" in error

    def test_validate_dimension_input_negative(self):
        """Test validation of negative values"""
        is_valid, value_mm, error = UnitConverter.validate_dimension_input("-5", UnitSystem.METRIC)
        assert not is_valid
        assert "positive" in error.lower()

    def test_validate_dimension_input_zero(self):
        """Test validation of zero value"""
        is_valid, value_mm, error = UnitConverter.validate_dimension_input("0", UnitSystem.METRIC)
        assert not is_valid
        assert "positive" in error.lower()

    def test_validate_dimension_input_too_small(self):
        """Test validation of too small values"""
        is_valid, value_mm, error = UnitConverter.validate_dimension_input("0.05", UnitSystem.METRIC)
        assert not is_valid
        assert "too small" in error.lower()

    def test_validate_dimension_input_too_large(self):
        """Test validation of too large values"""
        is_valid, value_mm, error = UnitConverter.validate_dimension_input("15000", UnitSystem.METRIC)
        assert not is_valid
        assert "too large" in error.lower()

    def test_dimensions_equal_exact(self):
        """Test exact dimension comparison"""
        assert UnitConverter.dimensions_equal(100.0, 100.0)
        assert UnitConverter.dimensions_equal(0.0, 0.0)

    def test_dimensions_equal_within_epsilon(self):
        """Test dimension comparison within epsilon tolerance"""
        assert UnitConverter.dimensions_equal(100.0, 100.0 + UnitConverter.EPSILON / 2)
        assert UnitConverter.dimensions_equal(50.5, 50.5 - UnitConverter.EPSILON / 2)

    def test_dimensions_not_equal(self):
        """Test dimension comparison for unequal values"""
        assert not UnitConverter.dimensions_equal(100.0, 100.1)
        assert not UnitConverter.dimensions_equal(50.0, 51.0)

    def test_dimensions_equal_custom_tolerance(self):
        """Test dimension comparison with custom tolerance"""
        assert UnitConverter.dimensions_equal(100.0, 100.05, tolerance=0.1)
        assert not UnitConverter.dimensions_equal(100.0, 100.2, tolerance=0.1)


class TestUserPreferences:
    """Test UserPreferences dataclass"""

    def test_default_preferences(self):
        """Test default user preferences"""
        prefs = UserPreferences()
        assert prefs.unit_system == UnitSystem.METRIC

    def test_to_dict(self):
        """Test conversion to dictionary"""
        prefs = UserPreferences(unit_system=UnitSystem.IMPERIAL)
        data = prefs.to_dict()
        assert data == {"unit_system": "imperial"}

    def test_from_dict(self):
        """Test creation from dictionary"""
        data = {"unit_system": "imperial"}
        prefs = UserPreferences.from_dict(data)
        assert prefs.unit_system == UnitSystem.IMPERIAL

    def test_from_dict_default(self):
        """Test creation from empty dictionary (uses defaults)"""
        prefs = UserPreferences.from_dict({})
        assert prefs.unit_system == UnitSystem.METRIC

    def test_round_trip_serialization(self):
        """Test round-trip serialization"""
        original = UserPreferences(unit_system=UnitSystem.IMPERIAL)
        data = original.to_dict()
        restored = UserPreferences.from_dict(data)
        assert original.unit_system == restored.unit_system
