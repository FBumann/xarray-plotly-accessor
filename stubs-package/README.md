# xarray_plotly_stubs

Type stubs for [xarray_plotly](https://github.com/felix/xarray_plotly).

## Recommended Approach: Protocol

For most use cases, use the `DataArrayWithPlotly` protocol instead of this stubs package:

```python
from xarray_plotly import DataArrayWithPlotly

def plot_data(da: DataArrayWithPlotly) -> None:
    fig = da.plotly.line()  # Properly typed!
```

This works without any additional packages and provides proper type checking.

## Stubs Package (Advanced)

If you want direct `da.plotly` typing without using the protocol, install this stubs package:

```bash
pip install xarray_plotly_stubs
```

**Warning**: These stubs may shadow xarray's built-in types in some type checkers. Use with caution.
