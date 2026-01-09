"""
xarray_plotly: Interactive Plotly Express plotting for xarray.

This package provides a `plotly` accessor for xarray DataArray objects,
enabling interactive visualization with Plotly Express.

Features
--------
- **Interactive plots**: Zoom, pan, hover, toggle traces
- **Automatic dimension assignment**: Dimensions fill slots (x, color, facet) by position
- **Multiple plot types**: line, bar, area, scatter, box, imshow
- **Faceting and animation**: Built-in subplot grids and animated plots
- **Customizable**: Returns Plotly Figure objects for further modification

Usage
-----
Accessor style::

    import xarray_plotly
    fig = da.plotly.line()

Function style (recommended for IDE completion)::

    from xarray_plotly import xpx
    fig = xpx(da).line()

Examples
--------
>>> import xarray as xr
>>> import numpy as np
>>> from xarray_plotly import xpx

>>> da = xr.DataArray(
...     np.random.rand(10, 3, 2),
...     dims=["time", "city", "scenario"],
... )

>>> # Auto-assignment: time->x, city->color, scenario->facet_col
>>> fig = xpx(da).line()

>>> # Explicit assignment
>>> fig = xpx(da).line(x="time", color="scenario", facet_col="city")

>>> # Skip a slot with None
>>> fig = xpx(da).line(color=None)
"""

from importlib.metadata import version

from xarray import DataArray, register_dataarray_accessor

from xarray_plotly import config
from xarray_plotly.accessor import DataArrayPlotlyAccessor
from xarray_plotly.common import SLOT_ORDERS, auto

__all__ = [
    "SLOT_ORDERS",
    "DataArrayPlotlyAccessor",
    "auto",
    "config",
    "xpx",
]


def xpx(da: DataArray) -> DataArrayPlotlyAccessor:
    """
    Get the plotly accessor for a DataArray with full IDE code completion.

    This is an alternative to `da.plotly` that provides proper type hints
    and code completion in IDEs.

    Parameters
    ----------
    da : DataArray
        The DataArray to plot.

    Returns
    -------
    DataArrayPlotlyAccessor
        The accessor with plotting methods.

    Examples
    --------
    >>> from xarray_plotly import xpx
    >>> fig = xpx(da).line()  # Full code completion works here
    """
    return DataArrayPlotlyAccessor(da)


__version__ = version("xarray_plotly")

# Register the accessor
register_dataarray_accessor("plotly")(DataArrayPlotlyAccessor)
