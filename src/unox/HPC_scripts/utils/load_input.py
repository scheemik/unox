import numpy as np
import xarray as xr

def get_npy_from_netcdf(
    netcdf,
    year,
    x_or_y=None,
    var=None,
    ):
    """ 
    Extract a numpy array for a specific year (and variable if requested) from a netcdf file.

    Parameters
    ----------
    netcdf : str or xr.Dataset
        Path to the netcdf file or an xarray Dataset.
    year : int
        The year for which to extract the data.
    x_or_y : str, optional
        If 'x', return the stage 1 x variables, if 'x2', return the stage 2 x variables, 
        if 'y', return the y variables. If None, return all variables.
    var : str, optional
        The variable to extract from the netcdf file. Overrides the `x_or_y` argument. 
        If None, all variables are returned.

    Returns
    -------
    np.ndarray
        The extracted data as a numpy array.
    
    Examples
    --------
    >>> input_set = 'my_inputs'
    >>> arr = get_npy_from_netcdf(f'inputfiles/{input_set}/{input_set}.nc', 2019, 'x')
    >>> type(arr)
    <class 'numpy.ndarray'>
    >>> arr.shape
    (364, 56, 120, 9)
    """
    # Check if netcdf is a string (file path) or an xarray Dataset
    if isinstance(netcdf, str):
        # Verify the netcdf file path
        # netcdf_filepath = unox.verify_path(netcdf)
        # Load the netcdf file
        xr_dataset = xr.load_dataset(netcdf)
    elif isinstance(netcdf, xr.Dataset):
        xr_dataset = netcdf
    else:
        raise TypeError(f'netcdf must be a file path (str) or an xarray.Dataset, got {type(netcdf)}.')
    # Verify the dataset
    # xr_dataset = udata.verify_dataset(xr_dataset)
    # Select the data for the specified year
    data_for_year = xr_dataset.sel(time=slice(f'{year}-01-01', f'{year}-12-31'))
    if isinstance(var, type(None)):
        if x_or_y in ['x', 'x2']:
            # Get the list of x variables from the `x_vars` attribute
            x_vars = xr_dataset.attrs.get('x_vars')
            if x_or_y == 'x':
                # x_vars = xr_dataset.attrs.get('x1_vars')
                x_vars = [
                    'no2',
                    'no2_tm1',
                    'u10',
                    'v10',
                    'blh',
                    'sp',
                    'skt',
                    't2m',
                    'ssrd',
                ]
            elif x_or_y == 'x2':
                # Get the stage 2 cutoff
                stage_2_cutoff = xr_dataset.attrs.get('stage_2_cutoff')
                if stage_2_cutoff > year:
                    raise ValueError(f"Stage 2 data not available for year {year} (cutoff is {stage_2_cutoff}).")
                # x_vars = xr_dataset.attrs.get('x2_vars')
                x_vars = [
                    'no2_s2',
                    'no2_s2_tm1',
                    'u10',
                    'v10',
                    'blh',
                    'sp',
                    'skt',
                    't2m',
                    'ssrd',
                ]
            # Grab just the x variables for the dataset
            # data_for_year = data_for_year[x_vars]
            # Drop all nan values
            data_for_year = data_for_year.dropna(dim='time', how='all')
            # Convert the entire dataset to a numpy array by looping over x_vars
            list_of_x_arrs = []
            for i in range(len(x_vars)):
                this_arr = get_npy_from_netcdf(data_for_year, year, var=x_vars[i])
                list_of_x_arrs.append(this_arr)
            # Stack the arrays together along a new axis in last place
            data_array = np.stack(tuple(list_of_x_arrs), axis=-1)
        elif x_or_y == 'y':
            # Get the y variable from the `y_var` attribute
            y_var = xr_dataset.attrs.get('y_var')
            if y_var is None:
                raise ValueError("The dataset does not have a 'y_var' attribute.")
            return get_npy_from_netcdf(data_for_year, year, var=y_var)
        else:
            raise ValueError(f"x_or_y must be 'x', 'y', or None, got {x_or_y}.")
    elif not isinstance(var, str):
        raise TypeError(f'var must be a string, got {type(var)}.')
    else:
        # Verify the variable is in the dataset
        if var not in data_for_year.data_vars:
            raise ValueError(f"Variable '{var}' not found in dataset. Available variables: {list(data_for_year.data_vars)}")
        # Drop all nan values
        data_for_year = data_for_year[var].dropna(dim='time', how='all')
        # Convert to numpy array
        data_array = data_for_year.to_numpy()
    return data_array