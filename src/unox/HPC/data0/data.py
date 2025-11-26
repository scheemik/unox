import xarray as xr
import pandas as pd

# Necessary to use relative imports (starting with a dot) to avoid
# errors when running on HPC as the `unox` package is not available
from .verify_path import verify_path
from .verify import verify_dataset

def get_dataset(
    set_to_get,
    is_input_set=False,
    **kwargs,
):
    """Get the given dataset.

    Parameters
    ----------
    set_to_get : str
        The name of the dataset to get.
    is_input_set : bool, optional
        If True, treat the dataset as an input set.
    **kwargs : keyword arguments

    Returns
    -------
    xr_dataset : xarray.Dataset or xarray.DataArray
        The loaded and verified xarray dataset.
    """
    # If set_to_get is a string, load the dataset
    if isinstance(set_to_get, str):
        if is_input_set:
            # Check whether a file path in the `inputfiles` directory was given
            if 'inputfiles/' not in set_to_get:
                # Assemble the file path
                file_path = f'inputfiles/{set_to_get}/{set_to_get}.nc'
        else:
            file_path = set_to_get
        # Load (and verify) the dataset
        xr_dataset = load_dataset(file_path, **kwargs)
    # If set_to_get is a xarray Dataset or DataArray, verify it
    elif isinstance(set_to_get, xr.Dataset) or isinstance(set_to_get, xr.DataArray):
        xr_dataset = verify_dataset(set_to_get, **kwargs)
    else:
        raise TypeError(f"set_to_get must be string, xr.Dataset, or xr.DataArray. Got {type(set_to_get)}.")
    return xr_dataset

def load_dataset(
    file_path,
    **kwargs,
    ):
    """Load the data from the given filepath into an xarray dataset.

    Verifies the given filepath, ensures the file contains an applicable format,
    and loads the data into an xarray dataset.

    Parameters
    ----------
    file_path : str
        The filepath to the data file to load.
    **kwargs : keyword arguments
        Additional keyword arguments to pass to `csv_to_xr()` and `verify_dataset()`.

    Returns
    -------
    xr_dataset : xarray.Dataset or xarray.DataArray
        The loaded xarray dataset.
    """
    # Verify the filepath
    file_path = vfy.verify_path(file_path)
    # If it is a csv, use custom function to load
    if file_path.endswith('.csv'):
        xr_dataset = csv_to_xr(file_path, **kwargs)
    else:
        xr_dataset = xr.open_dataset(file_path)
    # Verify the dataset
    xr_dataset = verify_dataset(xr_dataset, **kwargs)
    return xr_dataset