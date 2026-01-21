"""Tests for the figures module (overlay_figures, add_secondary_y)."""

from __future__ import annotations

import copy

import numpy as np
import plotly.graph_objects as go
import pytest
import xarray as xr

from xarray_plotly import add_secondary_y, combine_figures, overlay_figures, xpx


class TestCombineFiguresBasic:
    """Basic tests for combine_figures function."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Set up test data."""
        self.da_2d = xr.DataArray(
            np.random.rand(10, 3),
            dims=["time", "cat"],
            coords={"time": np.arange(10), "cat": ["A", "B", "C"]},
            name="value",
        )

    def test_no_overlays_returns_copy(self) -> None:
        """Test that no overlays returns a deep copy of base."""
        base = xpx(self.da_2d).line()
        result = combine_figures(base)

        assert isinstance(result, go.Figure)
        assert len(result.data) == len(base.data)
        # Verify it's a copy, not the same object
        assert result is not base
        assert result.data[0] is not base.data[0]

    def test_combine_two_static_figures(self) -> None:
        """Test combining two static figures."""
        area_fig = xpx(self.da_2d).area()
        line_fig = xpx(self.da_2d).line()

        combined = combine_figures(area_fig, line_fig)

        assert isinstance(combined, go.Figure)
        expected_trace_count = len(area_fig.data) + len(line_fig.data)
        assert len(combined.data) == expected_trace_count

    def test_preserves_base_layout(self) -> None:
        """Test that base figure's layout is preserved."""
        area_fig = xpx(self.da_2d).area(title="My Area Plot")
        line_fig = xpx(self.da_2d).line(title="My Line Plot")

        combined = combine_figures(area_fig, line_fig)

        assert combined.layout.title.text == "My Area Plot"

    def test_multiple_overlays(self) -> None:
        """Test combining multiple overlays."""
        area_fig = xpx(self.da_2d).area()
        line_fig = xpx(self.da_2d).line()
        scatter_fig = xpx(self.da_2d).scatter()

        combined = combine_figures(area_fig, line_fig, scatter_fig)

        expected_count = len(area_fig.data) + len(line_fig.data) + len(scatter_fig.data)
        assert len(combined.data) == expected_count

    def test_overlay_traces_added_in_order(self) -> None:
        """Test that overlay traces are added after base traces."""
        # Create figures with distinguishable y values
        da_1 = xr.DataArray([1, 2, 3], dims=["x"], name="first")
        da_2 = xr.DataArray([10, 20, 30], dims=["x"], name="second")

        fig1 = xpx(da_1).line()
        fig2 = xpx(da_2).line()

        combined = combine_figures(fig1, fig2)

        # First trace should have y values from fig1
        assert list(combined.data[0].y) == [1, 2, 3]
        # Second trace should have y values from fig2
        assert list(combined.data[1].y) == [10, 20, 30]


class TestCombineFiguresFacets:
    """Tests for combine_figures with faceted figures."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Set up test data."""
        self.da_3d = xr.DataArray(
            np.random.rand(10, 3, 2),
            dims=["time", "cat", "facet"],
            coords={
                "time": np.arange(10),
                "cat": ["A", "B", "C"],
                "facet": ["left", "right"],
            },
            name="value",
        )

    def test_matching_facet_structures(self) -> None:
        """Test combining figures with matching facet structures."""
        area_fig = xpx(self.da_3d).area(facet_col="facet")
        line_fig = xpx(self.da_3d).line(facet_col="facet")

        combined = combine_figures(area_fig, line_fig)

        assert isinstance(combined, go.Figure)
        expected_count = len(area_fig.data) + len(line_fig.data)
        assert len(combined.data) == expected_count

    def test_overlay_with_extra_subplots_raises(self) -> None:
        """Test that overlay with extra subplots raises ValueError."""
        # Base without facets
        base = xpx(self.da_3d.isel(facet=0)).line()
        # Overlay with facets
        overlay = xpx(self.da_3d).line(facet_col="facet")

        with pytest.raises(ValueError, match="subplots not present in base"):
            combine_figures(base, overlay)

    def test_preserves_axis_references(self) -> None:
        """Test that traces preserve their xaxis/yaxis references."""
        area_fig = xpx(self.da_3d).area(facet_col="facet")
        line_fig = xpx(self.da_3d).line(facet_col="facet")

        combined = combine_figures(area_fig, line_fig)

        # Collect axis references from both original and combined
        original_axes = set()
        for trace in area_fig.data:
            xaxis = getattr(trace, "xaxis", None) or "x"
            yaxis = getattr(trace, "yaxis", None) or "y"
            original_axes.add((xaxis, yaxis))

        combined_axes = set()
        for trace in combined.data:
            xaxis = getattr(trace, "xaxis", None) or "x"
            yaxis = getattr(trace, "yaxis", None) or "y"
            combined_axes.add((xaxis, yaxis))

        # Combined should have same axis structure
        assert combined_axes == original_axes


class TestCombineFiguresAnimation:
    """Tests for combine_figures with animated figures."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Set up test data."""
        self.da_3d = xr.DataArray(
            np.random.rand(10, 3, 4),
            dims=["x", "cat", "time"],
            coords={
                "x": np.arange(10),
                "cat": ["A", "B", "C"],
                "time": [0, 1, 2, 3],
            },
            name="value",
        )

    def test_matching_frames_merged(self) -> None:
        """Test that matching animation frames are merged correctly."""
        area_fig = xpx(self.da_3d).area(animation_frame="time")
        line_fig = xpx(self.da_3d).line(animation_frame="time")

        combined = combine_figures(area_fig, line_fig)

        assert isinstance(combined, go.Figure)
        # Should have same number of frames
        assert len(combined.frames) == len(area_fig.frames)
        # Each frame should have more data
        for i, frame in enumerate(combined.frames):
            expected_data = len(area_fig.frames[i].data) + len(line_fig.frames[i].data)
            assert len(frame.data) == expected_data

    def test_static_overlay_replicated_to_frames(self) -> None:
        """Test that static overlay is replicated to all animation frames."""
        animated = xpx(self.da_3d).area(animation_frame="time")
        static = xpx(self.da_3d.isel(time=0)).line()

        combined = combine_figures(animated, static)

        # Combined should have all frames from animated figure
        assert len(combined.frames) == len(animated.frames)

        # Each frame should include the static traces
        for frame in combined.frames:
            # Frame data should include both animated and static traces
            expected_count = len(animated.frames[0].data) + len(static.data)
            assert len(frame.data) == expected_count

    def test_animated_overlay_on_static_base_raises(self) -> None:
        """Test that animated overlay on static base raises ValueError."""
        static = xpx(self.da_3d.isel(time=0)).line()
        animated = xpx(self.da_3d).area(animation_frame="time")

        with pytest.raises(ValueError, match="base figure does not"):
            combine_figures(static, animated)

    def test_mismatched_frame_names_raises(self) -> None:
        """Test that mismatched frame names raise ValueError."""
        da1 = xr.DataArray(
            np.random.rand(10, 3),
            dims=["x", "time"],
            coords={"x": np.arange(10), "time": [0, 1, 2]},
        )
        da2 = xr.DataArray(
            np.random.rand(10, 4),
            dims=["x", "time"],
            coords={"x": np.arange(10), "time": [0, 1, 2, 3]},
        )

        fig1 = xpx(da1).line(animation_frame="time")
        fig2 = xpx(da2).line(animation_frame="time")

        with pytest.raises(ValueError, match="frame names don't match"):
            combine_figures(fig1, fig2)

    def test_frame_names_preserved(self) -> None:
        """Test that frame names are preserved in combined figure."""
        area_fig = xpx(self.da_3d).area(animation_frame="time")
        line_fig = xpx(self.da_3d).line(animation_frame="time")

        combined = combine_figures(area_fig, line_fig)

        original_names = {frame.name for frame in area_fig.frames}
        combined_names = {frame.name for frame in combined.frames}
        assert original_names == combined_names


class TestCombineFiguresFacetsAndAnimation:
    """Tests for combine_figures with both facets and animation."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Set up test data."""
        self.da_4d = xr.DataArray(
            np.random.rand(10, 3, 2, 4),
            dims=["x", "cat", "facet", "time"],
            coords={
                "x": np.arange(10),
                "cat": ["A", "B", "C"],
                "facet": ["left", "right"],
                "time": [0, 1, 2, 3],
            },
            name="value",
        )

    def test_facets_and_animation_combined(self) -> None:
        """Test combining figures with both facets and animation."""
        area_fig = xpx(self.da_4d).area(facet_col="facet", animation_frame="time")
        line_fig = xpx(self.da_4d).line(facet_col="facet", animation_frame="time")

        combined = combine_figures(area_fig, line_fig)

        assert isinstance(combined, go.Figure)
        # Check trace count
        expected_traces = len(area_fig.data) + len(line_fig.data)
        assert len(combined.data) == expected_traces
        # Check frame count
        assert len(combined.frames) == len(area_fig.frames)

    def test_static_overlay_on_animated_faceted_base(self) -> None:
        """Test static overlay replicated on animated faceted base."""
        animated = xpx(self.da_4d).area(facet_col="facet", animation_frame="time")
        static = xpx(self.da_4d.isel(time=0)).line(facet_col="facet")

        combined = combine_figures(animated, static)

        # Should have same frames as animated
        assert len(combined.frames) == len(animated.frames)
        # Each frame should have combined trace count
        for frame in combined.frames:
            expected = len(animated.frames[0].data) + len(static.data)
            assert len(frame.data) == expected


class TestCombineFiguresDeepCopy:
    """Tests to ensure combine_figures creates deep copies."""

    def test_base_not_modified(self) -> None:
        """Test that base figure is not modified."""
        da = xr.DataArray(np.random.rand(10, 3), dims=["x", "cat"])
        base = xpx(da).area()
        original_trace_count = len(base.data)
        original_title = copy.deepcopy(base.layout.title)

        overlay = xpx(da).line()
        _ = combine_figures(base, overlay)

        # Base should be unchanged
        assert len(base.data) == original_trace_count
        assert base.layout.title == original_title

    def test_overlay_not_modified(self) -> None:
        """Test that overlay figure is not modified."""
        da = xr.DataArray(np.random.rand(10, 3), dims=["x", "cat"])
        base = xpx(da).area()
        overlay = xpx(da).line()
        original_trace_count = len(overlay.data)

        _ = combine_figures(base, overlay)

        # Overlay should be unchanged
        assert len(overlay.data) == original_trace_count

    def test_combined_traces_independent(self) -> None:
        """Test that combined traces are independent of originals."""
        da = xr.DataArray(np.random.rand(10, 3), dims=["x", "cat"])
        base = xpx(da).area()
        overlay = xpx(da).line()

        combined = combine_figures(base, overlay)

        # Modify combined figure
        combined.data[0].name = "modified"

        # Originals should be unchanged
        assert base.data[0].name != "modified"


class TestOverlayFiguresAlias:
    """Test that overlay_figures and combine_figures are equivalent."""

    def test_overlay_figures_is_combine_figures(self) -> None:
        """Test that overlay_figures is the same function as combine_figures."""
        assert overlay_figures is combine_figures

    def test_overlay_figures_works(self) -> None:
        """Test that overlay_figures works correctly."""
        da = xr.DataArray(np.random.rand(10, 3), dims=["x", "cat"])
        area_fig = xpx(da).area()
        line_fig = xpx(da).line()

        combined = overlay_figures(area_fig, line_fig)

        assert isinstance(combined, go.Figure)
        expected_count = len(area_fig.data) + len(line_fig.data)
        assert len(combined.data) == expected_count


class TestAddSecondaryYBasic:
    """Basic tests for add_secondary_y function."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Set up test data."""
        self.temp = xr.DataArray(
            [20, 22, 25, 23, 21],
            dims=["time"],
            coords={"time": [0, 1, 2, 3, 4]},
            name="Temperature",
        )
        self.precip = xr.DataArray(
            [0, 5, 12, 2, 8],
            dims=["time"],
            coords={"time": [0, 1, 2, 3, 4]},
            name="Precipitation",
        )

    def test_creates_secondary_y_axis(self) -> None:
        """Test that secondary y-axis is created."""
        temp_fig = xpx(self.temp).line()
        precip_fig = xpx(self.precip).bar()

        combined = add_secondary_y(temp_fig, precip_fig)

        assert isinstance(combined, go.Figure)
        assert combined.layout.yaxis2 is not None
        assert combined.layout.yaxis2.side == "right"
        assert combined.layout.yaxis2.overlaying == "y"

    def test_secondary_traces_use_y2(self) -> None:
        """Test that secondary figure traces are assigned to y2."""
        temp_fig = xpx(self.temp).line()
        precip_fig = xpx(self.precip).bar()

        combined = add_secondary_y(temp_fig, precip_fig)

        # First trace (from temp_fig) should use default y
        assert combined.data[0].yaxis is None or combined.data[0].yaxis == "y"
        # Second trace (from precip_fig) should use y2
        assert combined.data[1].yaxis == "y2"

    def test_preserves_base_layout(self) -> None:
        """Test that base figure's layout is preserved."""
        temp_fig = xpx(self.temp).line(title="My Temperature Plot")
        precip_fig = xpx(self.precip).bar()

        combined = add_secondary_y(temp_fig, precip_fig)

        assert combined.layout.title.text == "My Temperature Plot"

    def test_total_trace_count(self) -> None:
        """Test that all traces from both figures are included."""
        temp_fig = xpx(self.temp).line()
        precip_fig = xpx(self.precip).bar()

        combined = add_secondary_y(temp_fig, precip_fig)

        expected_count = len(temp_fig.data) + len(precip_fig.data)
        assert len(combined.data) == expected_count

    def test_secondary_y_title_from_secondary_figure(self) -> None:
        """Test that secondary y-axis title comes from secondary figure."""
        temp_fig = xpx(self.temp).line()
        precip_fig = xpx(self.precip).bar()
        # Plotly Express sets y-axis title based on the data

        combined = add_secondary_y(temp_fig, precip_fig)

        # The secondary y-axis title should be set
        assert combined.layout.yaxis2.title is not None

    def test_custom_secondary_y_title(self) -> None:
        """Test that custom secondary y-axis title can be provided."""
        temp_fig = xpx(self.temp).line()
        precip_fig = xpx(self.precip).bar()

        combined = add_secondary_y(temp_fig, precip_fig, secondary_y_title="Rain (mm)")

        assert combined.layout.yaxis2.title.text == "Rain (mm)"


class TestAddSecondaryYFacetsError:
    """Tests for add_secondary_y error handling with facets."""

    def test_base_with_facets_raises(self) -> None:
        """Test that base figure with facets raises ValueError."""
        da = xr.DataArray(
            np.random.rand(10, 2),
            dims=["time", "facet"],
            coords={"time": np.arange(10), "facet": ["A", "B"]},
        )
        base = xpx(da).line(facet_col="facet")
        secondary = xpx(da.isel(facet=0)).bar()

        with pytest.raises(ValueError, match="Base figure has facets"):
            add_secondary_y(base, secondary)

    def test_secondary_with_facets_raises(self) -> None:
        """Test that secondary figure with facets raises ValueError."""
        da = xr.DataArray(
            np.random.rand(10, 2),
            dims=["time", "facet"],
            coords={"time": np.arange(10), "facet": ["A", "B"]},
        )
        base = xpx(da.isel(facet=0)).line()
        secondary = xpx(da).bar(facet_col="facet")

        with pytest.raises(ValueError, match="Secondary figure has facets"):
            add_secondary_y(base, secondary)


class TestAddSecondaryYAnimation:
    """Tests for add_secondary_y with animated figures."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Set up test data."""
        self.da_2d = xr.DataArray(
            np.random.rand(10, 4),
            dims=["x", "time"],
            coords={"x": np.arange(10), "time": [0, 1, 2, 3]},
            name="value",
        )

    def test_matching_animation_frames(self) -> None:
        """Test add_secondary_y with matching animation frames."""
        fig1 = xpx(self.da_2d).line(animation_frame="time")
        fig2 = xpx(self.da_2d).bar(animation_frame="time")

        combined = add_secondary_y(fig1, fig2)

        assert len(combined.frames) == len(fig1.frames)
        # Verify frame names match
        for orig, comb in zip(fig1.frames, combined.frames, strict=False):
            assert orig.name == comb.name

    def test_static_secondary_on_animated_base(self) -> None:
        """Test static secondary replicated to all animation frames."""
        animated = xpx(self.da_2d).line(animation_frame="time")
        static = xpx(self.da_2d.isel(time=0)).bar()

        combined = add_secondary_y(animated, static)

        assert len(combined.frames) == len(animated.frames)
        # Each frame should have traces from both figures
        for frame in combined.frames:
            expected = len(animated.frames[0].data) + len(static.data)
            assert len(frame.data) == expected

    def test_animated_secondary_on_static_base_raises(self) -> None:
        """Test that animated secondary on static base raises ValueError."""
        static = xpx(self.da_2d.isel(time=0)).line()
        animated = xpx(self.da_2d).bar(animation_frame="time")

        with pytest.raises(ValueError, match="base figure does not"):
            add_secondary_y(static, animated)

    def test_mismatched_animation_frames_raises(self) -> None:
        """Test that mismatched animation frames raise ValueError."""
        da1 = xr.DataArray(
            np.random.rand(10, 3),
            dims=["x", "time"],
            coords={"x": np.arange(10), "time": [0, 1, 2]},
        )
        da2 = xr.DataArray(
            np.random.rand(10, 4),
            dims=["x", "time"],
            coords={"x": np.arange(10), "time": [0, 1, 2, 3]},
        )

        fig1 = xpx(da1).line(animation_frame="time")
        fig2 = xpx(da2).bar(animation_frame="time")

        with pytest.raises(ValueError, match="frame names don't match"):
            add_secondary_y(fig1, fig2)


class TestAddSecondaryYDeepCopy:
    """Tests to ensure add_secondary_y creates deep copies."""

    def test_base_not_modified(self) -> None:
        """Test that base figure is not modified."""
        da = xr.DataArray([1, 2, 3, 4, 5], dims=["x"])
        base = xpx(da).line()
        original_trace_count = len(base.data)

        secondary = xpx(da).bar()
        _ = add_secondary_y(base, secondary)

        assert len(base.data) == original_trace_count
        # Base should not have yaxis2 (check via to_plotly_json)
        assert "yaxis2" not in base.layout.to_plotly_json()

    def test_secondary_not_modified(self) -> None:
        """Test that secondary figure is not modified."""
        da = xr.DataArray([1, 2, 3, 4, 5], dims=["x"])
        base = xpx(da).line()
        secondary = xpx(da).bar()
        original_yaxis = secondary.data[0].yaxis

        _ = add_secondary_y(base, secondary)

        # Secondary traces should still use original yaxis
        assert secondary.data[0].yaxis == original_yaxis
