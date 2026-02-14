"""
Unit tests for optimization algorithms.
"""

import pytest
from src.models import (
    PCB, ArraySpacing, ArrayRails, PanelSize, Configuration, UnitSystem, UserPreferences
)
from src.core import ArrayBuilder, PanelBuilder, LayoutOptimizer


class TestArrayBuilder:
    """Test array generation"""

    def test_generate_simple_arrays(self):
        """Test generating arrays for a simple PCB"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)

        arrays = list(ArrayBuilder.generate_arrays(
            pcb=pcb,
            spacing=spacing,
            rails=rails,
            allow_array_rotation=True,
            max_width_mm=500.0,
            max_height_mm=400.0
        ))

        # Should generate arrays
        assert len(arrays) > 0
        # First should be 1x1
        assert arrays[0].pcb_count_x == 1
        assert arrays[0].pcb_count_y == 1

    def test_generate_arrays_with_rotation(self):
        """Test that rotation creates additional array configs"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=True)
        spacing = ArraySpacing(x_spacing=0.0, y_spacing=0.0)
        rails = ArrayRails(top=0.0, bottom=0.0, left=0.0, right=0.0)

        # Count arrays without specifying constraints
        arrays_no_rot = list(ArrayBuilder.generate_arrays(
            pcb=PCB(width=100.0, height=80.0, allow_rotation=False),
            spacing=spacing,
            rails=rails,
            allow_array_rotation=False,
            max_width_mm=300.0,
            max_height_mm=300.0
        ))

        arrays_with_rot = list(ArrayBuilder.generate_arrays(
            pcb=pcb,
            spacing=spacing,
            rails=rails,
            allow_array_rotation=False,
            max_width_mm=300.0,
            max_height_mm=300.0
        ))

        # Rotation should create more configurations
        assert len(arrays_with_rot) > len(arrays_no_rot)

    def test_max_dimension_constraint(self):
        """Test that max dimensions limit array sizes"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=0.0, y_spacing=0.0)
        rails = ArrayRails(top=0.0, bottom=0.0, left=0.0, right=0.0)

        arrays = list(ArrayBuilder.generate_arrays(
            pcb=pcb,
            spacing=spacing,
            rails=rails,
            allow_array_rotation=False,
            max_width_mm=250.0,  # Should fit max 2 PCBs wide
            max_height_mm=200.0  # Should fit max 2 PCBs tall
        ))

        # Check that no array exceeds constraints
        for array in arrays:
            assert array.width <= 250.0
            assert array.height <= 200.0
            assert array.pcb_count_x <= 2
            assert array.pcb_count_y <= 2

    def test_count_possible_arrays(self):
        """Test counting arrays matches actual generation"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)

        count = ArrayBuilder.count_possible_arrays(
            pcb=pcb,
            spacing=spacing,
            rails=rails,
            allow_array_rotation=True,
            max_width_mm=400.0,
            max_height_mm=300.0
        )

        arrays = list(ArrayBuilder.generate_arrays(
            pcb=pcb,
            spacing=spacing,
            rails=rails,
            allow_array_rotation=True,
            max_width_mm=400.0,
            max_height_mm=300.0
        ))

        assert count == len(arrays)


class TestPanelBuilder:
    """Test panel generation"""

    def test_generate_simple_panels(self):
        """Test generating panels for a simple array"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)
        array = next(ArrayBuilder.generate_arrays(
            pcb, spacing, rails, allow_array_rotation=False
        ))  # Get 1x1 array

        panel_size = PanelSize(
            name="Test",
            width=600.0,
            height=450.0,
            array_spacing_x=5.0,
            array_spacing_y=5.0,
            border_keepout_x=10.0,
            border_keepout_y=10.0
        )

        panels = list(PanelBuilder.generate_panels(array, panel_size))

        # Should generate panels
        assert len(panels) > 0
        # All should be valid
        for panel in panels:
            assert panel.is_valid()

    def test_panels_sorted_by_count(self):
        """Test that panels are generated in order"""
        pcb = PCB(width=50.0, height=50.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=0.0, y_spacing=0.0)
        rails = ArrayRails(top=0.0, bottom=0.0, left=0.0, right=0.0)
        array = next(ArrayBuilder.generate_arrays(
            pcb, spacing, rails, allow_array_rotation=False
        ))  # 1x1 array = 50x50mm

        panel_size = PanelSize(
            name="Large",
            width=600.0,
            height=600.0,
            array_spacing_x=0.0,
            array_spacing_y=0.0,
            border_keepout_x=0.0,
            border_keepout_y=0.0
        )

        panels = list(PanelBuilder.generate_panels(array, panel_size, try_rotation=False))

        # First should be 1x1
        assert panels[0].array_count_x == 1
        assert panels[0].array_count_y == 1

    def test_no_panels_for_oversized_array(self):
        """Test that no panels generated if array too large"""
        pcb = PCB(width=1000.0, height=800.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=0.0, y_spacing=0.0)
        rails = ArrayRails(top=0.0, bottom=0.0, left=0.0, right=0.0)
        array = next(ArrayBuilder.generate_arrays(
            pcb, spacing, rails, allow_array_rotation=False
        ))  # 1x1 array = 1000x800mm

        panel_size = PanelSize(
            name="Small",
            width=600.0,
            height=450.0,
            array_spacing_x=5.0,
            array_spacing_y=5.0,
            border_keepout_x=10.0,
            border_keepout_y=10.0
        )

        panels = list(PanelBuilder.generate_panels(array, panel_size))

        # Should generate no valid panels
        assert len(panels) == 0

    def test_find_best_fit(self):
        """Test finding single best panel"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=0.0, y_spacing=0.0)
        rails = ArrayRails(top=0.0, bottom=0.0, left=0.0, right=0.0)
        array = next(ArrayBuilder.generate_arrays(
            pcb, spacing, rails, allow_array_rotation=False
        ))

        panel_size = PanelSize(
            name="Test",
            width=600.0,
            height=450.0,
            array_spacing_x=0.0,
            array_spacing_y=0.0,
            border_keepout_x=0.0,
            border_keepout_y=0.0
        )

        best = PanelBuilder.find_best_fit(array, panel_size)

        # Should find a panel
        assert best is not None
        assert best.is_valid()

        # Should have maximum arrays (6x5 = 30 for 100x80 PCB on 600x450 panel)
        assert best.array_count_x * best.array_count_y == 30

    def test_find_best_fit_no_valid_raises(self):
        """Test that find_best_fit raises when no valid config"""
        pcb = PCB(width=1000.0, height=800.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=0.0, y_spacing=0.0)
        rails = ArrayRails(top=0.0, bottom=0.0, left=0.0, right=0.0)
        array = next(ArrayBuilder.generate_arrays(
            pcb, spacing, rails, allow_array_rotation=False
        ))

        panel_size = PanelSize(
            name="Small",
            width=600.0,
            height=450.0,
            array_spacing_x=5.0,
            array_spacing_y=5.0,
            border_keepout_x=10.0,
            border_keepout_y=10.0
        )

        with pytest.raises(ValueError, match="No valid panel configuration"):
            PanelBuilder.find_best_fit(array, panel_size)


class TestLayoutOptimizer:
    """Test complete layout optimization"""

    def test_optimize_simple_configuration(self):
        """Test optimization with a simple configuration"""
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
            pcb=pcb,
            array_spacing=spacing,
            array_rails=rails,
            allow_array_rotation=True,
            panel_sizes=[panel_size]
        )

        results = LayoutOptimizer.optimize(config, top_n=10)

        # Should return results
        assert len(results) > 0
        assert len(results) <= 10

        # All should be valid
        for panel in results:
            assert panel.is_valid()

        # Should be sorted by utilization (descending)
        for i in range(len(results) - 1):
            assert results[i].utilization_ratio >= results[i+1].utilization_ratio

    def test_optimize_returns_top_n(self):
        """Test that optimizer returns exactly top_n results (or fewer if not enough)"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=0.0, y_spacing=0.0)
        rails = ArrayRails(top=0.0, bottom=0.0, left=0.0, right=0.0)
        panel_size = PanelSize(
            name="Large",
            width=1000.0,
            height=1000.0,
            array_spacing_x=0.0,
            array_spacing_y=0.0,
            border_keepout_x=0.0,
            border_keepout_y=0.0
        )

        config = Configuration(
            pcb=pcb,
            array_spacing=spacing,
            array_rails=rails,
            allow_array_rotation=False,
            panel_sizes=[panel_size]
        )

        results = LayoutOptimizer.optimize(config, top_n=5)

        # Should return exactly 5 (or fewer if less exist)
        assert len(results) <= 5

    def test_optimize_multiple_panel_sizes(self):
        """Test optimization with multiple panel sizes"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=True)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)

        panel_sizes = [
            PanelSize("Small", 400.0, 300.0, 5.0, 5.0, 10.0, 10.0),
            PanelSize("Medium", 600.0, 450.0, 5.0, 5.0, 10.0, 10.0),
            PanelSize("Large", 800.0, 600.0, 5.0, 5.0, 10.0, 10.0),
        ]

        config = Configuration(
            pcb=pcb,
            array_spacing=spacing,
            array_rails=rails,
            allow_array_rotation=True,
            panel_sizes=panel_sizes
        )

        results = LayoutOptimizer.optimize(config, top_n=10)

        # Should have results from different panel sizes
        panel_names = {panel.panel_size.name for panel in results}
        assert len(panel_names) > 1  # Should use multiple panel sizes

    def test_find_single_best(self):
        """Test finding single best configuration"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=0.0, y_spacing=0.0)
        rails = ArrayRails(top=0.0, bottom=0.0, left=0.0, right=0.0)
        panel_size = PanelSize(
            name="Test",
            width=600.0,
            height=450.0,
            array_spacing_x=0.0,
            array_spacing_y=0.0,
            border_keepout_x=0.0,
            border_keepout_y=0.0
        )

        config = Configuration(
            pcb=pcb,
            array_spacing=spacing,
            array_rails=rails,
            allow_array_rotation=False,
            panel_sizes=[panel_size]
        )

        best = LayoutOptimizer.find_single_best(config)

        # Should return a valid panel
        assert best is not None
        assert best.is_valid()

    def test_find_single_best_no_valid_raises(self):
        """Test that find_single_best raises when PCB too large"""
        pcb = PCB(width=1000.0, height=800.0, allow_rotation=False)
        spacing = ArraySpacing(x_spacing=0.0, y_spacing=0.0)
        rails = ArrayRails(top=0.0, bottom=0.0, left=0.0, right=0.0)
        panel_size = PanelSize(
            name="Small",
            width=600.0,
            height=450.0,
            array_spacing_x=5.0,
            array_spacing_y=5.0,
            border_keepout_x=10.0,
            border_keepout_y=10.0
        )

        config = Configuration(
            pcb=pcb,
            array_spacing=spacing,
            array_rails=rails,
            allow_array_rotation=False,
            panel_sizes=[panel_size]
        )

        with pytest.raises(ValueError, match="No valid panel configuration"):
            LayoutOptimizer.find_single_best(config)

    def test_estimate_search_space(self):
        """Test search space estimation"""
        pcb = PCB(width=100.0, height=80.0, allow_rotation=True)
        spacing = ArraySpacing(x_spacing=3.0, y_spacing=3.0)
        rails = ArrayRails(top=5.0, bottom=5.0, left=5.0, right=5.0)
        panel_size = PanelSize(
            name="Test",
            width=600.0,
            height=450.0,
            array_spacing_x=5.0,
            array_spacing_y=5.0,
            border_keepout_x=10.0,
            border_keepout_y=10.0
        )

        config = Configuration(
            pcb=pcb,
            array_spacing=spacing,
            array_rails=rails,
            allow_array_rotation=True,
            panel_sizes=[panel_size]
        )

        stats = LayoutOptimizer.estimate_search_space(config)

        # Should return statistics
        assert 'total_combinations' in stats
        assert 'arrays_per_panel' in stats
        assert 'panel_count' in stats
        assert stats['panel_count'] == 1
        assert stats['total_combinations'] > 0
