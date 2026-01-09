"""Type definitions for xarray_plotly."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from xarray_plotly.accessor import DataArrayPlotlyAccessor


@runtime_checkable
class DataArrayWithPlotly(Protocol):
    """Protocol for DataArray with plotly accessor.

    Use this for type hints when you need the plotly accessor to be recognized:

        from xarray_plotly import DataArrayWithPlotly

        def my_function(da: DataArrayWithPlotly) -> None:
            fig = da.plotly.line()  # Properly typed!
    """

    @property
    def plotly(self) -> DataArrayPlotlyAccessor: ...

    # Add common DataArray methods/properties for better compatibility
    @property
    def dims(self) -> tuple[str, ...]: ...

    @property
    def name(self) -> str | None: ...
