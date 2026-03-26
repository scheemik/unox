import numpy as np
import xarray as xr
import os
import json

# Necessary to use relative imports (starting with a dot) to avoid
# errors when running on HPC as the `unox` package is not available
from .paths import verify_path
from .dataset import get_years
from .verify_dataset import verify_dataset
from .verify_dtype import verify_number
from .config import get_config

def get_npy_from_netcdf(
    netcdf,
    year,
    model_config,
    x_or_y=None,
    var=None,
):
    """ Extract a numpy array for a specific year (and variable if requested) from a netcdf file.

        Parameters
        ----------
        netcdf : `str` or `xr.Dataset`
            Path to the netcdf file or an xarray Dataset.
        year : `int`
            The year for which to extract the data.
        model_config : `str` or `dict`
            Path to the input configuration JSON file or a dictionary containing the configuration.
        x_or_y : `str`, optional
            If 'x', return the stage 1 x variables, if 'x2', return the stage 2 x variables,
            if 'y', return the y variables. If None, return all variables.
        var : `str`, optional
            The variable to extract from the netcdf file. Overrides the `x_or_y` argument.
            If None, all variables are returned.

        Returns
        -------
        data_array : `numpy.ndarray`
            The extracted data as a numpy array.
        lats : `numpy.ndarray`
            The latitude values of the arrays to restrict.
        lons : `numpy.ndarray`
            The longitude values of the arrays to restrict.

        Examples
        --------
        >>> input_set = 'my_inputs'
        >>> arr, lats, lons = get_npy_from_netcdf(f'inputfiles/{input_set}/{input_set}.nc', 2019, 'x')
        >>> type(arr)
        <class 'numpy.ndarray'>
        >>> arr.shape
        (364, 56, 120, 9)
    """
    # Verify argument types
    if isinstance(netcdf, str):
        # Verify the netcdf file path
        netcdf_filepath = verify_path(netcdf)
        # Load the netcdf file
        xr_dataset = xr.load_dataset(netcdf)
    elif isinstance(netcdf, xr.Dataset):
        xr_dataset = netcdf
    else:
        raise TypeError(f"(get_npy_from_netcdf) `netcdf` must be a file path (str) or an xarray.Dataset. Got type: {type(netcdf)}")
    # Verify the dataset
    xr_dataset = verify_dataset(xr_dataset)
    # Verify the year
    if not verify_number(year):
        raise TypeError(f"(get_npy_from_netcdf) `year` must be a number. Got type: {type(year)}")
    # Verify year is present in the dataset
    ds_years = get_years(xr_dataset)
    if year not in ds_years:
        raise ValueError(f"(get_npy_from_netcdf) `year` must be a year present in `netcdf`. Available years: {ds_years}")
    # Verify the input config
    if isinstance(model_config, type({})):
        config_dict = model_config
    elif isinstance(model_config, str):
        # Get the input config from file
        ## Note: `get_config` checks whether the file exists
        config_dict = get_config(model_config)
    else:
        raise TypeError(f"(get_npy_from_netcdf) `model_config` must be a str or dict. Got type: {type(model_config)}")
    # Verify `x_or_y` and `var`
    if isinstance(x_or_y, type(None)) and isinstance(var, type(None)):
        raise ValueError(f"(get_npy_from_netcdf) Cannot have both `x_or_y` and `var` have a values of `None`.")
    elif isinstance(x_or_y, type(None)):
        if not isinstance(x_or_y, str):
            TypeError(f"(get_npy_from_netcdf) `x_or_y` must be a str. Got type: {type(x_or_y)}")
    elif isinstance(var, type(None)):
        if not isinstance(var, str):
            TypeError(f"(get_npy_from_netcdf) `var` must be a str. Got type: {type(var)}")

    # Apply the input configuration file
    xr_dataset = apply_config(xr_dataset, config_dict)
    # Select the data for the specified year
    data_for_year = xr_dataset.sel(time=slice(f'{year}-01-01', f'{year}-12-31'))
    # Check whether any data remains
    if data_for_year.sizes['time'] == 0:
        raise ValueError(f"(get_npy_from_netcdf) No data available for year {year} in the dataset.")
    if isinstance(var, type(None)):
        if x_or_y in ['x', 'x2']:
            # Get the list of x variables from the `x_vars` attribute
            if x_or_y == 'x':
                x_vars = xr_dataset.attrs.get('x1_vars')
            elif x_or_y == 'x2':
                # Get the stage 2 cutoff
                stage_2_cutoff = xr_dataset.attrs.get('stage_2_cutoff')
                if stage_2_cutoff > year:
                    raise ValueError(f"(get_npy_from_netcdf) Stage 2 data not available for year {year} (cutoff is {stage_2_cutoff}).")
                x_vars = xr_dataset.attrs.get('x2_vars')
            # Grab just the x variables for the dataset
            data_for_year = data_for_year[x_vars]
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
                this_arr, in_lats, in_lons = get_npy_from_netcdf(data_for_year, year, config_dict, var=this_var)
                list_of_x_arrs.append(this_arr)
                # print(f'\tLoaded {this_var} for year {year} with shape {this_arr.shape}')
            # Stack the arrays together along a new axis in last place
            data_array = np.stack(tuple(list_of_x_arrs), axis=-1)
        elif x_or_y == 'y':
            # Get the y variable from the `y_var` attribute
            y_var = xr_dataset.attrs.get('y_var')
            if y_var is None:
                raise ValueError("(get_npy_from_netcdf) The dataset does not have a 'y_var' attribute.")
            return get_npy_from_netcdf(data_for_year, year, config_dict, var=y_var)
        else:
            raise ValueError(f"(get_npy_from_netcdf) `x_or_y` must be 'x', 'y', or None. Got: {x_or_y}")
    elif not isinstance(var, str):
        raise TypeError(f"(get_npy_from_netcdf) `var` must be a string. Got type: {type(var)}")
    else:
        # Verify the variable is in the dataset
        # udata.verify_var(data_for_year, var)
        if var not in data_for_year.data_vars:
            raise ValueError(f"(get_npy_from_netcdf) Variable '{var}' not found in dataset. Available variables: {list(data_for_year.data_vars)}")
        # Apply a mask to the variable, if applicable
        data_for_year[var] = apply_mask(data_for_year, var, config_dict, year)
        # Drop all nan values
        data_for_year = data_for_year[var].dropna(dim='time', how='all')
        # Convert to numpy array
        data_array = data_for_year.to_numpy()
    return data_array, data_for_year['lat'].values, data_for_year['lon'].values

def apply_config(
    input_netcdf,
    model_config,
):
    """ Apply the conditions in the config to the netcdf.

        Based on the parameters in the input configuration, modify the xarray in the input netcdf and return the resulting xarray dataset.

        Parameters
        ----------
        input_netcdf : `str` or `xr.Dataset`
            Path to the netcdf file or an xarray Dataset.
        model_config : `str` or `dict`
            Path to the input configuration JSON file or a dictionary containing the configuration.

        Returns
        -------
        prepped_dataset : `xr.Dataset`
            The dataset from the input netcdf with the configuration rules applied.
    """
    # Verify argument types
    if isinstance(input_netcdf, str):
        # Verify the netcdf file path
        netcdf_filepath = verify_path(input_netcdf)
        # Load the netcdf file
        xr_dataset = xr.load_dataset(input_netcdf)
    elif isinstance(input_netcdf, xr.Dataset):
        xr_dataset = input_netcdf
    else:
        raise TypeError(f"(apply_config) `input_netcdf` must be a file path (str) or an xarray.Dataset. Got type: {type(netcdf)}")
    # Verify the dataset
    xr_dataset = verify_dataset(xr_dataset)
    # Verify the input config
    if isinstance(model_config, type({})):
        config_dict = model_config
    elif isinstance(model_config, str):
        # Verify the input config file path
        model_config_path = model_config
        if not os.path.isfile(model_config_path):
            model_config_path = f"inputfiles/_model_configs/{model_config}.json"
        # Load config file to a dictionary
        with open(model_config_path, 'r') as file:
            config_dict = json.load(file)
    else:
        raise TypeError(f"(apply_config) `model_config` must be a str or dict. Got type: {type(model_config)}")

    # Trim the lat-lon extent of the dataset, if applicable
    if 'grid_size' in config_dict:
        # Find the grid size
        grid_size = config_dict['grid_size']
        # print('grid_size:', grid_size)
        # Assumes there are two numbers: number of latitude cells, number of longitude cells
        if not len(grid_size) == 2:
            raise ValueError(f"(apply_config) Expected `grid_size` to have a length of 2. Got length of {len(grid_size)}: {grid_size}")
        else:
            n_lats = grid_size[0]
            n_lons = grid_size[1]
        # Get the length of the latitude and longitude dimensions in the dataset
        xr_n_lats = xr_dataset.sizes['lat']
        xr_n_lons = xr_dataset.sizes['lon']
        # Ensure that the desired grid size is not larger than the available grid
        if n_lats > xr_n_lats:
            raise ValueError(f"(apply_config) Requested length of latitude grid ({n_lats}) cannot exceed length of latitude dimension in the given netcdf ({xr_n_lats}).")
        if n_lons > xr_n_lons:
            raise ValueError(f"(apply_config) Requested length of longitude grid ({n_lons}) cannot exceed length of longitude dimension in the given netcdf ({xr_n_lons}).")
        # If the given xarray Dataset is already the specified size, return it immediately
        if n_lats == xr_n_lats and n_lons == xr_n_lons:
            return xr_dataset
        ## Find indices to use when restricting available grid to desired size
        # Get lat-lon extent of the xarray dataset
        # xr_extent = udata.get_extent(xr_dataset)
        lat_min = np.unique(xr_dataset.lat.min().values)[0]
        lat_max = np.unique(xr_dataset.lat.max().values)[0]
        lon_min = np.unique(xr_dataset.lon.min())[0]
        lon_max = np.unique(xr_dataset.lon.max())[0]
        xr_extent = (lat_min, lat_max, lon_min, lon_max)
        # Find the centre coordinate based on that extent
        xr_centre = (
            (xr_extent[1]-xr_extent[0])/2+xr_extent[0], 
            (xr_extent[3]-xr_extent[2])/2+xr_extent[2]
        )
        # Get the latitude and longitude values from the xarray Dataset
        lats = xr_dataset['lat'].values
        lons = xr_dataset['lon'].values
        # Find the indices of lats and lons closest to the centre
        c_idx_lat = (np.abs(lats-xr_centre[0])).argmin()
        c_idx_lon = (np.abs(lons-xr_centre[1])).argmin()
        # Calculate the start and stop indices of the trimmed grid for lat
        min_idx_lat = int(c_idx_lat - np.floor(n_lats/2))
        max_idx_lat = int(c_idx_lat + np.ceil(n_lats/2))
        lats_tr = lats[min_idx_lat:max_idx_lat]
        # Calculate the start and stop indices of the trimmed grid for lon
        min_idx_lon = int(c_idx_lon - np.floor(n_lons/2))
        max_idx_lon = int(c_idx_lon + np.ceil(n_lons/2))
        lons_tr = lons[min_idx_lon:max_idx_lon]
        # Trim the xarray Dataset to the specified grid size
        xr_dataset = xr_dataset.isel(
            lat = slice(min_idx_lat, max_idx_lat),
            lon = slice(min_idx_lon, max_idx_lon),
            drop=True,
        )
    return xr_dataset

def apply_mask(
    xr_dataset,
    var,
    config_dict,
    year,
):
    """ Apply specified mask to the given variable.

        Determine the mask to apply based on the configuration dictionary and apply it to the specified variable in the xarray dataset.

        Parameters
        ----------
        xr_dataset : `xr.Dataset`
            The xarray dataset containing the variable to be masked.
        var : `str`
            The variable to which the mask will be applied.
        config_dict : `dict`
            Configuration dictionary specifying mask details.
        year : `int`
            The year for which the data is being processed.

        Returns
        -------
        xr.DataArray
            The masked variable as an xarray DataArray.
    """
    # Verify argument types
    if not isinstance(xr_dataset, xr.Dataset):
        raise TypeError(f"(apply_mask) `xr_dataset` must be an xarray.Dataset. Got type: {type(xr_dataset)}")
    xr_dataset = verify_dataset(xr_dataset)
    if not isinstance(var, str):
        raise TypeError(f"(apply_mask) `var` must be a string. Got type: {type(var)}")
    # udata.verify_var(xr_dataset, var)
    if not isinstance(config_dict, dict):
        raise TypeError(f"(apply_mask) `config_dict` must be a dict. Got type: {type(config_dict)}")
    # Determine whether a mask should be applied
    use_mask = False
    if 'lsm_vars' in config_dict:
        lsm_vars = config_dict['lsm_vars']
        if var in lsm_vars:
            use_mask = 'lsm'
    if 'zfi_vars' in config_dict:
        zfi_vars = config_dict['zfi_vars']
        if use_mask == True:
            raise ValueError(f"(apply_mask) Cannot apply both land-sea mask and zero-fill mask to the same variable, {var}.")
        elif var in zfi_vars:
            use_mask = 'zfi'
        elif zfi_vars == ['none']:
            use_mask = False
            print(f"\t{year}: Not zeroing out {var}")
    # If no mask is to be applied, return the original variable
    if use_mask == False:
        return xr_dataset[var]
    # If applying the land-sea mask
    elif use_mask == 'lsm':
        # Verify the land-sea mask exists
        # udata.verify_var(xr_dataset, 'lsm')
        if 'lsm' not in xr_dataset.data_vars:
            raise ValueError(f"(apply_mask) Variable 'lsm' not found in dataset. Available variables: {list(xr_dataset.data_vars)}")
        # Apply the land-sea mask
        print(f'\t{year}: Applying land-sea mask to {var}')
        return xr_dataset[var]*xr_dataset['lsm']
        # lsm_threshold = 1
        # return xr_dataset[var].where(xr_dataset['lsm'] >= lsm_threshold)
    # If zeroing the variable for ZFI (Zeroed Feature Importance)
    elif use_mask == 'zfi':
        print(f'\t{year}: Zeroing out {var}')
        return xr_dataset[var]*0
    else:
        raise ValueError(f"(apply_mask) Unexpected value for `use_mask`: {use_mask}")