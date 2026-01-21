"""
Helper functions for combining and manipulating Plotly figures.
"""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import plotly.graph_objects as go


def _get_subplot_axes(fig: go.Figure) -> set[tuple[str, str]]:
    """Extract (xaxis, yaxis) pairs from figure traces.

    Args:
        fig: A Plotly figure.

    Returns:
        Set of (xaxis, yaxis) tuples, e.g., {('x', 'y'), ('x2', 'y2')}.
    """
    axes_pairs = set()
    for trace in fig.data:
        xaxis = getattr(trace, "xaxis", None) or "x"
        yaxis = getattr(trace, "yaxis", None) or "y"
        axes_pairs.add((xaxis, yaxis))
    return axes_pairs


def _validate_compatible_structure(base: go.Figure, overlay: go.Figure) -> None:
    """Validate that overlay's subplot structure is compatible with base.

    Args:
        base: The base figure.
        overlay: The overlay figure to check.

    Raises:
        ValueError: If overlay has subplots not present in base.
    """
    base_axes = _get_subplot_axes(base)
    overlay_axes = _get_subplot_axes(overlay)

    extra_axes = overlay_axes - base_axes
    if extra_axes:
        raise ValueError(
            f"Overlay figure has subplots not present in base figure: {extra_axes}. "
            "Ensure both figures have the same facet structure."
        )


def _validate_animation_compatibility(base: go.Figure, overlay: go.Figure) -> None:
    """Validate animation frame compatibility between base and overlay.

    Args:
        base: The base figure.
        overlay: The overlay figure to check.

    Raises:
        ValueError: If overlay has animation but base doesn't, or frame names don't match.
    """
    base_has_frames = bool(base.frames)
    overlay_has_frames = bool(overlay.frames)

    if overlay_has_frames and not base_has_frames:
        raise ValueError(
            "Overlay figure has animation frames but base figure does not. "
            "Cannot add animated overlay to static base figure."
        )

    if base_has_frames and overlay_has_frames:
        base_frame_names = {frame.name for frame in base.frames}
        overlay_frame_names = {frame.name for frame in overlay.frames}

        if base_frame_names != overlay_frame_names:
            missing_in_overlay = base_frame_names - overlay_frame_names
            extra_in_overlay = overlay_frame_names - base_frame_names
            msg = "Animation frame names don't match between base and overlay."
            if missing_in_overlay:
                msg += f" Missing in overlay: {missing_in_overlay}."
            if extra_in_overlay:
                msg += f" Extra in overlay: {extra_in_overlay}."
            raise ValueError(msg)


def _merge_frames(
    base: go.Figure,
    overlays: list[go.Figure],
    base_trace_count: int,
    overlay_trace_counts: list[int],
) -> list:
    """Merge animation frames from base and overlay figures.

    Args:
        base: The base figure with animation frames.
        overlays: List of overlay figures (may or may not have frames).
        base_trace_count: Number of traces in the base figure.
        overlay_trace_counts: Number of traces in each overlay figure.

    Returns:
        List of merged frames.
    """
    import plotly.graph_objects as go

    merged_frames = []

    for base_frame in base.frames:
        frame_name = base_frame.name
        merged_data = list(base_frame.data)

        for overlay, _overlay_trace_count in zip(overlays, overlay_trace_counts, strict=False):
            if overlay.frames:
                # Find matching frame in overlay
                overlay_frame = next((f for f in overlay.frames if f.name == frame_name), None)
                if overlay_frame:
                    merged_data.extend(overlay_frame.data)
            else:
                # Static overlay: replicate traces to this frame
                merged_data.extend(overlay.data)

        merged_frames.append(
            go.Frame(
                data=merged_data,
                name=frame_name,
                traces=list(range(base_trace_count + sum(overlay_trace_counts))),
            )
        )

    return merged_frames


def overlay_figures(base: go.Figure, *overlays: go.Figure) -> go.Figure:
    """Overlay multiple Plotly figures on the same axes.

    Creates a new figure with the base figure's layout, sliders, and buttons,
    with all overlay traces added on top. Correctly handles faceted figures
    and animation frames.

    Args:
        base: The base figure whose layout is preserved.
        *overlays: One or more figures to overlay on the base.

    Returns:
        A new combined figure.

    Raises:
        ValueError: If overlay has subplots not in base, animation frames don't match,
            or overlay has animation but base doesn't.

    Example:
        >>> import numpy as np
        >>> import xarray as xr
        >>> from xarray_plotly import xpx, overlay_figures
        >>>
        >>> da = xr.DataArray(np.random.rand(10, 3), dims=["time", "cat"])
        >>> area_fig = xpx(da).area()
        >>> line_fig = xpx(da).line()
        >>> combined = overlay_figures(area_fig, line_fig)
        >>>
        >>> # With animation
        >>> da3d = xr.DataArray(np.random.rand(10, 3, 4), dims=["x", "cat", "time"])
        >>> area = xpx(da3d).area(animation_frame="time")
        >>> line = xpx(da3d).line(animation_frame="time")
        >>> combined = overlay_figures(area, line)
    """
    import plotly.graph_objects as go

    if not overlays:
        # No overlays: return a deep copy of base
        return copy.deepcopy(base)

    # Validate all overlays
    for overlay in overlays:
        _validate_compatible_structure(base, overlay)
        _validate_animation_compatibility(base, overlay)

    # Create new figure with base's layout
    combined = go.Figure(layout=copy.deepcopy(base.layout))

    # Add all traces from base
    for trace in base.data:
        combined.add_trace(copy.deepcopy(trace))

    # Add all traces from overlays
    for overlay in overlays:
        for trace in overlay.data:
            combined.add_trace(copy.deepcopy(trace))

    # Handle animation frames
    if base.frames:
        base_trace_count = len(base.data)
        overlay_trace_counts = [len(overlay.data) for overlay in overlays]
        merged_frames = _merge_frames(base, list(overlays), base_trace_count, overlay_trace_counts)
        combined.frames = merged_frames

    return combined


# Backwards compatibility alias
combine_figures = overlay_figures


def add_secondary_y(
    base: go.Figure,
    secondary: go.Figure,
    *,
    secondary_y_title: str | None = None,
) -> go.Figure:
    """Add a secondary y-axis with traces from another figure.

    Creates a new figure with the base figure's layout and a secondary y-axis
    on the right side. All traces from the secondary figure are plotted against
    the secondary y-axis.

    Args:
        base: The base figure (left y-axis).
        secondary: The figure whose traces use the secondary y-axis (right).
        secondary_y_title: Optional title for the secondary y-axis.
            If not provided, uses the secondary figure's y-axis title.

    Returns:
        A new figure with both primary and secondary y-axes.

    Raises:
        ValueError: If either figure has facets (subplots), or if animation
            frames don't match.

    Example:
        >>> import numpy as np
        >>> import xarray as xr
        >>> from xarray_plotly import xpx, add_secondary_y
        >>>
        >>> # Two variables with different scales
        >>> temp = xr.DataArray([20, 22, 25, 23], dims=["time"], name="Temperature (°C)")
        >>> precip = xr.DataArray([0, 5, 12, 2], dims=["time"], name="Precipitation (mm)")
        >>>
        >>> temp_fig = xpx(temp).line()
        >>> precip_fig = xpx(precip).bar()
        >>> combined = add_secondary_y(temp_fig, precip_fig)
    """
    import plotly.graph_objects as go

    # Check for facets - not supported with secondary y
    base_axes = _get_subplot_axes(base)
    secondary_axes = _get_subplot_axes(secondary)

    if len(base_axes) > 1 or base_axes != {("x", "y")}:
        raise ValueError(
            "Base figure has facets (subplots). Secondary y-axis is not supported "
            "with faceted figures."
        )
    if len(secondary_axes) > 1 or secondary_axes != {("x", "y")}:
        raise ValueError(
            "Secondary figure has facets (subplots). Secondary y-axis is not supported "
            "with faceted figures."
        )

    # Validate animation compatibility
    _validate_animation_compatibility(base, secondary)

    # Create new figure with base's layout
    combined = go.Figure(layout=copy.deepcopy(base.layout))

    # Add all traces from base (primary y-axis)
    for trace in base.data:
        combined.add_trace(copy.deepcopy(trace))

    # Add all traces from secondary, assigned to y2
    for trace in secondary.data:
        trace_copy = copy.deepcopy(trace)
        trace_copy.yaxis = "y2"
        combined.add_trace(trace_copy)

    # Configure secondary y-axis
    y2_title = secondary_y_title
    if y2_title is None and secondary.layout.yaxis and secondary.layout.yaxis.title:
        y2_title = secondary.layout.yaxis.title.text

    combined.update_layout(
        yaxis2={
            "title": y2_title,
            "overlaying": "y",
            "side": "right",
        },
    )

    # Handle animation frames
    if base.frames:
        merged_frames = _merge_secondary_y_frames(base, secondary)
        combined.frames = merged_frames

    return combined


def _merge_secondary_y_frames(base: go.Figure, secondary: go.Figure) -> list:
    """Merge animation frames for secondary y-axis combination.

    Args:
        base: The base figure with animation frames.
        secondary: The secondary figure (may or may not have frames).

    Returns:
        List of merged frames with secondary traces assigned to y2.
    """
    import plotly.graph_objects as go

    merged_frames = []
    base_trace_count = len(base.data)
    secondary_trace_count = len(secondary.data)

    for base_frame in base.frames:
        frame_name = base_frame.name
        merged_data = list(base_frame.data)

        if secondary.frames:
            # Find matching frame in secondary
            secondary_frame = next((f for f in secondary.frames if f.name == frame_name), None)
            if secondary_frame:
                # Add secondary frame data with y2 assignment
                for trace_data in secondary_frame.data:
                    trace_copy = copy.deepcopy(trace_data)
                    if hasattr(trace_copy, "yaxis"):
                        trace_copy.yaxis = "y2"
                    merged_data.append(trace_copy)
        else:
            # Static secondary: replicate traces to this frame
            for trace in secondary.data:
                trace_copy = copy.deepcopy(trace)
                if hasattr(trace_copy, "yaxis"):
                    trace_copy.yaxis = "y2"
                merged_data.append(trace_copy)

        merged_frames.append(
            go.Frame(
                data=merged_data,
                name=frame_name,
                traces=list(range(base_trace_count + secondary_trace_count)),
            )
        )

    return merged_frames
