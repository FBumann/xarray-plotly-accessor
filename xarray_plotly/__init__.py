"""Interactive Plotly Express plotting for xarray.

This package provides a `plotly` accessor for xarray DataArray and Dataset objects,
enabling interactive visualization with Plotly Express.

Features:
    - **Interactive plots**: Zoom, pan, hover, toggle traces
    - **Automatic dimension assignment**: Dimensions fill slots (x, color, facet) by position
    - **Multiple plot types**: line, bar, area, scatter, box, imshow
    - **Dataset support**: Plot all variables at once with "variable" dimension
    - **Faceting and animation**: Built-in subplot grids and animated plots
    - **Customizable**: Returns Plotly Figure objects for further modification

Usage:
Mos    Recommended::

        import xarray_plotly as xpx

        fig = xpx(da).line()           # Create plots
        combined = xpx.overlay(fig1, fig2)  # Use helper functions

    Accessor style::

        import xarray_plotly
        fig = da.plotly.line()

Example:
    ```python
    import xarray as xr
    import numpy as np
    import xarray_plotly as xpx

    da = xr.DataArray(
        np.random.rand(10, 3, 2),
        dims=["time", "city", "scenario"],
    )
    fig = xpx(da).line()  # Auto: time->x, city->color, scenario->facet_col

    # Combine figures
    area = xpx(da).area()
    line = xpx(da).line()
    combined = xpx.overlay(area, line)
    ```
"""

from __future__ import annotations

import sys
import types
from importlib.metadata import version
from typing import TYPE_CHECKING, overload

from xarray import DataArray, Dataset, register_dataarray_accessor, register_dataset_accessor

from xarray_plotly import config
from xarray_plotly.accessor import DataArrayPlotlyAccessor, DatasetPlotlyAccessor
from xarray_plotly.common import SLOT_ORDERS, auto
from xarray_plotly.figures import (
    add_secondary_y,
    overlay,
    update_traces,
)

__all__ = [
    "SLOT_ORDERS",
    "add_secondary_y",
    "auto",
    "config",
    "overlay",
    "update_traces",
]

__version__ = version("xarray_plotly")

# Register the accessors
register_dataarray_accessor("plotly")(DataArrayPlotlyAccessor)
register_dataset_accessor("plotly")(DatasetPlotlyAccessor)


class _CallableModule(types.ModuleType):
    """A module that can be called as a function.

    Enables the pattern::

        import xarray_plotly as xpx
        fig = xpx(da).line()        # Call module as function
        fig = xpx.overlay(a, b)     # Access module attributes
    """

    @overload
    def __call__(self, data: DataArray) -> DataArrayPlotlyAccessor: ...

    @overload
    def __call__(self, data: Dataset) -> DatasetPlotlyAccessor: ...

    def __call__(
        self, data: DataArray | Dataset
    ) -> DataArrayPlotlyAccessor | DatasetPlotlyAccessor:
        """Get the plotly accessor for a DataArray or Dataset.

        Args:
            data: The DataArray or Dataset to plot.

        Returns:
            The accessor with plotting methods (line, bar, area, scatter, box, imshow, pie).

        Example:
            ```python
            import xarray_plotly as xpx

            fig = xpx(da).line()
            fig = xpx(ds).line(var="temperature")
            ```
        """
        if isinstance(data, Dataset):
            return DatasetPlotlyAccessor(data)
        return DataArrayPlotlyAccessor(data)


# Make the module callable
sys.modules[__name__].__class__ = _CallableModule

# For type checking, expose the call signature
if TYPE_CHECKING:

    @overload
    def __call__(data: DataArray) -> DataArrayPlotlyAccessor: ...

    @overload
    def __call__(data: Dataset) -> DatasetPlotlyAccessor: ...

    def __call__(
        data: DataArray | Dataset,
    ) -> DataArrayPlotlyAccessor | DatasetPlotlyAccessor: ...
