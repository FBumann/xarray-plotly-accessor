# xarray_plotly

**Interactive Plotly Express plotting accessor for xarray**

::: xarray_plotly
    options:
      show_root_heading: false
      show_docstring_description: true
      show_docstring_examples: true
      members: false

## Installation

```bash
pip install xarray_plotly
```

## Usage

```python
import xarray as xr
import numpy as np
import xarray_plotly  # registers the accessor

da = xr.DataArray(
    np.random.randn(100, 3).cumsum(axis=0),
    dims=["time", "city"],
    coords={"time": np.arange(100), "city": ["NYC", "LA", "Chicago"]},
)

# Accessor style
fig = da.plotly.line()

# Or with xpx() for IDE code completion
from xarray_plotly import xpx
fig = xpx(da).line()
```

## Next Steps

- [Getting Started](getting-started.ipynb) - Interactive tutorial
- [Plot Types](examples/plot-types.ipynb) - All available plot types
- [Advanced Usage](examples/advanced.ipynb) - Configuration and customization
- [API Reference](api.md) - Full API documentation
