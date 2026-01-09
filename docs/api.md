# API Reference

## xpx Function

The recommended way to use xarray_plotly with full IDE code completion:

```python
from xarray_plotly import xpx

fig = xpx(da).line()
```

::: xarray_plotly.xpx
    options:
      show_root_heading: true

## Accessor

The accessor style (`da.plotly.line()`) works but doesn't provide IDE code completion.

::: xarray_plotly.accessor.DataArrayPlotlyAccessor
    options:
      show_root_heading: true
      members:
        - line
        - bar
        - area
        - scatter
        - box
        - imshow

## Plotting Functions

::: xarray_plotly.plotting
    options:
      show_root_heading: true
      members:
        - line
        - bar
        - area
        - scatter
        - box
        - imshow

## Common Utilities

::: xarray_plotly.common
    options:
      show_root_heading: true
      members:
        - auto
        - SLOT_ORDERS
        - assign_slots
