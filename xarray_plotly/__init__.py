"""
xarray_plotly: Interactive Plotly Express plotting accessor for xarray.

This package provides a `plotly` accessor for xarray DataArray objects that
enables interactive plotting using Plotly Express.

Examples
--------
>>> import xarray as xr
>>> import numpy as np
>>> import xarray_plotly  # registers the accessor

>>> da = xr.DataArray(
...     np.random.rand(10, 3, 2),
...     dims=["time", "city", "scenario"],
... )

>>> # Auto-assignment: time->x, city->color, scenario->facet_col
>>> fig = da.plotly.line()

>>> # Explicit assignment
>>> fig = da.plotly.line(x="time", color="scenario", facet_col="city")

>>> # Skip a slot
>>> fig = da.plotly.line(color=None)  # time->x, city->facet_col, scenario->facet_row
"""

from typing import TYPE_CHECKING

from xarray import DataArray, register_dataarray_accessor

from xarray_plotly._typing import DataArrayWithPlotly
from xarray_plotly.accessor import DataArrayPlotlyAccessor
from xarray_plotly.common import SLOT_ORDERS, auto

__all__ = [
    "SLOT_ORDERS",
    "DataArray",
    "DataArrayPlotlyAccessor",
    "DataArrayWithPlotly",
    "auto",
]

from importlib.metadata import version

__version__ = version("xarray_plotly")

# Register the accessor
register_dataarray_accessor("plotly")(DataArrayPlotlyAccessor)  # type: ignore[no-untyped-call]

# IDE code completion support
# This block is only evaluated by type checkers and IDEs, not at runtime
if TYPE_CHECKING:
    from xarray import DataArray as _DataArray

    class _DataArrayPlotlyExtension:
        @property
        def plotly(self) -> DataArrayPlotlyAccessor: ...

    class DataArray(_DataArray, _DataArrayPlotlyExtension):  # type: ignore[no-redef,no-untyped-call]
        ...
