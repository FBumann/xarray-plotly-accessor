"""Type stubs for xarray_plotly - provides IDE autocompletion."""

from xarray import DataArray as _DataArray

from xarray_plotly._typing import DataArrayWithPlotly as DataArrayWithPlotly
from xarray_plotly.accessor import DataArrayPlotlyAccessor as DataArrayPlotlyAccessor
from xarray_plotly.common import SLOT_ORDERS as SLOT_ORDERS
from xarray_plotly.common import auto as auto

__version__: str

# Augment xarray.DataArray with plotly accessor for IDE autocompletion
class DataArray(_DataArray):  # type: ignore[no-untyped-call]
    @property
    def plotly(self) -> DataArrayPlotlyAccessor: ...
