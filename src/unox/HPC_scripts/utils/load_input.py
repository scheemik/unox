import numpy as np
import xarray as xr
import os
import json

def get_npy_from_netcdf(
    netcdf,
    year,
    input_config,
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
    input_config : str or dict
        Path to the input configuration JSON file or a dictionary containing the configuration.
    x_or_y : str, optional
        If 'x', return the stage 1 x variables, if 'x2', return the stage 2 x variables, 
        if 'y', return the y variables. If None, return all variables.
    var : str, optional
        The variable to extract from the netcdf file. Overrides the `x_or_y` argument. 
        If None, all variables are returned.
    use_lsm : bool, optional
        Whether to use land-sea mask when extracting data. Default is False.

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
    # Verify the input config
    if isinstance(input_config, type({})):
        config_dict = input_config
    elif isinstance(input_config, str):
        # Verify the input config file path
        input_config_path = input_config
        if not os.path.isfile(input_config_path):
            input_config_path = f"inputfiles/_input_configs/{input_config}.json"
        # Load config file to a dictionary
        with open(input_config_path, 'r') as file:
            config_dict = json.load(file)
    else:
        raise TypeError(f'input_config must be a str or dict, got {type(input_config)}.')
    # Select the data for the specified year
    data_for_year = xr_dataset.sel(time=slice(f'{year}-01-01', f'{year}-12-31'))
    if isinstance(var, type(None)):
        if x_or_y in ['x', 'x2']:
            # Get the list of x variables from the `x_vars` attribute
            x_vars = xr_dataset.attrs.get('x_vars')
            if x_or_y == 'x':
                x_vars = xr_dataset.attrs.get('x1_vars')
            elif x_or_y == 'x2':
                # Get the stage 2 cutoff
                stage_2_cutoff = xr_dataset.attrs.get('stage_2_cutoff')
                if stage_2_cutoff > year:
                    raise ValueError(f"Stage 2 data not available for year {year} (cutoff is {stage_2_cutoff}).")
                x_vars = xr_dataset.attrs.get('x2_vars')
            # Grab just the x variables for the dataset
            # data_for_year = data_for_year[x_vars]
            # Drop all nan values
            data_for_year = data_for_year.dropna(dim='time', how='all')
            # Convert the entire dataset to a numpy array by looping over x_vars
            list_of_x_arrs = []
            for i in range(len(x_vars)):
                this_var = x_vars[i]
                # Skip the land-sea mask if applicable
                if this_var == 'lsm':
                    continue
                # Get the numpy array for this variable
                this_arr = get_npy_from_netcdf(data_for_year, year, config_dict, var=this_var)
                list_of_x_arrs.append(this_arr)
                # print(f'\tLoaded {this_var} for year {year} with shape {this_arr.shape}')
            # Stack the arrays together along a new axis in last place
            data_array = np.stack(tuple(list_of_x_arrs), axis=-1)
        elif x_or_y == 'y':
            # Get the y variable from the `y_var` attribute
            y_var = xr_dataset.attrs.get('y_var')
            if y_var is None:
                raise ValueError("The dataset does not have a 'y_var' attribute.")
            return get_npy_from_netcdf(data_for_year, year, config_dict, var=y_var)
        else:
            raise ValueError(f"x_or_y must be 'x', 'y', or None, got {x_or_y}.")
    elif not isinstance(var, str):
        raise TypeError(f'var must be a string, got {type(var)}.')
    else:
        # Verify the variable is in the dataset
        # udata.verify_var(data_for_year, var)
        if var not in data_for_year.data_vars:
            raise ValueError(f"Variable '{var}' not found in dataset. Available variables: {list(data_for_year.data_vars)}")
        # Apply a mask to the variable, if applicable
        data_for_year[var] = apply_mask(data_for_year, var, config_dict)
        # # Get the land-sea mask variables from the configuration, if they exist
        # if 'lsm_vars' in config_dict:
        #     lsm_vars = config_dict['lsm_vars']
        #     use_lsm = True
        # else:
        #     print(f"\tNo 'lsm_vars' found in input config: {input_config}")
        #     use_lsm = False
        # # Check whether to apply the land-sea mask
        # if use_lsm and var in lsm_vars:
        #     # Verify the land-sea mask exists
        #     # udata.verify_var(data_for_year, 'lsm')
        #     if 'lsm' not in data_for_year.data_vars:
        #         raise ValueError(f"Variable 'lsm' not found in dataset. Available variables: {list(data_for_year.data_vars)}")
        #     # Apply the land-sea mask
        #     print(f'\tApplying land-sea mask to {var} for year {year}')
        #     data_for_year[var] = data_for_year[var]*data_for_year['lsm']
        #     # lsm_threshold = 1
        #     # data_for_year[var] = data_for_year[var].where(data_for_year['lsm'] >= lsm_threshold)
        # Drop all nan values
        data_for_year = data_for_year[var].dropna(dim='time', how='all')
        # Convert to numpy array
        data_array = data_for_year.to_numpy()
    return data_array

def apply_mask(
    xr_dataset,
    var,
    config_dict,
):
    """Apply specified mask to the given variable.

    Determine the mask to apply based on the configuration dictionary
    and apply it to the specified variable in the xarray dataset.

    Parameters
    ----------
    xr_dataset : xr.Dataset
        The xarray dataset containing the variable to be masked.
    var : str
        The variable to which the mask will be applied.
    config_dict : dict
        Configuration dictionary specifying mask details.

    Returns
    -------
    xr.DataArray
        The masked variable as an xarray DataArray.
    """
    # Verify argument types
    if not isinstance(xr_dataset, xr.Dataset):
        raise TypeError(f'xr_dataset must be an xarray.Dataset, got {type(xr_dataset)}.')
    # udata.verify_dataset(xr_dataset)
    if not isinstance(var, str):
        raise TypeError(f'var must be a string, got {type(var)}.')
    # udata.verify_var(xr_dataset, var)
    if not isinstance(config_dict, dict):
        raise TypeError(f'config_dict must be a dict, got {type(config_dict)}.')
    # Determine whether a mask should be applied
    use_mask = False
    if 'lsm_vars' in config_dict:
        lsm_vars = config_dict['lsm_vars']
        if var in lsm_vars:
            use_mask = 'lsm'
    if 'zfi_vars' in config_dict:
        zfi_vars = config_dict['zfi_vars']
        if use_mask == True:
            raise ValueError(f"Cannot apply both land-sea mask and zero-fill mask to the same variable, {var}.")
        elif var in zfi_vars:
            use_mask = 'zfi'
    # If no mask is to be applied, return the original variable
    if use_mask == False:
        return xr_dataset[var]
    # If applying the land-sea mask
    elif use_mask == 'lsm':
        # Verify the land-sea mask exists
        # udata.verify_var(xr_dataset, 'lsm')
        if 'lsm' not in xr_dataset.data_vars:
            raise ValueError(f"Variable 'lsm' not found in dataset. Available variables: {list(xr_dataset.data_vars)}")
        # Apply the land-sea mask
        print(f'\tApplying land-sea mask to {var}')
        return xr_dataset[var]*xr_dataset['lsm']
        # lsm_threshold = 1
        # return xr_dataset[var].where(xr_dataset['lsm'] >= lsm_threshold)
    # If zeroing the variable for ZFI (Zeroed Feature Importance)
    elif use_mask == 'zfi':
        print(f'\tZeroing out {var}')
        return xr_dataset[var]*0
    else:
        raise ValueError(f'Unexpected value for use_mask: {use_mask}.')