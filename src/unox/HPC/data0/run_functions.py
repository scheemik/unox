import numpy as np

# Necessary to use relative imports (starting with a dot) to avoid
# errors when running on HPC as the `unox` package is not available
from .paths import verify_path
from .load_input import get_npy_from_netcdf


def prepare_input(
    uarr,
    config_path,
    output_metadata,
    split_year = 2019,
):
    """Prepare the input data for the model.

    Get the training data from the input NetCDF dataset as numpy arrays
    and concatenate them along the time dimension.

    Parameters
    ----------
    uarr : unox.uarray
        The dataset of the input NetCDF file.
    split_year : int, optional
        The year at which to split the training and validation data.
        Defaults to 2019.
    
    Returns
    -------
    """
    # Verify the uarray object
    uarr._verify()
    # Get list of years present in the `from_xr` netcdf
    years = uarr._get_years()
    # Create blank lists to hold x and y training data
    xtrain_list = []
    ytrain_list = []
    # If before the split year, add x and y data to train lists
    for year in range(min(years), split_year):
        this_x_train_arr, in_lats, in_lons = get_npy_from_netcdf(uarr.xr, year, config_path, x_or_y='x')
        xtrain_list.append(this_x_train_arr)
        this_y_train_arr, in_lats, in_lons = get_npy_from_netcdf(uarr.xr, year, config_path, x_or_y='y')
        ytrain_list.append(this_y_train_arr)
        output_metadata['train_years']['stage1'].append(year)
    # Check the shapes of the input arrays
    print(f"\tShape of first xtrain file: {xtrain_list[0].shape}")
    print(f"\tShape of first ytrain file: {ytrain_list[0].shape}")
    # Concatenate training data
    xtrain = np.concatenate(xtrain_list, axis=0)
    ytrain = np.concatenate(ytrain_list, axis=0)
    print("After concatenation:")
    print(f"\tShape of xtrain: {xtrain.shape}")
    print(f"\tShape of ytrain: {ytrain.shape}")
    return xtrain, ytrain, output_metadata